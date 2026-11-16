# One & Done Optimizer: 2027 Season Teaser

**Working title:** PLAYER 1, READY
**You are building:** a finished 15 second, 16:9 teaser video for X (Twitter), rendered from code using the files in `assets/`.

Read this whole brief before writing any code. Everything you need is here. Where the brief and your own taste disagree, follow the brief, then tell me what you would change.

---

## 1. The idea

One & Done Optimizer is a golf analytics product for PGA Tour One and Done pools (pick one golfer per event, never reuse a golfer, total prize money wins). The brand feeling is **a Saturday morning in 1992, standing at an arcade cabinet, carefully choosing your character so you win.**

The viewer is the kid at the cabinet. We never see them. We only see what they see: a CRT glowing in a dark arcade, a coin going in, a character to choose. The product is the game.

Purpose: build excitement for the 2027 PGA Tour One and Done season. No hard sell. The end card says "2027 SEASON. INSERT COIN."

## 2. Deliverables

| File | Spec |
|---|---|
| `out/oad_teaser_2027_16x9.mp4` | 1920x1080, 30 fps constant, exactly 450 frames (15.000 s), H.264 High profile, yuv420p, CRF 16 to 18, `+faststart`, AAC 48 kHz stereo at 192 kbps or better |
| `out/poster.png` | Frame 420 (end card) as a 1920x1080 still, for the X thumbnail |
| `out/stills/shot_1.png` to `shot_6.png` | One representative frame per shot, for review |
| `out/audio/soundtrack.wav` | The synthesized mix on its own |
| `README.md` | How to re-render, and where each timing, text string and color lives so I can tweak them |

Never exceed 15.000 seconds. Integrated loudness around -14 LUFS, true peak under -1 dBFS.

## 3. Tech approach

Preferred: **Remotion** (React, TypeScript), one composition, 1920x1080, 30 fps, 450 frames. It handles the video clips, CSS and SVG filter effects, and frame-exact timing in one place.

If Remotion cannot be installed in this environment, fall back to an HTML page rendered frame by frame with Playwright, then assembled with ffmpeg. Tell me which path you took and why.

Rules:
- Every animation must be driven by the frame number. No wall-clock timers, no CSS animations that run on their own clock.
- Keep all timings, copy and colors in a single `config.ts` so they are easy to edit.
- Fonts must be bundled locally or loaded through a Remotion font package. Use an open-license pixel font. **Press Start 2P** (OFL) is the default. The site UI uses a wide pixel display face; match it if you can identify an open-license equivalent, otherwise Press Start 2P is fine.
- Audio is synthesized by a script in this repo (section 8). Do not download music or sound effects.

## 4. Assets (already in this folder)

### Video, `assets/video/`

All three are 1920x1080 screen recordings with variable frame rate, an unused audio track, and black letterbox bars. **Active picture is `crop=1920:888:0:96`.** A white browser scrollbar sits on the far right edge and must be cropped out. The page content is left-aligned and does not fill the full width, so crop into the content rather than showing the empty right side.

Before using them: convert each to 30 fps constant frame rate, drop the audio, and apply the crop. Write the results to `assets/video/prepped/`.

| File | Length | What it shows | Motion in the recording |
|---|---|---|---|
| `home_hero.mp4` | 3.5 s | Home page hero: "OPTIMIZE YOUR SEASON" in green and purple pixel type, a pixel golf flag, two buttons | Essentially static |
| `this_week.mp4` | 3.3 s | "This Week" page: event title, a Filters panel with three strategy buttons (FRONT RUNNER, IN THE HUNT, HAIL MARY), and TOP RECOMMENDATIONS with three ranked golfer cards | Static. No clicks happen |
| `roadmap_scroll.mp4` | 6.0 s | "Season Roadmap" page | 0 to 1.5 s: top of page with strategy toggle, green OPTIMIZE SEASON button and the event table. 1.5 to 3.5 s: scrolls down through the full season table. 3.5 to 6.0 s: rests on three stat tiles (PROJECTED EARNINGS $13.35M, LOCKED PICKS 31, EVENTS PLANNED 31/31) |

Because the recordings contain almost no interaction, **you create the motion**: push-ins, pans, reveal masks, highlight overlays and one recreated UI element (the score counter in shot 4). Confirm the timestamps above yourself by extracting frames before you rely on them.

### Images, `assets/images/`

| File | Size | Use |
|---|---|---|
| `logo_marquee.png` | 949x457 | The neon logo with tagline "Insert Coin. Pick Winners." Used as the cabinet marquee and on the end card. It has a dark scenic background, not transparency. Either mask it to the rounded neon frame or blend it into a matching dark background |
| `character_select.png` | 1920x1004 | A finished "CHARACTER SELECT SCREEN" graphic: two pixel golfer cards, three stat bars each (Course History, Recent Form, Course Fit), an orange INSERT COIN button. Shot 2 |
| `chart_radial_sg.png` | 911x1067 | Radial strokes-gained chart. Shot 5 flash. **Contains a real player headshot in the center: crop to a section of the colored ring so the photo is not visible** |
| `comparison_last20.png` | 1285x1046 | Head to head stat comparison. Shot 5 flash. **Contains two real player headshots in the header: crop to the stat rows below the header** |
| `accuracy_report.png` | 1299x1561 | Model accuracy report with three big stat tiles (0.97, 0.95, 0.87). Shot 5 flash. Crop to the three stat tiles and the Top 5, Top 10, Top 20 row |

