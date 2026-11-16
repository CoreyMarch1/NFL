import React from 'react';
import {Img, staticFile} from 'remotion';
import {ASSETS, CABINET, COLORS, LOGO} from '../config';
import {CRTContent, ScreenOverlay} from './CRT';

// Camera: framePoint = worldPoint * s + (tx, ty)
export type Cam = {s: number; tx: number; ty: number};
export const camLookAt = (s: number, wx: number, wy: number, fx = 960, fy = 540): Cam => ({
  s,
  tx: fx - wx * s,
  ty: fy - wy * s,
});
export const camLerp = (a: Cam, b: Cam, t: number): Cam => ({
  s: a.s + (b.s - a.s) * t,
  tx: a.tx + (b.tx - a.tx) * t,
  ty: a.ty + (b.ty - a.ty) * t,
});
export const SCREEN_CENTER = {
  x: CABINET.screen.x + CABINET.screen.w / 2,
  y: CABINET.screen.y + CABINET.screen.h / 2,
};

// Rounded rectangle whose sides bulge outward slightly, like CRT glass.
export const screenPath = (w: number, h: number, r: number, b: number) =>
  `M ${r} 0 Q ${w / 2} ${-b} ${w - r} 0 Q ${w} 0 ${w} ${r} Q ${w + b} ${h / 2} ${w} ${h - r} ` +
  `Q ${w} ${h} ${w - r} ${h} Q ${w / 2} ${h + b} ${r} ${h} Q 0 ${h} 0 ${h - r} Q ${-b} ${h / 2} 0 ${r} Q 0 0 ${r} 0 Z`;

// The neon logo, masked to its rounded neon frame (drops the scenic backdrop).
export const MaskedLogo: React.FC<{height: number; style?: React.CSSProperties}> = ({height, style}) => {
  const f = LOGO.neonFrame;
  const s = height / f.h;
  return (
    <div
      style={{
        position: 'relative',
        width: f.w * s,
        height: f.h * s,
        borderRadius: f.r * s,
        overflow: 'hidden',
        ...style,
      }}
    >
      <Img
        src={staticFile(ASSETS.logo)}
        style={{position: 'absolute', left: -f.x * s, top: -f.y * s, width: LOGO.nat.w * s, height: LOGO.nat.h * s}}
      />
    </div>
  );
};

const Stripes: React.FC<{left: number; flip?: boolean; on: number}> = ({left, flip, on}) => (
  <div
    style={{
      position: 'absolute',
      left,
      top: 18,
      width: 250,
      height: CABINET.marquee.h - 36,
      opacity: 0.25 + 0.75 * on,
      transform: flip ? 'scaleX(-1)' : undefined,
      backgroundImage: `repeating-linear-gradient(115deg, ${COLORS.green} 0 14px, transparent 14px 30px, ${COLORS.purple} 30px 44px, transparent 44px 60px)`,
      WebkitMaskImage: 'linear-gradient(to right, rgba(0,0,0,0.9), rgba(0,0,0,0))',
      maskImage: 'linear-gradient(to right, rgba(0,0,0,0.9), rgba(0,0,0,0))',
    }}
  />
);

