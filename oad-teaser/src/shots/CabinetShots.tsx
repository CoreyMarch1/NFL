import React from 'react';
import {Img, staticFile} from 'remotion';
import {ASSETS, BEAT, CABINET, COLORS, COPY, CUTS, HOME, LOGO, SEASON_TABLE, SHOT1, SHOT2, SHOT6} from '../config';
import {Cabinet, SCREEN_CENTER, camLerp, camLookAt} from '../components/Cabinet';
import {Box, Clip, PIXEL_FONT, SeasonTable, Window, easeInOut, easeOut, hash, lerp, prog, tableX} from '../components/util';

const SW = CABINET.screen.w;
const SH = CABINET.screen.h;

// ----------------------------- SHOT 1: INSERT COIN ---------------------------
export const Shot1: React.FC<{frame: number}> = ({frame}) => {
  const [p0, p1] = SHOT1.powerOn;
  const on = frame >= p0;
  // 12..14 a white line grows sideways, 14..20 it opens vertically
  const lineW = lerp(0.12, 1, easeOut(prog(frame, p0, p0 + 3)));
  const open = frame < p0 + 2 ? 0.006 : lerp(0.006, 1, easeOut(prog(frame, p0 + 2, p1)));
  const white = frame < p0 + 2 ? 1 : 1 - prog(frame, p0 + 2, p1 + 1);
  const overshoot = 1 + 0.7 * (1 - prog(frame, p1 - 2, p1 + 6)) * (frame >= p0 ? 1 : 0);
  const lit = prog(frame, p0 + 2, p1 + 4);
  // marquee tube flickers on
  const mt = frame - SHOT1.marqueeOn;
  const pattern = [0.8, 0.1, 0.9, 0.25, 0, 1, 0.9, 0.3, 1, 1, 0.6, 1];
  const marquee = mt < 0 ? 0 : mt < pattern.length ? pattern[mt] : 1 - 0.04 * hash(frame, 7);
  const push = lerp(SHOT1.pushScale[0], SHOT1.pushScale[1], prog(frame, p1, CUTS.shot2));
  const cam = camLookAt(push, SHOT1.pushAnchor.x, SHOT1.pushAnchor.y, SHOT1.pushAnchor.x, SHOT1.pushAnchor.y);
  return (
    <Cabinet frame={frame} cam={cam} lit={lit} marquee={marquee} screenGlow={on ? Math.min(1, lit + 0.3) : 0}>
      {on ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            transform: `scale(${lineW}, ${open})`,
            filter: `brightness(${overshoot})`,
          }}
        >
          <Window win={HOME.window} outW={SW} outH={SH} background={COLORS.pageBg}>
            <Clip src={ASSETS.home} sourceFrame={SHOT1.clipStart + Math.max(0, frame - p1)} />
          </Window>
          <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: white}} />
        </div>
      ) : null}
    </Cabinet>
  );
};

// -------------------------- SHOT 2: CHOOSE YOUR GOLFER -----------------------
// The Season Roadmap table on the CRT: one golfer per event. Rows wipe on,
// then a selection cursor hops between the golfer dropdowns and locks.
export const Shot2: React.FC<{frame: number}> = ({frame}) => {
  const t = prog(frame, CUTS.shot2, CUTS.shot3);
  const cam = camLookAt(lerp(SHOT2.cameraScale[0], SHOT2.cameraScale[1], t), SCREEN_CENTER.x, SCREEN_CENTER.y);
  const T = SEASON_TABLE;
  const top = T.shot2Top;
  const srcH = (SH * T.width) / SW;

  const [m1, m2] = SHOT2.cursorMoves;
  const row = SHOT2.cursorRows[frame < m1 ? 0 : frame < m2 ? 1 : 2];
  const locked = frame >= SHOT2.lockAt;
  const cursorOn = frame >= SHOT2.rowsFrom + 8;
  const blinkOn = locked || (frame - CUTS.shot2) % SHOT2.blinkPeriod < SHOT2.blinkPeriod / 2 + 1;
  const lockFlash = locked && frame < SHOT2.lockAt + SHOT2.lockFlashFrames;
  const beat = Math.pow(1 - ((frame - CUTS.shot2) % BEAT) / BEAT, 2.2);
  const rowY = (i: number) => T.rowTop + i * T.rowPitch - top;
  const sel = {x: tableX(T.selector.x) - 8, y: rowY(row) + T.selector.dy - 8, w: T.selector.w + 16, h: T.selector.h + 16};
  const color = locked ? COLORS.green : '#FFFFFF';
  const glow = locked ? '57,255,20' : '34,211,238';

  return (
    <Cabinet frame={frame} cam={cam} marquee={1}>
      <Window win={{x: 0, y: 0, w: T.width}} outW={SW} outH={SH} background={COLORS.pageBg}>
        <SeasonTable sourceFrame={SHOT2.srcFrame} top={top} height={srcH} />
        {/* rows wipe on left to right, one after another */}
        {Array.from({length: T.rows + 1}).map((_, i) => {
          const start = SHOT2.rowsFrom + Math.min(i, T.rows - 1) * SHOT2.rowsStagger;
          const p = easeOut(prog(frame, start, start + SHOT2.rowsDuration));
          if (p >= 1) return null;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: 2 + (T.width - 2) * p,
                top: rowY(i) + 1,
                width: (T.width - 2) * (1 - p) + 2,
                height: T.rowPitch,
                background: T.rowBg,
                borderLeft: p > 0 ? `4px solid ${COLORS.green}` : undefined,
              }}
            />
          );
        })}
        {/* selected row tint + cursor on the golfer dropdown */}
        {cursorOn ? (
          <div
            style={{
              position: 'absolute',
              left: 2,
              top: rowY(row) + 1,
              width: T.width,
              height: T.rowPitch - 1,
              background: `rgba(${glow},${0.1 + 0.06 * beat})`,
            }}
          />
        ) : null}
        {cursorOn && blinkOn ? (
          <Box
            r={sel}
            style={{
              border: `4px solid ${color}`,
              borderRadius: 6,
              boxShadow: `0 0 ${14 + 10 * beat}px rgba(${glow},1), 0 0 ${34 + 20 * beat}px rgba(${glow},0.6), inset 0 0 10px rgba(${glow},0.45)`,
            }}
          />
        ) : null}
        {lockFlash ? <div style={{position: 'absolute', left: -50, top: -50, width: 1000, height: 800, background: '#fff', opacity: 0.85}} /> : null}
      </Window>
    </Cabinet>
  );
};