### Reference only, `assets/reference/`

`ui_this_week_still.png` and `ui_pricing_still.png` are sharp stills of the live site. Use them to sample colors and match type. Do not put them in the video.

## 5. Look and feel

**Palette.** Sample exact values from the assets. Starting points: arcade green `#39FF14`, purple `#A020F0`, cyan `#22D3EE`, coin orange `#FF8A1F`, background near-black navy `#0B0D1A`.

**The cabinet.** Build it in code, not from a stock image. A dark arcade room implied by blackness; a cabinet front with a thick dark bezel around a 4:3-ish curved screen; the logo as a backlit marquee above the screen; faint green and purple glow spilling from the screen onto the bezel. Simple and graphic is better than fake-realistic.

**CRT treatment on everything shown on the screen:**
- Scanlines (2 px period, about 15 to 20 percent darkness), plus a slow rolling brightness band
- Phosphor bloom on bright greens and purples
- Slight RGB channel offset, 1 to 2 px, stronger toward the edges
- Subtle barrel curvature and vignette, visible mainly when the bezel is in frame
- Light noise and 1 to 2 percent brightness flicker

**Legibility rule.** The bezel is visible in shots 1, 2 and 6. In shots 3, 4 and 5 the camera is pushed in past the bezel so the UI fills the frame; keep scanlines and bloom but drop the curvature. If a viewer on a phone cannot read the three golfer cards in shot 3, the effect is too heavy.

**Title cards (supers).** Pixel font, all caps, green fill with a purple hard drop shadow (4 px offset), thin dark outline for contrast. Positioned in the lower third, inside a 5 percent title-safe margin. Each one types on over 6 frames or snaps in with a 2 frame white flash. Five words maximum. No em dashes anywhere in on-screen text.

## 6. Shot list

30 fps. Frame numbers are inclusive start, exclusive end. Music is 120 BPM, so one beat is exactly 15 frames and every cut below lands on a beat.

### Shot 1, frames 0 to 60 (0:00 to 0:02): Insert coin
- 0 to 12: black. Coin sound at frame 3.
- 12 to 20: CRT power-on. A horizontal white line expands vertically into the full picture with a brightness overshoot.
- 20 to 60: wide view of the cabinet. Marquee logo flickers on. `home_hero.mp4` plays on the screen as the attract mode. Slow push in toward the screen (scale about 1.00 to 1.12).
- Super: none. "OPTIMIZE YOUR SEASON" is already in the UI and must be readable.

### Shot 2, frames 60 to 150 (0:02 to 0:05): Choose your golfer
- Hard cut. `character_select.png` on the CRT with the bezel still visible at the edges.
- Mask the six stat bars and animate them filling left to right between frames 66 and 96, staggered 4 frames apart.
- A bright selection outline blinks on the left golfer card, jumps to the right card at frame 105, back to the left at frame 120, then locks at frame 135 with a 3 frame white flash.
- The orange INSERT COIN button pulses on each beat.
- Super, frames 72 to 144: **CHOOSE YOUR GOLFER**

### Shot 3, frames 150 to 240 (0:05 to 0:08): The right pick
- 2 frame white flash, then `this_week.mp4`, cropped tight to the Filters panel plus the TOP RECOMMENDATIONS column so it fills the frame.
- The three recommendation cards start hidden behind masks that match the page background. Reveal card 1 at frame 165, card 2 at 180, card 3 at 195. Each punches in with a quick scale from 1.08 to 1.00 and a green edge flash.
- Frames 205 to 235: a highlight sweeps across the three strategy buttons in order (FRONT RUNNER, IN THE HUNT, HAIL MARY), 10 frames each, as an overlay glow.
- Super, frames 160 to 236: **THE RIGHT PICK. EVERY WEEK.**

### Shot 4, frames 240 to 330 (0:08 to 0:11): Map the whole season
- 240 to 262: top of `roadmap_scroll.mp4`. A pixel arrow cursor (you draw it) moves to the green OPTIMIZE SEASON button and presses it at frame 255: button flash plus a 2 px press offset.
- 262 to 285: the scrolling section of the clip, sped up so the whole season table whips past with vertical motion blur.
- 285 to 330: land on the stat tiles and push in on PROJECTED EARNINGS. Cover the real tile with a recreated tile in the same style whose value counts up from $0.00M to $13.35M between frames 288 and 318, easing out, then flashes green and holds. LOCKED PICKS and EVENTS PLANNED stay as recorded.
- Super, frames 250 to 326: **MAP THE WHOLE SEASON**

### Shot 5, frames 330 to 390 (0:11 to 0:13): Unfair advantage
- Three 20 frame flashes, hard cuts, each with a fast push in (scale 1.00 to 1.10):
  - 330 to 350: `chart_radial_sg.png`, cropped to the ring, no headshot
  - 350 to 370: `comparison_last20.png`, cropped to the stat rows, no headshots
  - 370 to 390: `accuracy_report.png`, cropped to the stat tiles
