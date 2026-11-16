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
  charSelectBg: '#03101D', // sampled from character_select.png edges
  barEmpty: '#474745', // sampled empty stat-bar gray
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
  barsFrom: 66,
  barsStagger: 4,
  barsDuration: 10, // last bar finishes at 66 + 5*4 + 10 = 96
  cursorMoves: [105, 120] as const, // jump right, jump back left
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

// character_select.png (1920x1004)
export const CHAR_SELECT = {
  stageScale: 0.517, // image px -> screen units
  stageTop: 18,
  bars: [
    // x0 = fill start, x1 = fill end, as painted in the image
    {x0: 650, x1: 945, y: 357, h: 34, round: true},
    {x0: 648, x1: 852, y: 454, h: 35, round: false},
    {x0: 650, x1: 914, y: 551, h: 34, round: false},
    {x0: 1315, x1: 1588, y: 357, h: 34, round: false},
    {x0: 1316, x1: 1560, y: 455, h: 34, round: false},
    {x0: 1315, x1: 1582, y: 551, h: 34, round: false},
  ],
  cards: [
    {x: 364, y: 290, w: 258, h: 336},
    {x: 1030, y: 290, w: 259, h: 336},
  ] as Rect[],
  button: {x: 626, y: 682, w: 668, h: 160},
};

// Shot 5 crops (source px). All exclude the player headshots.
export const SHOT5_CROPS = {
  radial: {src: 'images/chart_radial_sg.png', nat: {w: 911, h: 1067}, crop: {x: 120, y: 690, w: 670, h: 377}},
  comparison: {src: 'images/comparison_last20.png', nat: {w: 1285, h: 1046}, crop: {x: 4, y: 328, w: 1277, h: 718}},
  accuracy: {src: 'images/accuracy_report.png', nat: {w: 1299, h: 1561}, crop: {x: 0, y: 392, w: 1299, h: 731}},
};

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
  charSelect: 'images/character_select.png',
  logo: 'images/logo_marquee.png',
  fontPixel: 'fonts/PressStart2P.woff2',
  fontMono: 'fonts/SpaceMono-Bold.woff2',
  clipSize: {w: 1900, h: 888},
};
