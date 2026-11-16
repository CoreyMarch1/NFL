// Full render: Remotion renders every frame to PNG, then ffmpeg encodes the
// final H.264 + AAC file in one pass (so there is only one lossy generation).
//   node scripts/render.mjs            -> out/oad_teaser_2027_16x9.mp4
//   node scripts/render.mjs 150 240    -> draft of a frame range to out/draft_150_240.mp4 (no audio)
import {renderFrames} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {ROOT, browserExecutable, chromiumOptions, prepare} from './common.mjs';

const [a, b] = process.argv.slice(2).map(Number);
const draft = Number.isFinite(a) && Number.isFinite(b);
const framesDir = path.join(ROOT, 'out/frames');
fs.rmSync(framesDir, {recursive: true, force: true});
fs.mkdirSync(framesDir, {recursive: true});

const {serveUrl, composition} = await prepare();
const total = draft ? b - a : composition.durationInFrames;
let last = 0;
await renderFrames({
  serveUrl,
  composition,
  inputProps: {},
  outputDir: framesDir,
  imageFormat: 'png',
  frameRange: draft ? [a, b - 1] : null,
  browserExecutable,
  chromiumOptions,
  onStart: () => console.log(`rendering ${total} frames...`),
  onFrameUpdate: (n) => {
    if (n - last >= 30 || n === total) {
      last = n;
      console.log(`  ${n}/${total}`);
    }
  },
});

const files = fs.readdirSync(framesDir).filter((f) => f.endsWith('.png')).sort();
if (files.length !== total) throw new Error(`expected ${total} frames, got ${files.length}`);
// rename to a gapless sequence for ffmpeg
files.forEach((f, i) => fs.renameSync(path.join(framesDir, f), path.join(framesDir, `f_${String(i).padStart(4, '0')}.png`)));

const video = ['-framerate', '30', '-i', path.join(framesDir, 'f_%04d.png')];
const x264 = ['-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30',
  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-vf', 'scale=out_color_matrix=bt709:out_range=tv'];
if (draft) {
  const out = path.join(ROOT, `out/draft_${a}_${b}.mp4`);
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...video, ...x264, '-movflags', '+faststart', out], {stdio: 'inherit'});
  console.log(`wrote ${out}`);
} else {
  const out = path.join(ROOT, 'out/oad_teaser_2027_16x9.mp4');
  const audio = path.join(ROOT, 'out/audio/soundtrack.wav');
  if (!fs.existsSync(audio)) throw new Error('run scripts/make_audio.py first');
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...video, '-i', audio, ...x264, '-frames:v', String(total),
    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-ac', '2', '-t', '15', '-movflags', '+faststart', out], {stdio: 'inherit'});
  console.log(`wrote ${out}`);
}
fs.rmSync(framesDir, {recursive: true, force: true});
