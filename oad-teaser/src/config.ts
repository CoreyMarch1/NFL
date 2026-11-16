// ---------------------------------------------------------------------------
// ONE & DONE OPTIMIZER: 2027 SEASON TEASER
// Every timing, text string, color and crop rectangle lives in this file.
// All frame numbers are at 30 fps; ranges are [inclusive start, exclusive end).
// ---------------------------------------------------------------------------

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION = 450; // 15.000 s
export const BEAT = 15; // 120 BPM

// ------------------------------- COLORS -----------------------------------
export const COLORS = {
  green: '#39FF14', // sampled from the site UI (hero text, buttons)
  purple: '#A020F0',
  cyan: '#22D3EE',
  orange: '#FF8A1F',
  white: '#F4F7FF',
  bg: '#0B0D1A', // brand near-black navy
  pageBg: '#090C19', // sampled from the recordings (rgb 9,12,25)
  tileBg: '#18182C', // sampled from the roadmap stat tiles
  tileLabel: '#9A98A8',
  logoBg: '#06090F', // sampled from logo_marquee.png corners
  cabinet: '#0A0C18',
  bezel: '#05060C',
  superOutline: '#05060C',
};

// -------------------------------- COPY ------------------------------------
export const COPY = {
  super1: 'CHOOSE YOUR GOLFER',
  super2: 'THE RIGHT PICK. EVERY WEEK.',
  super3: 'MAP THE WHOLE SEASON',
  super4: 'YOUR UNFAIR ADVANTAGE',
  endCard: '2027 SEASON. INSERT COIN.',
  site: '1doneoptimizer.com',
  handle: '@1nDoneOptimizer',
  tileLabel: 'PROJECTED EARNINGS', // recreated tile, text already in the UI
};

// ------------------------------- SUPERS -----------------------------------
// mode 'type': types on over 6 frames. mode 'snap': snaps in with a 2 frame
// white flash. y is the vertical center of the text in the 1080p frame.
export type SuperDef = {
  text: string;
  from: number;
  to: number;
  mode: 'type' | 'snap';
  size: number;
  y: number;
};
export const SUPERS: SuperDef[] = [
  {text: COPY.super1, from: 72, to: 144, mode: 'type', size: 60, y: 952},
  {text: COPY.super2, from: 160, to: 236, mode: 'snap', size: 54, y: 962},
  {text: COPY.super3, from: 250, to: 326, mode: 'type', size: 60, y: 952},
  {text: COPY.super4, from: 334, to: 388, mode: 'snap', size: 60, y: 952},
];
export const SUPER_STYLE = {
  typeFrames: 6,
  flashFrames: 2,
  shadowOffset: 4,
  outline: 3,
  scrim: 0.62, // darkness of the soft band behind each super
  safeMargin: 0.05,
};

// ------------------------------- TIMINGS ----------------------------------
export const CUTS = {shot2: 60, shot3: 150, shot4: 240, shot5: 330, shot6: 390};

export const SHOT1 = {
  coinAt: 3,
  powerOn: [12, 20] as const, // CRT line expands into picture
  marqueeOn: 20,
  pushScale: [1.0, 1.12] as const,
  pushAnchor: {x: 960, y: 150}, // world point that stays fixed during the push
  clipStart: 6, // first source frame of home_hero (skips recorder warm-up)
};

export const SHOT2 = {
  cameraScale: [1.78, 1.84] as const, // screen fills the frame, bezel at sides
  srcFrame: 4, // roadmap_scroll source frame (top of page, at rest)
  rowsFrom: 66, // season rows wipe on one by one
  rowsStagger: 4,
  rowsDuration: 10, // last row finishes at 66 + 5*4 + 10 = 96
  cursorRows: [0, 2, 1] as const, // row selected at start, after move 1, after move 2
  cursorMoves: [105, 120] as const,
  lockAt: 135,
  lockFlashFrames: 3,
  blinkPeriod: 6,
};

export const SHOT3 = {
  flashFrames: 2,
  clipStart: 6,
  cardReveals: [165, 180, 195] as const,
  punchFrames: 7,
  punchScale: 1.08,
  sweepFrom: 205,
  sweepEach: 10,
};

export const SHOT4 = {
  pressAt: 255,
  whip: [262, 285] as const,
  // Source frames (30 fps) measured from roadmap_scroll.mp4:
  // page is at rest until ~61, scrolls 62..126, rests on the tiles from 128.
  srcTopFrame: 4,
  srcScroll: [60, 128] as const,
  srcRestFrame: 128,
  whipBlur: 16, // px of vertical gaussian blur at peak
  count: [288, 318] as const,
  countTo: 13.35,
};

export const SHOT5 = {
  flashes: [330, 350, 370] as const,
  each: 20,
  push: [1.0, 1.1] as const,
};

export const SHOT6 = {
  pullBack: [390, 405] as const,
  closeScale: 1.5, // camera scale at the cut (logo is 1290 px wide here)
  wideCam: {s: 1.08, tx: -76.8, ty: -22}, // full cabinet framing
  driftScale: 1.1,
  blink: {on1: 408, off: 420, on2: 426},
  holdFrom: 444,
};

