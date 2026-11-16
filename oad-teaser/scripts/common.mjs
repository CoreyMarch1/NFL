// Shared helpers for the render scripts.
import {bundle} from '@remotion/bundler';
import {selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// Use CHROME_PATH if set, else a pre-installed Playwright headless shell if
// one exists, else let Remotion download its own browser.
const findBrowser = () => {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = '/opt/pw-browsers';
  if (fs.existsSync(base)) {
    for (const d of fs.readdirSync(base)) {
      if (!d.startsWith('chromium_headless_shell')) continue;
      for (const sub of fs.readdirSync(path.join(base, d))) {
        const p = path.join(base, d, sub, 'chrome-headless-shell');
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined;
};
export const browserExecutable = findBrowser();
export const chromiumOptions = {gl: 'swangle'};

export const prepare = async () => {
  const serveUrl = await bundle({
    entryPoint: path.join(ROOT, 'src/index.ts'),
    publicDir: path.join(ROOT, 'assets'),
  });
  const composition = await selectComposition({serveUrl, id: 'Teaser', browserExecutable, chromiumOptions});
  return {serveUrl, composition};
};
