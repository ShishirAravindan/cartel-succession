#!/usr/bin/env python3
"""End-to-end learning story checks through the local browser session."""
from pathlib import Path
import subprocess
CODE=r'''async page=>{
 const assert=(x,m)=>{if(!x)throw Error(m);},errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:8765/viz/index.html');
 await page.waitForFunction(()=>Explorer.parity?.ok);
 await page.waitForFunction(()=>document.getElementById('evidence-check').textContent.includes('cross-check passed'));
 for(let i=0;i<8;i++){await page.locator(`[data-scene="${i}"]`).click();if(i<7)await page.locator('#coffee-play').click();}
 await page.locator('#glossary-open').click();assert(await page.locator('.glossary-entry').count()===19,'collected glossary');await page.locator('#glossary-close').click();
 await page.locator('[data-scene="1"]').click();assert((await page.locator('#coffee-cups').textContent()).includes('1.473'),'price war reaches competitive benchmark');
 for(const arm of ['control','same_history','lookalike','same_none','same_full']){
  await page.locator('[data-act="3"]').click();await page.locator('#path-arm-buttons button').filter({hasText:new RegExp(`^${arm}$`)}).click();
  if(arm==='same_full'){assert(await page.locator('#prompt-notes').isVisible(),'real notes visible');assert((await page.locator('#prompt-notes-text').textContent()).includes('149 consecutive'),'actual excerpt');}
  if(arm==='same_none')assert(await page.locator('#prompt-empty').isVisible(),'empty history shown');
  await page.locator('#path-run').click();assert((await page.locator('#path-verdict').textContent()).includes('joins = true'),'plain join verdict');
  await page.locator('#path-continue').click();assert(await page.locator('#path-chart path').count()>=3,'enforcer overlay');
  await page.locator('#path-run').click();await page.locator('#path-continue').click();await page.locator('#path-cut').click();
  assert(await page.locator('[name=probe-response]:checked').count()===0,'probe has no default');await page.locator('#path-run').click();assert((await page.locator('#path-choice-error').textContent()).includes('no default'),'probe requires explicit choice');
  await page.locator('[name=probe-response][value="1.92"]').check();await page.locator('#path-run').click();
  assert((await page.locator('#path-counterfactual').textContent()).includes('T+17…29'),'counterfactual same window');
  if(arm==='lookalike')assert((await page.locator('#path-verdict').textContent()).includes('probe_punished = false'),'lookalike never punishes');
  await page.locator('#path-continue').click();assert(await page.locator('#act-4').isVisible(),'play then evidence');
  assert(await page.locator('#evidence-chart path').count()===30,'15 newcomer + 15 incumbent paths');
  await page.locator('#evidence-probe').click();await page.locator('#evidence-seed').selectOption('200');assert((await page.locator('#evidence-chart').textContent()).includes('probe_return'),'seed windows');await page.locator('#evidence-seed').selectOption('all');await page.locator('#evidence-main').click();
 }
 assert((await page.locator('#paths-explored').textContent()).includes('5 paths'),'running comparison');assert(await page.locator('#path-comparison tr').count()===5,'comparison rows');
 await page.locator('[data-act="3"]').click();await page.locator('#path-history').uncheck();await page.locator('#path-notes').check();assert((await page.locator('#path-toggle-status').textContent()).includes('running now'),'notes-only pending');
 await page.locator('#path-arm-buttons button').filter({hasText:/^same_history$/}).click();assert(!(await page.locator('#path-run').isDisabled()),'completed arm restores play');
 await page.locator('[data-act="5"]').click();assert(await page.locator('#act-5 .pending-result').count()===7,'all result interpretations marked');for(const text of await page.locator('#act-5 .pending-result').allTextContents())assert(text.includes('[pending morning results]'),'pending result marker');await page.locator('#coda-coffee').click();assert(await page.locator('#act-1').isVisible(),'coffee-shop close loop');
 await page.locator('[data-act="2"]').click();assert(await page.locator('#act-2 .timeline-card').count()===5,'five timeline cards');assert(await page.locator('#act-2 a[href^="https:"]').count()===6,'six confirmed primary source links');assert((await page.locator('#act-2 .unconfirmed').textContent()).includes('[source to add]'),'unconfirmed incident remains placeholder');await page.locator('#timeline-to-paths').click();assert(await page.locator('#act-3').isVisible(),'timeline bridges to experiment');
 await page.locator('#skip-results').click();assert(await page.locator('#act-4').isVisible(),'skip to results');await page.locator('#evidence-arm-select').selectOption('same_history');assert((await page.locator('#evidence-caption').textContent()).includes('13 of 15'),'arm selection in evidence');await page.locator('#story-csv').setInputFiles('.playwright-cli/committed-p1.csv');await page.waitForFunction(()=>document.getElementById('evidence-check').textContent.includes('manual CSV'));
 // Ephemeral aliases test future-data plumbing, not actual sibling/other-model results.
 await page.evaluate(()=>{const payload=JSON.parse(document.getElementById('p1-data').textContent),groups=Explorer.adaptP1CSV(payload.csv);for(const[arm,seed]of [['sib_history','215'],['oth_full','216']]){const g=structuredClone(groups.get('200|same_history'));g.arm=arm;g.seed=seed;groups.set(`${seed}|${arm}`,g);}installEvidence(groups,payload.report,'synthetic verification aliases',false);});
 assert(await page.locator('#replacement-ladder').isVisible(),'future data enables replacement ladder');assert((await page.locator('#evidence-check').textContent()).includes('2 additional paths have no report entry'),'extra paths remain explicitly unverified');await page.locator('#evidence-arm-select').selectOption('sib_history');assert(await page.locator('#evidence-seed option[value="215"]').count()===1,'extra seeds accepted');assert(!(await page.locator('#pending-arms button').filter({hasText:/^sib_history$/}).isDisabled()),'new arm enables from data');
 await page.reload();await page.waitForFunction(()=>document.getElementById('evidence-check').textContent.includes('cross-check passed'));
 const ref=await page.evaluate(()=>JSON.parse(document.getElementById('p1-data').textContent).report);ref.rows[0].joins=!ref.rows[0].joins;
 await page.route('**/seat_swap/results/p1.json',route=>route.fulfill({contentType:'application/json',body:JSON.stringify(ref)}));await page.reload();await page.waitForFunction(()=>document.getElementById('evidence-check').classList.contains('fail'));assert((await page.locator('#evidence-check').textContent()).includes('mismatch'),'red count mismatch banner');await page.unroute('**/seat_swap/results/p1.json');await page.reload();await page.waitForFunction(()=>document.getElementById('evidence-check').textContent.includes('cross-check passed'));
 await page.setViewportSize({width:390,height:844});for(const act of ['1','2','3','4','5']){await page.locator(`[data-act="${act}"]`).click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`act ${act} mobile overflow`);}
 await page.goto('http://127.0.0.1:8765/viz/index.html#act-2');assert(await page.locator('#act-2').isVisible(),'chapter deep link');assert(await page.locator('#act-progress-value').getAttribute('value')==='2','progress reflects chapter');
 assert(errors.length===0,errors.join('; '));return 'All story milestones passed: scenes, glossary, all five path loops, auto-load, strict adapter, report mismatch, seed drill-down, comparison and mobile.';
}'''
if __name__=='__main__':
 root=Path(__file__).resolve().parent
 temporary=root/'.playwright-cli'
 temporary.mkdir(exist_ok=True)
 (temporary/'committed-p1.csv').write_bytes((root.parent/'seat_swap/results/p1_prices.csv').read_bytes())
 r=subprocess.run(['playwright-cli','-s=cartel-viz','run-code',CODE],cwd=Path(__file__).resolve().parent,capture_output=True,text=True)
 print(r.stdout);print(r.stderr)
 raise SystemExit(r.returncode or (1 if '### Error' in r.stdout else 0))
