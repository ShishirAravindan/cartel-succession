#!/usr/bin/env python3
"""Verify the guided UI in the existing local playwright-cli cartel-viz session."""
from pathlib import Path
import subprocess

CODE = r'''async page => {
  const assert=(condition,message)=>{if(!condition)throw Error(message);};
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('http://127.0.0.1:8765/viz/index.html#practice');
  await page.waitForFunction(()=>window.Explorer?.parity?.ok);
  await page.setViewportSize({width:1440,height:1100});
  assert(await page.locator('#guided').isVisible(),'guide opens by default');
  assert(!(await page.locator('#sandbox').isVisible()),'sandbox hidden initially');
  // Sandbox remains a separate working state when the guide is used.
  await page.locator('#guide-lesson .skip-guide').click();
  await page.locator('#preset').selectOption('copier');await page.locator('#next').click();
  const sandboxBefore=await page.locator('#progress').textContent();
  await page.locator('#mode-guide').click();
  await page.locator('#guide-price').fill('');await page.locator('#guide-run').click();
  assert(!(await page.locator('#guide-verdict').isVisible()),'empty price cannot finish a lesson');
  await page.locator('#guide-price').fill('2.90');await page.locator('#guide-run').click();
  assert(!(await page.locator('#guide-verdict').isVisible()),'out-of-range price cannot finish a lesson');
  const canonical=[['joins = true'],['probe_punished = true','disciplined = true'],['enforces = false'],['probe_punished = false','disciplined = false'],['overpriced = true']];
  const titles=['Join','Get caught','The shock','Nobody’s watching','Too greedy'];
  async function lesson(index,price,expected) {
    assert(await page.locator('#guide-title').textContent()===titles[index],`step ${index+1} title`);
    assert(await page.locator('#guide-position').textContent()===`Step ${index+1} of 5`,'step position');
    // Skip exists on every step and restores the same unfinished lesson.
    await page.locator('#guide-lesson .skip-guide').click();
    assert(await page.locator('#sandbox').isVisible(),'skip reaches sandbox');
    assert(await page.locator('#progress').textContent()===sandboxBefore,'guide preserves sandbox');
    await page.locator('#mode-guide').click();
    if(index===1||index===3) {
      await page.locator('#guide-run').click();
      assert((await page.locator('#guide-instruction').textContent()).includes('Now what?'),'pause after the cut');
      assert((await page.locator('#guide-instruction').textContent()).includes(index===1?'1.47':'1.92'),'reacting and lookalike incumbents differ');
      assert(!(await page.locator('#guide-verdict').isVisible()),'complete probe windows before verdict');
    }
    if(index===2)assert((await page.locator('#guide-chart').textContent()).includes('Round 180 (T+30), seat 0: price 1.4730'),'scheduled shock appears before response');
    await page.locator('#guide-price').fill(String(price));
    await page.locator('#guide-run').click();
    assert(await page.locator('#guide-verdict').isVisible(),'verdict displayed');
    const codes=await page.locator('#guide-verdict code').allTextContents();
    assert(JSON.stringify(codes)===JSON.stringify(expected),`step ${index+1}: ${JSON.stringify(codes)}`);
    assert((await page.locator('#guide-rounds').textContent()).startsWith(['10 / 10','14 / 14','11 / 11','14 / 14','10 / 10'][index]),'short complete window');
    if(index===4)assert((await page.locator('#guide-anchor').textContent()).includes('$2.89'),'anchor explanation visible');
    await page.locator('#guide-continue').click();
  }
  for(let i=0;i<5;i++)await lesson(i,i===4?2.50:1.92,canonical[i]);
  assert(await page.locator('#guide-end').isVisible(),'end screen visible');
  assert(await page.locator('#guide-summary > li').count()===5,'five verdicts in a row');
  const columns=await page.locator('#guide-summary').evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length);
  assert(columns===5,'desktop end screen has five columns');
  assert((await page.locator('#guide-summary').textContent()).includes('disciplined = true'),'summary retains prior verdict');
  assert((await page.locator('#guide-summary').textContent()).includes('enforces = false'),'summary keeps shock verdict separate');
  await page.screenshot({path:'preview-guided-end.png',fullPage:true});
  await page.locator('#guide-end .skip-guide').click();assert(await page.locator('#sandbox').isVisible(),'end skip reaches sandbox');
  await page.locator('#mode-guide').click();await page.locator('#guide-restart').click();
  const alternatives=[['joins = false'],['probe_punished = true','disciplined = false'],['enforces = true'],['probe_punished = false','disciplined = false'],['overpriced = false']];
  const prices=[1.47,1.60,1.47,1.60,1.92];
  for(let i=0;i<5;i++)await lesson(i,prices[i],alternatives[i]);
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile summary has no page overflow');
  await page.screenshot({path:'preview-guided-mobile-end.png',fullPage:true});
  await page.locator('#guide-restart').click();
  assert(await page.locator('#guide-price').inputValue()==='1.92','restart restores initial choice');
  assert(!(await page.locator('#guide-verdict').isVisible()),'restart clears verdict');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile lesson has no page overflow');
  await page.screenshot({path:'preview-guided-mobile.png',fullPage:true});
  assert(await page.locator('#guide-lesson .skip-guide').isVisible(),'mobile skip remains visible');
  await page.locator('#mode-sandbox').click();assert(await page.locator('#progress').textContent()===sandboxBefore,'restart leaves sandbox intact');
  await page.locator('#mode-guide').click();await page.setViewportSize({width:1440,height:1100});
  await page.screenshot({path:'preview-guided.png',fullPage:true});
  assert(errors.length===0,`browser errors: ${errors.join('; ')}`);
  return {passed:'Five-step guide: canonical and alternative choices, exact windows, every skip link, separate sandbox, restart, and desktop/mobile layouts.'};
}'''

if __name__ == '__main__':
    result = subprocess.run(['playwright-cli', '-s=cartel-viz', 'run-code', CODE],
                            cwd=Path(__file__).resolve().parent, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode or (1 if '### Error' in result.stdout else 0))