// ------------------------------ SHOT 6: END CARD -----------------------------
export const Shot6: React.FC<{frame: number}> = ({frame}) => {
  const [a, b] = SHOT6.pullBack;
  const close = camLookAt(SHOT6.closeScale, SCREEN_CENTER.x, SCREEN_CENTER.y);
  const wide = SHOT6.wideCam;
  const anchorY = 100;
  const drift = camLookAt(SHOT6.driftScale, 960, anchorY, 960 * wide.s + wide.tx, anchorY * wide.s + wide.ty);
  const cam =
    frame < b
      ? camLerp(close, wide, easeInOut(prog(frame, a, b)))
      : camLerp(wide, drift, easeOut(prog(frame, b, SHOT6.holdFrom)));
  const {on1, off, on2} = SHOT6.blink;
  const textOn = (frame >= on1 && frame < off) || frame >= on2;
  const lw = LOGO.endCardWidth;
  const lh = (lw * LOGO.nat.h) / LOGO.nat.w;
  const feather =
    'linear-gradient(to right, transparent 0%, #000 11%, #000 89%, transparent 100%), linear-gradient(to bottom, transparent 0%, #000 14%, #000 95%, transparent 100%)';
  return (
    <Cabinet frame={frame} cam={cam} marquee={1 - 0.04 * hash(frame, 7)}>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 38%, #0c1a14, ${COLORS.logoBg} 70%)`}} />
      <Img
        src={staticFile(ASSETS.logo)}
        style={{
          position: 'absolute',
          left: (SW - lw) / 2,
          top: 14,
          width: lw,
          height: lh,
          WebkitMaskImage: feather,
          maskImage: feather,
          WebkitMaskComposite: 'source-in',
          maskComposite: 'intersect',
        }}
      />
      {/* extra glow carries the logo instead of upscaling it */}
      <div
        style={{
          position: 'absolute',
          left: (SW - lw) / 2 + lw * 0.13,
          top: 14 + lh * 0.2,
          width: lw * 0.74,
          height: lh * 0.64,
          borderRadius: 40,
          boxShadow: '0 0 90px rgba(57,255,20,0.35), 0 0 160px rgba(160,32,240,0.3)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          width: SW,
          top: 462,
          textAlign: 'center',
          fontFamily: PIXEL_FONT,
          fontSize: 34,
          lineHeight: '40px',
          color: COLORS.green,
          textShadow: `3px 3px 0 ${COLORS.purple}, 0 0 22px rgba(57,255,20,0.8)`,
          whiteSpace: 'pre',
          opacity: textOn ? 1 : 0,
        }}
      >
        {COPY.endCard}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 0,
          width: SW,
          top: 608,
          textAlign: 'center',
          fontFamily: PIXEL_FONT,
          fontSize: 16,
          color: COLORS.white,
          whiteSpace: 'pre',
          textShadow: '0 0 10px rgba(34,211,238,0.7)',
        }}
      >
        {`${COPY.site}   ${COPY.handle}`}
      </div>
    </Cabinet>
  );
};
