# One & Done Optimizer: 2027 Season Teaser

15 second, 1920x1080, 30 fps teaser ("PLAYER 1, READY"), rendered from code with
[Remotion](https://www.remotion.dev). The creative brief is in `BRIEF.md`.

## Re-render

Requirements: Node 18+, ffmpeg, Python 3 with numpy.

```bash
npm install
```

```bash
npm run prep     # raw recordings -> assets/video/prepped (30 fps CFR, cropped, no audio)
```

```bash
npm run audio    # synthesize out/audio/soundtrack.wav (-14 LUFS)
```

```bash
npm run stills   # out/stills/shot_1..6.png and out/poster.png
```

```bash
npm run render   # out/oad_teaser_2027_16x9.mp4 (about 20 minutes)
```

`npm run all` runs the four steps in order. Other useful commands:

- `node scripts/stills.mjs 30 100 200` renders specific frames to `out/stills/frame_NNN.png`.
- `node scripts/render.mjs 150 240` renders a silent draft of one frame range.
- `npm run studio` opens Remotion Studio to scrub the timeline.

Rendering uses the Chrome at `CHROME_PATH` if set, otherwise a pre-installed
Playwright headless shell, otherwise Remotion downloads its own.

### Dropping in new recordings

Replace `assets/video/home_hero.mp4`, `this_week.mp4` and `roadmap_scroll.mp4`
with new captures of the same pages at 1920x1080 (same file names), then run
`npm run all`. If the page layout moved, update the rectangles in the LAYOUT
section of `src/config.ts`. If the scroll timing in the roadmap capture changed,
update `SHOT4.srcScroll` and `SHOT4.srcRestFrame` (source frame numbers at 30 fps).

## Where things live

Everything you are likely to tweak is in **`src/config.ts`**:

| What | Where in `src/config.ts` |
|---|---|
| Colors | `COLORS` |
| All on-screen text | `COPY` |
| Super timing, size, position, type-on vs snap | `SUPERS`, `SUPER_STYLE` |
| Cut points | `CUTS` |
| Per-shot timings (coin, power-on, bar fills, cursor moves, card reveals, button press, whip, count-up, end-card blink) | `SHOT1` to `SHOT6` |
| CRT look (scanlines, RGB offset, bloom, noise, flicker, rolling band) | `CRT` |
| Cabinet geometry | `CABINET` |
| Crop windows and overlay rectangles for each asset | `HOME`, `THIS_WEEK`, `ROADMAP`, `SEASON_TABLE`, `SHOT5_FLASHES`, `LOGO` |
| Asset file names | `ASSETS` |

Other files:

| File | Purpose |
|---|---|
| `src/Teaser.tsx` | Picks the shot for the current frame and layers the supers on top |
| `src/shots/CabinetShots.tsx` | Shots 1, 2 and 6 (bezel visible) |
| `src/shots/FullShots.tsx` | Shots 3, 4 and 5 (camera pushed in past the bezel) |
| `src/components/Cabinet.tsx` | The arcade cabinet, marquee, bezel and camera |
| `src/components/CRT.tsx` | CRT treatment |
| `src/components/Super.tsx` | Title cards |
| `scripts/make_audio.py` | Soundtrack synth. SFX frame numbers are in the `SFX` dict at the top; music structure in `PROG`, `LEAD` and `energy()`; mix levels in `MUSIC_GAIN`, `SFX_GAIN`; loudness target in `TARGET_LUFS` |
| `scripts/prep_video.sh` | Clip prep (crop value is at the top) |
| `scripts/stills.mjs` | Review stills. `POSTER_FRAME` and the per-shot still frames are at the top |
| `scripts/render.mjs` | Final render and encode settings (CRF, AAC bitrate) |

Every animation is a pure function of the frame number: there are no timers or
free-running CSS animations, and recordings are sampled by explicit source frame.

## Recordings first

Every shot is built from the three product screen recordings. The only still
image in the cut is `logo_marquee.png` (cabinet marquee and end card).
`character_select.png` and the three chart PNGs in `assets/images/` are not used.

Shots 2 and 5 show the Season Roadmap table as two strips of the recording
placed side by side (`SEASON_TABLE.strips`): the event column and the
earnings + golfer selection columns. This closes the empty middle of each row
so the text can be shown about twice as large. Nothing inside the strips is changed.

## Fonts and licenses

- Press Start 2P (SIL OFL 1.1), bundled at `assets/fonts/PressStart2P.woff2`: supers, end card, tile label.
- Space Mono Bold (SIL OFL 1.1), bundled at `assets/fonts/SpaceMono-Bold.woff2`: the recreated PROJECTED EARNINGS value only, to match the recorded UI.
- Remotion has its own license; it is free for individuals and small teams, larger companies need a company license. See remotion.dev/license.
- All audio is synthesized by `scripts/make_audio.py`. No samples or downloads.
