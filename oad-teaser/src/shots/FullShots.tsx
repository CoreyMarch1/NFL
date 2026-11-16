import React from 'react';
import {ASSETS, COLORS, COPY, CUTS, ROADMAP, SHOT3, SHOT4, SHOT5, SHOT5_FLASHES, THIS_WEEK} from '../config';
import {FullFrameCRT} from '../components/CRT';
import {Box, Clip, MONO_FONT, PIXEL_FONT, SeasonTable, Window, easeInOut, easeOut, lerp, lerpRect, prog} from '../components/util';

// ---------------------------- SHOT 3: THE RIGHT PICK -------------------------
export const Shot3: React.FC<{frame: number}> = ({frame}) => {
  const src = SHOT3.clipStart + (frame - CUTS.shot3);
  const push = lerp(1, 1.035, prog(frame, CUTS.shot3, CUTS.shot4));
  const w0 = THIS_WEEK.window;
  const win = {x: w0.x + (w0.w - w0.w / push) / 2, y: w0.y + (w0.h - w0.h / push) * 0.35, w: w0.w / push};
  const flash = frame < CUTS.shot3 + SHOT3.flashFrames;
  const sweepIdx = Math.floor((frame - SHOT3.sweepFrom) / SHOT3.sweepEach);
  const sweepT = ((frame - SHOT3.sweepFrom) % SHOT3.sweepEach) / SHOT3.sweepEach;
  return (
    <FullFrameCRT frame={frame}>
      <Window win={win} outW={1920} outH={1080} background={COLORS.pageBg}>
        <Clip src={ASSETS.thisWeek} sourceFrame={src} />
        {/* clean ends where the recording is cut off mid-panel */}
        <div style={{position: 'absolute', left: 0, top: THIS_WEEK.hideLeftBelow, width: 596, height: 400, background: COLORS.pageBg}} />
        <div style={{position: 'absolute', left: -200, top: THIS_WEEK.hideAllBelow, width: 2300, height: 400, background: COLORS.pageBg}} />
        {THIS_WEEK.cards.map((c, i) => {
          const at = SHOT3.cardReveals[i];
          if (frame < at) {
            // hidden behind a mask matching the page background
            return <Box key={i} r={{x: c.x - 6, y: c.y - 6, w: c.w + 12, h: c.h + 12}} style={{background: COLORS.pageBg}} />;
          }
          const p = prog(frame, at, at + SHOT3.punchFrames);
          const glow = 1 - prog(frame, at, at + 12);
          if (glow <= 0) return null;
          const s = lerp(SHOT3.punchScale, 1, easeOut(p));
          return (
            <Box
              key={i}
              r={c}
              style={{
                overflow: 'hidden',
                transform: `scale(${s})`,
                background: COLORS.pageBg,
                boxShadow: `0 0 0 ${4 * glow}px rgba(57,255,20,${glow}), 0 0 ${50 * glow}px rgba(57,255,20,${0.9 * glow})`,
              }}
            >
              <Clip src={ASSETS.thisWeek} sourceFrame={src} style={{left: -c.x, top: -c.y}} />
              <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: frame - at < 2 ? 0.55 : 0}} />
            </Box>
          );
        })}
        {/* highlight sweep across the strategy buttons */}
        {sweepIdx >= 0 && sweepIdx < 3 ? (
          <Box
            r={THIS_WEEK.buttons[sweepIdx]}
            style={{
              border: `3px solid ${COLORS.white}`,
              background: `rgba(57,255,20,${0.38 * (1 - sweepT * 0.6)})`,
              boxShadow: `0 0 26px ${COLORS.green}, 0 0 60px rgba(57,255,20,0.7)`,
              mixBlendMode: 'screen',
            }}
          />
        ) : null}
      </Window>
      {flash ? <div style={{position: 'absolute', inset: 0, background: '#fff'}} /> : null}
    </FullFrameCRT>
  );
};

