#!/usr/bin/env python3
"""Exercise the local page in an already open playwright-cli cartel-viz session."""
from pathlib import Path
import subprocess
import json

CODE = r'''async page => {
  const assert=(x,message)=>{if(!x)throw Error(message);};
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.reload();
  await page.waitForFunction(()=>window.Explorer?.parity!==null);
  assert(await page.evaluate(()=>Explorer.parity.ok),'green HTTP parity');
  await page.locator('#mode-sandbox').click();
  let views=0;
  for(const arm of ['control','same_history','same_none','same_full','lookalike']){
    for(const preset of ['copier','enforcer','anchored','follower','undercutter']){
      await page.locator('#main-track').click();
      await page.locator('#arm').selectOption(arm);
      await page.locator('#preset').selectOption(preset);
      await page.locator('#finish').click();
      assert(await page.locator('#progress').textContent()==='60 / 60 rounds completed · finished',`${arm}/${preset}: main complete`);
      const mainValues=await page.locator('.metric-value').allTextContents();
      assert(!mainValues.slice(0,4).includes('Pending'),`${arm}/${preset}: main metrics`);views++;
      await page.locator('#probe-track').click();await page.locator('#finish').click();
      assert(await page.locator('#progress').textContent()==='29 / 29 rounds completed · finished',`${arm}/${preset}: probe complete`);
      assert(!(await page.locator('.metric-value').allTextContents()).includes('Pending'),`${arm}/${preset}: probe metrics`);
      assert((await page.locator('#price-chart').textContent()).includes('probe_return'), 'probe windows labelled');views++;
    }
  }
  // Probe can also be completed first, from an untouched snapshot.
  await page.locator('#reset').click();await page.locator('#finish').click();
  await page.locator('#main-track').click();
  assert((await page.locator('#progress').textContent()).startsWith('15 / 60'),'probe-first advances main only to fork');
  // Manual actions: a cut immediately following the high pre-history triggers punishment.
  await page.locator('#arm').selectOption('same_history');await page.locator('#human-mode').click();
  await page.locator('#price').fill('1.60');await page.locator('#next').click();await page.locator('#next').click();
  assert((await page.locator('#round-table tr').first().textContent()).includes('1.4700'),'incumbent punishes on the next round');
  await page.locator('#price').fill('2.20');await page.locator('#finish').click();
  assert((await page.locator('#round-table tr').first().textContent()).includes('1.6000'),'auto-hold repeats last chosen price rather than unplayed input');
  assert(await page.locator('#next').isDisabled(),'manual line finishes at 60');
  await page.locator('#preset-mode').click();
  await page.locator('#preset').selectOption('anchored');
  for(const anchor of [2.0,2.5]){
    await page.locator('#anchor').evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('input'));},String(anchor));
    await page.locator('#finish').click();
    assert((await page.locator('.metric').nth(2).textContent()).includes('Yes'),'anchor overpricing recognized');
  }
  // Upload synthetic verification prices via the actual local file input.
  const fixture=await page.evaluate(()=>JSON.parse(document.getElementById('fixture-data').textContent));
  await page.locator('#csv-file').setInputFiles('.playwright-cli/synthetic-verification.csv');
  await page.waitForFunction(()=>!document.getElementById('exit-replay').hidden);
  assert(await page.locator('#arm').isDisabled(),'replay disables simulation');
  assert((await page.locator('#chart-title').textContent()).includes('CSV replay'),'replay visible');
  const values=await page.locator('.metric-value').allTextContents();
  assert(values[0]==='Yes'&&values[1]==='Yes'&&values[3]==='Yes'&&values[6]==='Yes','replay metrics match enforcer fixture');
  await page.locator('#replay-group').selectOption('8|lookalike');
  assert((await page.locator('.metric-value').allTextContents()).every(v=>v==='Pending'),'partial CSV cannot produce outcomes');
  assert(await page.locator('#price-chart circle').count()===2,'no invented price rows in replay');
  await page.locator('#csv-file').setInputFiles('.playwright-cli/invalid.csv');
  await page.waitForFunction(()=>document.getElementById('csv-status').classList.contains('error'));
  assert((await page.locator('#chart-title').textContent()).includes('lookalike'),'invalid upload preserves existing replay');
  await page.locator('#exit-replay').click();
  // Deliberate corruption must turn the banner red, including missing fixture files.
  const bad=JSON.parse(JSON.stringify(fixture));bad.market[0].profits[0]+=.01;
  await page.route('**/fixtures.json',route=>route.fulfill({contentType:'application/json',body:JSON.stringify(bad)}));
  await page.reload();await page.waitForFunction(()=>document.getElementById('parity').classList.contains('fail'));
  await page.unroute('**/fixtures.json');
  await page.route('**/fixtures.json',route=>route.fulfill({status:404,body:'missing'}));
  await page.reload();await page.waitForFunction(()=>document.getElementById('parity').classList.contains('fail'));
  await page.unroute('**/fixtures.json');await page.reload();await page.waitForFunction(()=>window.Explorer?.parity?.ok);await page.locator('#mode-sandbox').click();
  // Desktop and mobile visual/overflow checks.
  await page.setViewportSize({width:1440,height:1100});await page.locator('#finish').click();
  await page.screenshot({path:'preview-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'mobile page has no global horizontal overflow');
  await page.locator('#probe-track').click();await page.locator('#finish').click();
  await page.screenshot({path:'preview-mobile.png',fullPage:true});
  assert(errors.length===0,`browser errors: ${errors.join('; ')}`);
  console.log(`Passed: ${views} preset/arm/track views, probe-first isolation, manual play, anchors, CSV upload, parity failure/recovery, desktop and mobile layout.`);
}'''

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    fixture = json.loads((root/'fixtures.json').read_text())
    game = next(g for g in fixture['games'] if g['preset'] == 'enforcer')
    rows = ['seed,arm,round,p0,p1']
    for track, suffix in [('main', ''), ('probe', ':discipline')]:
        rows += [f"7,{game['arm']}{suffix},{r['round']},{r['prices'][0]},{r['prices'][1]}"
                 for r in game[track] if track == 'main' or r['round'] > 165]
    rows += ['8,lookalike,151,1.92,2.2']
    temporary = root/'.playwright-cli'
    temporary.mkdir(exist_ok=True)
    (temporary/'synthetic-verification.csv').write_text('\n'.join(rows))
    (temporary/'invalid.csv').write_text('seed,arm,round,p0,p1\n7,control,151,,1.92')
    # Pass exact JS as one argument, with no shell interpolation. CLI artifacts stay in viz/.
    result = subprocess.run(['playwright-cli', '-s=cartel-viz', 'run-code', CODE],
                            cwd=Path(__file__).resolve().parent, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    raise SystemExit(result.returncode or (1 if '### Error' in result.stdout else 0))
