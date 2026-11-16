// Renders review stills. Usage:
//   node scripts/stills.mjs                 -> one still per shot + poster
//   node scripts/stills.mjs 30 100 200      -> specific frames to out/stills/frame_NNN.png
import {renderStill} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {ROOT, browserExecutable, chromiumOptions, prepare} from './common.mjs';

// Brief asks for frame 420, but the end-card line is blinked OFF on 420..425,
// so the poster uses a frame where it is on. Set to 420 for the literal brief.
const POSTER_FRAME = 440;
const SHOT_FRAMES = {shot_1: 48, shot_2: 110, shot_3: 214, shot_4: 322, shot_5: 362, shot_6: 432};
const args = process.argv.slice(2).map(Number);
const jobs = args.length
  ? args.map((f) => [`out/stills/frame_${String(f).padStart(3, '0')}.png`, f])
  : [...Object.entries(SHOT_FRAMES).map(([n, f]) => [`out/stills/${n}.png`, f]), ['out/poster.png', POSTER_FRAME]];

fs.mkdirSync(path.join(ROOT, 'out/stills'), {recursive: true});
const {serveUrl, composition} = await prepare();
for (const [file, frame] of jobs) {
  await renderStill({serveUrl, composition, frame, output: path.join(ROOT, file), imageFormat: 'png', browserExecutable, chromiumOptions});
  console.log(`frame ${frame} -> ${file}`);
}