export const Cabinet: React.FC<{
  frame: number;
  cam: Cam;
  lit?: number; // 0..1 ambient visibility of the cabinet body
  marquee?: number; // 0..1 marquee backlight
  screenGlow?: number; // 0..1 glow spilling from the screen onto the bezel
  children: React.ReactNode;
}> = ({frame, cam, lit = 1, marquee = 1, screenGlow = 1, children}) => {
  const {body, marquee: mq, bezel, screen, screenRadius, screenBulge} = CABINET;
  const path = screenPath(screen.w, screen.h, screenRadius, screenBulge);
  const framePath = screenPath(screen.w * cam.s, screen.h * cam.s, screenRadius * cam.s, screenBulge * cam.s);
  return (
    <div style={{position: 'absolute', inset: 0, background: '#000', overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 1920,
          height: 1080,
          transformOrigin: '0 0',
          transform: `translate(${cam.tx}px, ${cam.ty}px) scale(${cam.s})`,
        }}
      >
        <div style={{position: 'absolute', inset: 0, opacity: lit}}>
          {/* the dark room: only a faint pool of light behind the cabinet */}
          <div
            style={{
              position: 'absolute',
              left: -400,
              top: -200,
              width: 2720,
              height: 1500,
              background:
                'radial-gradient(ellipse 50% 55% at 50% 52%, rgba(64,30,120,0.30), rgba(10,40,20,0.10) 55%, rgba(0,0,0,0) 80%)',
            }}
          />
          {/* cabinet body */}
          <div
            style={{
              position: 'absolute',
              left: body.x,
              top: body.y,
              width: body.w,
              height: body.h,
              background: `linear-gradient(to right, #04050b, ${COLORS.cabinet} 6%, #0d1022 50%, ${COLORS.cabinet} 94%, #04050b)`,
              borderLeft: `7px solid ${COLORS.purple}`,
              borderRight: `7px solid ${COLORS.purple}`,
              boxShadow: `0 0 50px rgba(160,32,240,0.45), inset 0 0 90px rgba(0,0,0,0.9)`,
            }}
          />
          {/* marquee */}
          <div
            style={{
              position: 'absolute',
              left: mq.x,
              top: mq.y,
              width: mq.w,
              height: mq.h,
              borderRadius: 10,
              border: '5px solid #02030a',
              background: `linear-gradient(to bottom, #0a1420, ${COLORS.logoBg} 60%, #0c0a1c)`,
              boxShadow: `0 0 ${70 * marquee}px rgba(57,255,20,${0.3 * marquee}), 0 ${24 * marquee}px ${90 * marquee}px rgba(160,32,240,${0.4 * marquee}), inset 0 0 40px rgba(0,0,0,0.8)`,
              overflow: 'hidden',
            }}
          >
            <Stripes left={0} on={marquee} />
            <Stripes left={mq.w - 260} flip on={marquee} />
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: 0.12 + 0.88 * marquee,
                filter: `brightness(${0.5 + 0.6 * marquee})`,
              }}
            >
              <MaskedLogo height={mq.h - 24} style={{boxShadow: `0 0 ${40 * marquee}px rgba(57,255,20,0.5)`}} />
            </div>
          </div>
          {/* speaker slats */}
          <div
            style={{
              position: 'absolute',
              left: mq.x + 300,
              top: mq.y + mq.h + 14,
              width: mq.w - 600,
              height: 16,
              backgroundImage: 'repeating-linear-gradient(to right, #1a1d33 0 18px, transparent 18px 30px)',
              opacity: 0.8,
            }}
          />
          {/* bezel */}
          <div
            style={{
              position: 'absolute',
              left: bezel.x,
              top: bezel.y,
              width: bezel.w,
              height: bezel.h,
              borderRadius: 26,
              background: `linear-gradient(to bottom, #0b0d18, ${COLORS.bezel} 30%, #020308)`,
              border: '3px solid #161a2c',
              boxShadow: 'inset 0 0 0 10px #05060c, inset 0 0 60px rgba(0,0,0,1), 0 10px 40px rgba(0,0,0,0.9)',
            }}
          />
          {/* control panel edge */}
          <div
            style={{
              position: 'absolute',
              left: body.x + 7,
              top: bezel.y + bezel.h + 14,
              width: body.w - 14,
              height: 200,
              background: 'linear-gradient(to bottom, #171a30, #0b0d1a 40%, #05060c)',
              borderTop: '3px solid #2a2f52',
            }}
          >
            {[COLORS.green, COLORS.purple, COLORS.orange].map((c, i) => (
              <div
                key={c}
                style={{
                  position: 'absolute',
                  left: 700 + i * 74,
                  top: 16,
                  width: 46,
                  height: 22,
                  borderRadius: '50%',
                  background: c,
                  boxShadow: `0 0 18px ${c}, inset 0 -6px 8px rgba(0,0,0,0.45)`,
                }}
              />
            ))}
          </div>
        </div>

        {/* glow spilling from the tube onto the bezel */}
        <div
          style={{
            position: 'absolute',
            left: screen.x,
            top: screen.y,
            width: screen.w,
            height: screen.h,
            borderRadius: screenRadius,
            opacity: screenGlow,
            boxShadow:
              '-26px -10px 70px rgba(57,255,20,0.26), 26px 12px 80px rgba(160,32,240,0.34), 0 0 26px rgba(120,220,255,0.18)',
          }}
        />
        {/* the tube */}
        <div
          style={{
            position: 'absolute',
            left: screen.x,
            top: screen.y,
            width: screen.w,
            height: screen.h,
            clipPath: `path('${path}')`,
            background: '#000',
          }}
        >
          <CRTContent frame={frame} w={screen.w} h={screen.h} vignette={0.6}>
            {children}
          </CRTContent>
          {/* glass: corner falloff and a soft diagonal reflection sell the curvature */}
          <div
            style={{
              position: 'absolute',
              inset: -screenBulge,
              background:
                'radial-gradient(ellipse 72% 72% at 50% 50%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.55) 100%), linear-gradient(118deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.012) 22%, rgba(255,255,255,0) 40%)',
              boxShadow: 'inset 0 0 26px rgba(0,0,0,0.9)',
            }}
          />
        </div>
      </div>
      <ScreenOverlay
        frame={frame}
        x={screen.x * cam.s + cam.tx}
        y={screen.y * cam.s + cam.ty}
        w={screen.w * cam.s}
        h={screen.h * cam.s}
        clipPath={`path('${framePath}')`}
      />
    </div>
  );
};
