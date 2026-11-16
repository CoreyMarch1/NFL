import React from 'react';
import {Img, staticFile} from 'remotion';
import {ASSETS, BEAT, CABINET, CHAR_SELECT, COLORS, COPY, CUTS, HOME, LOGO, SHOT1, SHOT2, SHOT6} from '../config';
import {Cabinet, SCREEN_CENTER, camLerp, camLookAt} from '../components/Cabinet';
import {Box, Clip, PIXEL_FONT, Window, easeInOut, easeOut, hash, lerp, prog} from '../components/util';

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
export const Shot2: React.FC<{frame: number}> = ({frame}) => {
  const t = prog(frame, CUTS.shot2, CUTS.shot3);
  const cam = camLookAt(lerp(SHOT2.cameraScale[0], SHOT2.cameraScale[1], t), SCREEN_CENTER.x, SCREEN_CENTER.y);
  const s = CHAR_SELECT.stageScale;
  const win = {x: (1920 - SW / s) / 2, y: -CHAR_SELECT.stageTop / s, w: SW / s};

  // selection cursor: left -> right at 105 -> left at 120 -> lock at 135
  const [m1, m2] = SHOT2.cursorMoves;
  const sel = frame >= m1 && frame < m2 ? 1 : 0;
  const locked = frame >= SHOT2.lockAt;
  const blinkOn = locked || (frame - CUTS.shot2) % SHOT2.blinkPeriod < SHOT2.blinkPeriod / 2 + 1;
  const lockFlash = locked && frame < SHOT2.lockAt + SHOT2.lockFlashFrames;
  const card = CHAR_SELECT.cards[sel];

  // INSERT COIN pulses on every beat
  const sinceBeat = (frame - CUTS.shot2) % BEAT;
  const pulse = Math.pow(1 - sinceBeat / BEAT, 2.2);
  const b = CHAR_SELECT.button;

  return (
    <Cabinet frame={frame} cam={cam} marquee={1}>
      <Window win={win} outW={SW} outH={SH} background={COLORS.charSelectBg}>
        <Img
          src={staticFile(ASSETS.charSelect)}
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: 1920,
            height: 1004,
            WebkitMaskImage: 'linear-gradient(to bottom, #000 0%, #000 92.5%, transparent 100%)',
            maskImage: 'linear-gradient(to bottom, #000 0%, #000 92.5%, transparent 100%)',
          }}
        />
        {/* stat bars: gray covers shrink to the right to reveal the painted fill */}
        {CHAR_SELECT.bars.map((bar, i) => {
          const start = SHOT2.barsFrom + i * SHOT2.barsStagger;
          const p = easeOut(prog(frame, start, start + SHOT2.barsDuration));
          if (p >= 1) return null;
          const x = lerp(bar.x0, bar.x1, p);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: x,
                top: bar.y,
                width: bar.x1 - x + 1,
                height: bar.h,
                background: COLORS.barEmpty,
                borderRadius: bar.round ? '0 9px 9px 0' : 0,
              }}
            />
          );
        })}
        {/* button pulse: a scaled, brightened copy of the button region */}
        <Box
          r={b}
          style={{
            overflow: 'hidden',
            transform: `scale(${1 + 0.045 * pulse})`,
            filter: `brightness(${1 + 0.35 * pulse})`,
            borderRadius: 26,
            boxShadow: `0 0 ${50 * pulse}px rgba(255,138,31,${0.8 * pulse})`,
          }}
        >
          <Img
            src={staticFile(ASSETS.charSelect)}
            style={{position: 'absolute', left: -b.x, top: -b.y, width: 1920, height: 1004}}
          />
        </Box>
        {/* selection outline */}
        {blinkOn ? (
          <Box
            r={{x: card.x - 12, y: card.y - 12, w: card.w + 24, h: card.h + 24}}
            style={{
              border: `9px solid ${locked ? COLORS.green : '#FFFFFF'}`,
              borderRadius: 22,
              boxShadow: locked
                ? `0 0 40px ${COLORS.green}, 0 0 90px rgba(57,255,20,0.6), inset 0 0 26px rgba(57,255,20,0.5)`
                : `0 0 34px ${COLORS.cyan}, 0 0 70px rgba(34,211,238,0.55), inset 0 0 20px rgba(34,211,238,0.5)`,
            }}
          />
        ) : null}
        {lockFlash ? <div style={{position: 'absolute', left: -200, top: -200, width: 2400, height: 1500, background: '#fff', opacity: 0.85}} /> : null}
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