- These are meant to register as depth, not to be read.
- Super, held across all three, frames 334 to 388: **YOUR UNFAIR ADVANTAGE**

### Shot 6, frames 390 to 450 (0:13 to 0:15): End card
- 390 to 405: fast pull back out to the full cabinet.
- 405 to 450: the screen shows the logo large and centered. Beneath it, **2027 SEASON. INSERT COIN.** blinks on at 408, off at 420, on at 426 and stays on.
- Small line at the bottom of the screen area: `1doneoptimizer.com   @1nDoneOptimizer`
- Final 6 frames: hold, no fade to black, so the loop on X restarts cleanly into the black of shot 1.

## 7. Copy sheet (exact strings)

```
CHOOSE YOUR GOLFER
THE RIGHT PICK. EVERY WEEK.
MAP THE WHOLE SEASON
YOUR UNFAIR ADVANTAGE
2027 SEASON. INSERT COIN.
1doneoptimizer.com
@1nDoneOptimizer
```

## 8. Audio

Write a script (`scripts/make_audio.ts` or `.py`) that synthesizes the full soundtrack to `out/audio/soundtrack.wav` at 48 kHz stereo. Everything is generated from oscillators and noise. No samples, no downloads, and nothing that imitates a recognizable game theme or sound.

No voiceover.

**Music.** Original chiptune, 120 BPM, A minor, 4/4. Two pulse-wave voices (lead and sixteenth-note arpeggio), one triangle bass, one noise channel for drums.
- 0:00 to 0:02: no music. Low 60 Hz cabinet hum only.
- 0:02 to 0:05: arpeggio and bass enter on the cut. Sparse.
- 0:05 to 0:11: full groove with drums and lead melody. Energy rises every two bars.
- 0:11 to 0:13: drum fill and rising arpeggio.
- 0:13: hard stop on the downbeat, then the end jingle.

**Sound effects**, frame-accurate:

| Frame | Sound |
|---|---|
| 3 | Coin drop: two quick high metallic pings |
| 12 | CRT power-on: low thunk plus a rising whine |
| 66 to 96 | Soft ascending ticks as the stat bars fill |
| 105, 120 | Menu blip on each cursor move |
| 135 | Select confirm: two-note rising chirp |
| 165, 180, 195 | Three rising confirm tones, one per card |
| 255 | Button press click |
| 288 to 318 | Fast score-counter ticking, pitch rising |
| 318 | "Level clear" three-note sting |
| 330, 350, 370 | Short noise hits on each flash cut |
| 393 | Single coin drop |
| 405 | Five-note "ready" jingle, major key, resolving by frame 440 |

Keep the effects above the music in the mix. Everything must still make sense with the sound off.

## 9. Hard constraints

- No real golfer photographs or illustrated likenesses anywhere in a readable frame. Golfer names appearing inside the product UI are fine.
- No third-party logos (apparel, equipment, tournament sponsors) added by you. If one appears incidentally inside a UI recording, do not zoom in on it.
- No recognizable game characters, sprites, music or sound effects. All arcade elements are original.
- Do not invent product claims, numbers or features. Only use text listed in section 7 or already present in the assets.
- Do not alter any numbers shown in the recorded UI other than animating the $13.35M count-up to its real final value.
- Do not upscale small assets beyond about 150 percent without checking for blur. `logo_marquee.png` is only 949 px wide: on the end card, keep it at or under 1300 px wide and let glow carry the rest.

## 10. How to work

1. Inspect every asset first: extract frames from each video, view each image, confirm the crop values and timestamps in section 4.
2. Prep the video clips (CFR, crop, no audio).
3. Build the cabinet and CRT layer, then render **one still per shot** to `out/stills/` and look at them yourself. Fix legibility and composition problems before animating.
4. Stop and show me the six stills. Wait for my go-ahead.
5. Animate, synthesize audio, render the full video.
6. Run the checks in section 11 and report the results.

## 11. Acceptance checks

Run these and include the output in your final message:
- `ffprobe` shows 1920x1080, 30 fps, 450 video frames, duration 15.000 s, H.264 yuv420p, AAC 48 kHz stereo.
- Loudness measured with ffmpeg `loudnorm` or `ebur128`: integrated about -14 LUFS, true peak under -1 dBFS.
- Extract frames 30, 100, 200, 310, 360 and 430 from the final MP4 and view them. Confirm each super is spelled exactly as in section 7, sits inside title-safe, and is readable.
- Scale frame 200 down to 640x360 and confirm the three golfer cards are still legible. This simulates a phone feed.
- Confirm no headshot is visible in frames 330 to 390.
- Confirm cuts land on frames 60, 150, 240, 330 and 390.

## 12. Known limitations to flag, not fix

- The UI recordings show 2026 season data. That is acceptable for this cut. Structure the project so I can drop in new recordings with the same file names and re-render.
- The recordings are short and mostly static. If a shot feels thin, tell me exactly what new capture would improve it (page, action, length) rather than padding with invented UI.