// -------------------------- SHOT 4: MAP THE WHOLE SEASON ---------------------
const PixelCursor: React.FC<{x: number; y: number; scale: number}> = ({x, y, scale}) => {
  // original 11x16 pixel arrow; 1 = outline, 2 = fill
  const rows = [
    '1',
    '11',
    '121',
    '1221',
    '12221',
    '122221',
    '1222221',
    '12222221',
    '122222221',
    '1222222221',
    '12222211111',
    '1221221',
    '121 1221',
    '11  1221',
    '1    1221',
    '     111',
  ];
  const px = 5 * scale;
  return (
    <div style={{position: 'absolute', left: x, top: y, filter: 'drop-shadow(3px 4px 0 rgba(0,0,0,0.6))'}}>
      {rows.map((r, j) =>
        r.split('').map((ch, i) =>
          ch === ' ' ? null : (
            <div
              key={`${i}-${j}`}
              style={{
                position: 'absolute',
                left: i * px,
                top: j * px,
                width: px + 0.5,
                height: px + 0.5,
                background: ch === '1' ? '#05060c' : '#ffffff',
              }}
            />
          ),
        ),
      )}
    </div>
  );
};

export const Shot4: React.FC<{frame: number}> = ({frame}) => {
  const [w0, w1] = SHOT4.whip;
  let content: React.ReactNode;
  if (frame < w0) {
    // top of the page: cursor travels to OPTIMIZE SEASON and presses it
    const win = lerpRect(ROADMAP.topWindow[0], ROADMAP.topWindow[1], easeInOut(prog(frame, CUTS.shot4, w0)));
    const ct = easeOut(prog(frame, CUTS.shot4 + 1, SHOT4.pressAt - 2));
    const pressed = frame >= SHOT4.pressAt && frame < SHOT4.pressAt + 4;
    const off = pressed ? 2 : 0;
    const flash = 1 - prog(frame, SHOT4.pressAt, SHOT4.pressAt + 6);
    const b = ROADMAP.button;
    const cx = lerp(ROADMAP.cursorFrom.x, ROADMAP.cursorTo.x, ct) + off;
    const cy = lerp(ROADMAP.cursorFrom.y, ROADMAP.cursorTo.y, ct) + off;
    content = (
      <Window win={win} outW={1920} outH={1080} background={COLORS.pageBg}>
        <Clip src={ASSETS.roadmap} sourceFrame={SHOT4.srcTopFrame} />
        {frame >= SHOT4.pressAt ? (
          <>
            <Box r={{x: b.x - 4, y: b.y - 4, w: b.w + 8, h: b.h + 8}} style={{background: COLORS.pageBg}} />
            <Box
              r={b}
              style={{
                overflow: 'hidden',
                transform: `translate(${off}px, ${off}px)`,
                boxShadow: `0 0 ${60 * flash}px rgba(57,255,20,${flash})`,
              }}
            >
              <Clip src={ASSETS.roadmap} sourceFrame={SHOT4.srcTopFrame} style={{left: -b.x, top: -b.y}} />
              <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: 0.85 * flash}} />
            </Box>
          </>
        ) : null}
        <PixelCursor x={cx} y={cy} scale={pressed ? 0.9 : 1} />
      </Window>
    );
  } else if (frame < w1) {
    // the season table whips past: sped-up scroll plus vertical motion blur
    const t = prog(frame, w0, w1);
    const src = lerp(SHOT4.srcScroll[0], SHOT4.srcScroll[1], t);
    const blur = SHOT4.whipBlur * Math.sin(Math.PI * Math.min(1, t * 1.08)) ** 0.6;
    content = (
      <>
        <svg width="0" height="0" style={{position: 'absolute'}}>
          <filter id="whip" x="0" y="-10%" width="100%" height="120%">
            <feGaussianBlur stdDeviation={`0 ${Math.max(0.01, blur)}`} />
          </filter>
        </svg>
        <div style={{position: 'absolute', inset: 0, filter: 'url(#whip)'}}>
          <Window win={ROADMAP.whipWindow} outW={1920} outH={1080} background={COLORS.pageBg}>
            <Clip src={ASSETS.roadmap} sourceFrame={src} />
          </Window>
        </div>
      </>
    );
  } else {
    // land on the stat tiles, push in on PROJECTED EARNINGS, count up
    const win = lerpRect(ROADMAP.tilesWindow[0], ROADMAP.tilesWindow[1], easeOut(prog(frame, w1, w1 + 26)));
    const [c0, c1] = SHOT4.count;
    const value = SHOT4.countTo * easeOut(prog(frame, c0, c1));
    const done = frame >= c1;
    const flash = done ? 1 - prog(frame, c1, c1 + 9) : 0;
    const tile = ROADMAP.earningsTile;
    content = (
      <Window win={win} outW={1920} outH={1080} background={COLORS.pageBg}>
        <Clip src={ASSETS.roadmap} sourceFrame={SHOT4.srcRestFrame + (frame - w1)} />
        {/* recreated tile face in the recorded tile's own style */}
        <Box
          r={{x: tile.x + 4, y: tile.y + 5, w: tile.w - 10, h: tile.h - 11}}
          style={{background: COLORS.tileBg, boxShadow: `inset 0 0 ${30 * flash}px rgba(57,255,20,${0.8 * flash})`}}
        >
          <div
            style={{
              position: 'absolute',
              left: 0,
              width: '100%',
              top: ROADMAP.tileLabelY - tile.y - 5 - 6,
              textAlign: 'center',
              fontFamily: PIXEL_FONT,
              fontSize: 11.5,
              lineHeight: '12px',
              letterSpacing: 0.4,
              color: COLORS.tileLabel,
              whiteSpace: 'pre',
            }}
          >
            {COPY.tileLabel.replace(' ', '  ')}
          </div>
          <div
            style={{
              position: 'absolute',
              left: 0,
              width: '100%',
              top: ROADMAP.tileValueY - tile.y - 5 - 21,
              textAlign: 'center',
              fontFamily: MONO_FONT,
              fontWeight: 700,
              fontSize: 31,
              lineHeight: '42px',
              color: flash > 0 ? `color-mix(in srgb, ${COLORS.green} ${Math.round(flash * 100)}%, #ffffff)` : '#ffffff',
              textShadow: `0 0 ${18 * flash}px ${COLORS.green}`,
            }}
          >
            {`$${value.toFixed(2)}M`}
          </div>
        </Box>
        {flash > 0 ? (
          <Box
            r={tile}
            style={{
              boxShadow: `0 0 0 ${3 * flash}px rgba(57,255,20,${flash}), 0 0 ${60 * flash}px rgba(57,255,20,${flash})`,
            }}
          />
        ) : null}
      </Window>
    );
  }
  return <FullFrameCRT frame={frame}>{content}</FullFrameCRT>;
};

