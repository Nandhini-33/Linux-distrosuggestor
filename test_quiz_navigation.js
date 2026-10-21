const { spawn } = require('child_process');
const http = require('http');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9224;

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  console.log('1. Launching Headless Chrome on port', PORT);
  const chrome = spawn(CHROME_PATH, [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    '--disable-gpu',
    '--no-sandbox',
    'about:blank'
  ]);

  try {
    // Wait for CDP
    let tabs = null;
    for (let i = 0; i < 25; i++) {
      await sleep(250);
      try {
        tabs = await new Promise((resolve, reject) => {
          http.get(`http://127.0.0.1:${PORT}/json/list`, res => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
          }).on('error', reject);
        });
        if (tabs && tabs.length > 0) break;
      } catch (e) {}
    }

    if (!tabs || tabs.length === 0) {
      throw new Error('Could not connect to Chrome CDP');
    }

    const pageTab = tabs.find(t => t.type === 'page') || tabs[0];
    const wsUrl = pageTab.webSocketDebuggerUrl;
    console.log('2. Connected to tab WebSocket:', wsUrl, 'URL:', pageTab.url);

    const ws = new WebSocket(wsUrl);
    let msgId = 1;
    const callbacks = new Map();

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.id && callbacks.has(data.id)) {
        const { resolve, reject } = callbacks.get(data.id);
        callbacks.delete(data.id);
        if (data.error) reject(data.error);
        else resolve(data.result);
      }
    };

    await new Promise(r => ws.onopen = r);

    function sendCmd(method, params = {}) {
      const id = msgId++;
      return new Promise((resolve, reject) => {
        callbacks.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    }

    async function evaluate(expr) {
      const res = await sendCmd('Runtime.evaluate', {
        expression: expr,
        returnByValue: true,
        awaitPromise: true
      });
      return res?.result?.value;
    }

    await sendCmd('Page.enable');
    await sendCmd('Runtime.enable');

    console.log('3. Navigating to http://127.0.0.1:5000/ ...');
    await sendCmd('Page.navigate', { url: 'http://127.0.0.1:5000/' });
    await sleep(2000);
    const href = await evaluate("window.location.href");
    console.log('Current URL in browser:', href);
    const title = await evaluate("document.title");
    console.log('Current Document Title:', title);

    // Test questions 1 to 7
    for (let step = 1; step <= 7; step++) {
      console.log(`\n--- Testing Question ${step} of 7 ---`);
      
      // Verify current step is active
      const currentActive = await evaluate(`document.querySelector('.wizard-step.active')?.dataset.step`);
      console.log(`Current active step in DOM: ${currentActive}`);
      if (parseInt(currentActive) !== step) {
        throw new Error(`Expected step ${step} to be active, got ${currentActive}`);
      }

      // Verify Next/Submit button is disabled initially before selection
      const isNextDisabled = await evaluate(`(() => {
        const btn = document.getElementById('nextStepBtn');
        const sBtn = document.getElementById('submitQuizBtn');
        return (btn && btn.disabled) || (sBtn && sBtn.disabled);
      })()`);
      console.log(`Next/Submit button initially disabled: ${isNextDisabled}`);

      // Click the first option card on this step
      console.log(`Clicking option card on step ${step}...`);
      await evaluate(`(() => {
        const stepEl = document.getElementById('step-${step}');
        const card = stepEl.querySelector('.option-card');
        if (card) card.click();
      })()`);

      // Verify option is highlighted
      const isSelected = await evaluate(`(() => {
        const stepEl = document.getElementById('step-${step}');
        const card = stepEl.querySelector('.option-card');
        return card ? card.classList.contains('selected') : false;
      })()`);
      console.log(`Option card highlighted (has .selected class): ${isSelected}`);

      // Verify Next button is now enabled
      const isNextEnabled = await evaluate(`(() => {
        const btn = document.getElementById('nextStepBtn');
        const sBtn = document.getElementById('submitQuizBtn');
        return ${step} === 7 ? !sBtn.disabled : !btn.disabled;
      })()`);
      console.log(`Next/Submit button now enabled: ${isNextEnabled}`);

      // WAIT 800ms: Verify NO automatic advance happened!
      console.log('Waiting 800ms to verify NO automatic advance occurs...');
      await sleep(800);
      const stillActive = await evaluate(`document.querySelector('.wizard-step.active')?.dataset.step`);
      console.log(`Step after 800ms delay: ${stillActive}`);
      if (parseInt(stillActive) !== step) {
        throw new Error(`BUG! Automatically advanced from step ${step} to ${stillActive} without pressing Next!`);
      }
      console.log(`✓ Confirmed: Selecting option did NOT auto-advance (stayed on Step ${step})`);

      // Now click Next button (or Submit for step 7)
      if (step < 7) {
        console.log(`Clicking Next button to move to Question ${step + 1}...`);
        await evaluate(`document.getElementById('nextStepBtn').click()`);
        await sleep(300);
        const nextStep = await evaluate(`document.querySelector('.wizard-step.active')?.dataset.step`);
        console.log(`Step after clicking Next: ${nextStep}`);
        if (parseInt(nextStep) !== step + 1) {
          throw new Error(`Expected step ${step + 1} after pressing Next, got ${nextStep}`);
        }
        console.log(`✓ Successfully moved from Step ${step} to Step ${step + 1} with Next button`);
      } else {
        console.log(`Step 7 reached! Clicking Submit button to get recommendation...`);
        await evaluate(`document.getElementById('submitQuizBtn').click()`);
        await sleep(1500);
        const resultDistro = await evaluate(`document.querySelector('.result-distro-name')?.textContent.trim() || document.querySelector('.best-match-title')?.textContent.trim() || document.body.innerText.includes('Recommendation')`);
        console.log(`Quiz Result Rendered: ${resultDistro}`);
        console.log('✓ All 7 questions successfully completed without auto-advance bug!');
      }
    }

    console.log('\n================ ALL BROWSER QUIZ TESTS PASSED! ================');
  } finally {
    chrome.kill();
  }
}

run().catch(err => {
  console.error('Test failed with error:', err);
  process.exit(1);
});