// ------------------------------- LAYOUT -----------------------------------
export type Rect = {x: number; y: number; w: number; h: number};

// Cabinet, in 1920x1080 "world" units at camera scale 1.
export const CABINET = {
  body: {x: 400, y: -40, w: 1120, h: 1200},
  marquee: {x: 440, y: 28, w: 1040, h: 186},
  bezel: {x: 440, y: 254, w: 1040, h: 764},
  screen: {x: 484, y: 296, w: 952, h: 680}, // 1.4:1, "4:3-ish"
  screenRadius: 30,
  screenBulge: 7,
};

// CRT effect strengths.
export const CRT = {
  scanlineAlpha: 0.34, // dark line alpha; 2 px period => ~17% average darkness
  rgbOffset: 1.25, // px of channel offset at the frame edge (0 at center)
  bloom: 0.55,
  bloomRadius: 12,
  noise: 0.07,
  flicker: 0.015,
  rollPeriod: 130, // frames for the brightness band to travel the screen
  rollStrength: 0.055,
};

// Source-pixel rectangles inside the prepped recordings (1900x888).
export const HOME = {
  window: {x: 250, y: 67, w: 1150, h: 821.4}, // hero crop shown on the CRT
};

export const THIS_WEEK = {
  // 16:9 window on the Filters panel + TOP RECOMMENDATIONS column.
  window: {x: 236, y: 372, w: 1064, h: 598.5},
  cards: [
    {x: 606, y: 449, w: 674, h: 118},
    {x: 606, y: 581, w: 674, h: 118},
    {x: 606, y: 713, w: 674, h: 118},
  ] as Rect[],
  buttons: [
    {x: 281, y: 496, w: 269, h: 33}, // FRONT RUNNER
    {x: 281, y: 536, w: 269, h: 33}, // IN THE HUNT
    {x: 281, y: 575, w: 269, h: 33}, // HAIL MARY
  ] as Rect[],
  // Areas painted with the page background so the frame ends cleanly
  // (the recording is cut off mid-panel below these lines).
  hideLeftBelow: 696,
  hideAllBelow: 846,
};

export const ROADMAP = {
  topWindow: [
    {x: -44, y: -22, w: 1624, h: 913.5},
    {x: 0, y: 0, w: 1536, h: 864},
  ] as Rect[],
  whipWindow: {x: 0, y: 12, w: 1536, h: 864},
  tilesWindow: [
    {x: 0, y: 12, w: 1536, h: 864},
    {x: 0, y: 96, w: 1090, h: 613.1},
  ] as Rect[],
  button: {x: 1037, y: 264, w: 490, h: 56},
  cursorFrom: {x: 760, y: 620},
  cursorTo: {x: 1290, y: 296},
  earningsTile: {x: 17, y: 217, w: 484, h: 115},
  tileLabelY: 250, // vertical centers measured from the recording
  tileValueY: 288,
};

// The season table as shown in shots 2 and 5: two strips of the recording
// (event column, then earnings + golfer selection) placed side by side, which
// closes the empty middle of each row so the text can be shown larger.
export const SEASON_TABLE = {
  strips: [
    {x: 16, w: 454},
    {x: 1000, w: 416},
  ],
  width: 870,
  rowTop: 428, // source y of the first row at the top-of-page frame
  rowPitch: 73,
  rows: 6,
  rowBg: '#12101C', // sampled row background
  selector: {x: 1156, w: 238, dy: 16, h: 42}, // golfer dropdown inside a row
  shot2Top: 330, // source y shown at the top of the CRT in shot 2
};

// Shot 5: three flashes cut from the recordings.
// type 'table' uses the two-strip season table (window is in strip coordinates),
// type 'clip' is a plain window onto a recording.
export type Flash = {type: 'table' | 'clip'; src: string; sourceFrame: number; win: {x: number; y: number; w: number; h: number}};
export const SHOT5_FLASHES: Flash[] = [
  {type: 'table', src: 'video/prepped/roadmap_scroll.mp4', sourceFrame: 92, win: {x: 0, y: 70, w: 870, h: 489}},
  {type: 'clip', src: 'video/prepped/roadmap_scroll.mp4', sourceFrame: 150, win: {x: 0, y: 350, w: 956, h: 538}},
  {type: 'clip', src: 'video/prepped/this_week.mp4', sourceFrame: 40, win: {x: 560, y: 380, w: 840, h: 472.5}},
];

// logo_marquee.png (949x457)
export const LOGO = {
  nat: {w: 949, h: 457},
  neonFrame: {x: 118, y: 88, w: 708, h: 300, r: 44}, // rounded neon frame
  endCardWidth: 860, // screen units; 1290 px in frame at the closest camera (limit 1300)
};

export const ASSETS = {
  home: 'video/prepped/home_hero.mp4',
  thisWeek: 'video/prepped/this_week.mp4',
  roadmap: 'video/prepped/roadmap_scroll.mp4',
  logo: 'images/logo_marquee.png',
  fontPixel: 'fonts/PressStart2P.woff2',
  fontMono: 'fonts/SpaceMono-Bold.woff2',
  clipSize: {w: 1900, h: 888},
};