// --------------------------- SHOT 5: UNFAIR ADVANTAGE ------------------------
// Three fast flashes cut from the product recordings, each with a push in.
export const Shot5: React.FC<{frame: number}> = ({frame}) => {
  const idx = frame < SHOT5.flashes[1] ? 0 : frame < SHOT5.flashes[2] ? 1 : 2;
  const def = SHOT5_FLASHES[idx];
  const t = prog(frame, SHOT5.flashes[idx], SHOT5.flashes[idx] + SHOT5.each);
  const s = lerp(SHOT5.push[0], SHOT5.push[1], easeOut(t));
  const c = def.win;
  const w = c.w / s;
  const win = {x: c.x + (c.w - w) / 2, y: c.y + ((c.h - c.h / s) / 2) * 0.6, w};
  const hit = frame - SHOT5.flashes[idx] < 1;
  return (
    <FullFrameCRT frame={frame}>
      <Window win={win} outW={1920} outH={1080} background={COLORS.pageBg}>
        {def.type === 'table' ? (
          <SeasonTable sourceFrame={def.sourceFrame} top={0} height={888} />
        ) : (
          <Clip src={def.src} sourceFrame={def.sourceFrame} />
        )}
      </Window>
      {hit ? <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: 0.5}} /> : null}
    </FullFrameCRT>
  );
};
