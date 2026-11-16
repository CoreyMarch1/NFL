import React from 'react';
import {continueRender, delayRender} from 'remotion';
import {CRT as FX} from '../config';
import {hash} from './util';

// Displacement map for the RGB channel offset: red = x, green = y. Sampling it
// with opposite scales for the red and blue channels gives an offset that is
// zero in the center of the screen and strongest at the edges.
let mapUrl = '';
if (typeof document !== 'undefined') {
  const c = document.createElement('canvas');
  c.width = 256;
  c.height = 256;
  const g = c.getContext('2d')!;
  const img = g.createImageData(256, 256);
  for (let y = 0; y < 256; y++) {
    for (let x = 0; x < 256; x++) {
      const i = (y * 256 + x) * 4;
      img.data[i] = x;
      img.data[i + 1] = y;
      img.data[i + 2] = 0;
      img.data[i + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  mapUrl = c.toDataURL('image/png');
  const h = delayRender('crt-map');
  const im = new Image();
  im.onload = () => continueRender(h);
  im.onerror = () => continueRender(h);
  im.src = mapUrl;
}

let idCounter = 0;

// Wraps on-screen content: RGB offset, phosphor bloom, flicker, rolling band
// and vignette. Scanlines and noise are added in output-pixel space by
// <ScreenOverlay> so their 2 px period never gets resampled by the camera.
export const CRTContent: React.FC<{
  frame: number;
  w: number;
  h: number;
  children: React.ReactNode;
  vignette?: number;
  bloom?: number;
  rgbOffset?: number;
}> = ({frame, w, h, children, vignette = 0.35, bloom = FX.bloom, rgbOffset = FX.rgbOffset}) => {
  const id = React.useMemo(() => `crt${idCounter++}`, []);
  const flicker = 1 + (hash(frame, 1) - 0.5) * 2 * FX.flicker;
  const bandH = h * 0.32;
  const bandY = ((frame % FX.rollPeriod) / FX.rollPeriod) * (h + bandH) - bandH;
  // displacement = scale * (map - 0.5), so the edge offset is scale / 2
  const scale = rgbOffset * 2;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: w, height: h, overflow: 'hidden', background: '#000'}}>
      <svg width="0" height="0" style={{position: 'absolute'}}>
        <filter
          id={id}
          x="0"
          y="0"
          width={w}
          height={h}
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feImage href={mapUrl} x="0" y="0" width={w} height={h} preserveAspectRatio="none" result="map" />
          <feDisplacementMap in="SourceGraphic" in2="map" scale={scale} xChannelSelector="R" yChannelSelector="G" result="dR" />
          <feDisplacementMap in="SourceGraphic" in2="map" scale={-scale} xChannelSelector="R" yChannelSelector="G" result="dB" />
          <feColorMatrix in="dR" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
          <feColorMatrix in="dB" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
          <feComposite in="r" in2="g" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="rg" />
          <feComposite in="rg" in2="b" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="rgb" />
          {/* bloom: keep only bright, saturated light, blur it, screen it back */}
          <feColorMatrix
            in="rgb"
            type="matrix"
            values="1.5 0 0 0 -0.55  0 1.5 0 0 -0.55  0 0 1.5 0 -0.55  0 0 0 1 0"
            result="hot"
          />
          <feGaussianBlur in="hot" stdDeviation={FX.bloomRadius} result="glow" />
          <feColorMatrix
            in="glow"
            type="matrix"
            values={`${bloom} 0 0 0 0  0 ${bloom} 0 0 0  0 0 ${bloom} 0 0  0 0 0 1 0`}
            result="glow2"
          />
          <feBlend in="glow2" in2="rgb" mode="screen" />
        </filter>
      </svg>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: w,
          height: h,
          overflow: 'hidden',
          filter: `url(#${id}) brightness(${flicker})`,
        }}
      >
        {children}
      </div>
      {/* slow rolling brightness band */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: bandY,
          width: w,
          height: bandH,
          background: `linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,${FX.rollStrength}) 50%, rgba(255,255,255,0))`,
          mixBlendMode: 'screen',
        }}
      />
      {vignette > 0 ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,${vignette}) 100%)`,
          }}
        />
      ) : null}
    </div>
  );
};

// Scanlines (2 px period) and light noise, drawn in final output pixels.
export const ScreenOverlay: React.FC<{
  frame: number;
  x: number;
  y: number;
  w: number;
  h: number;
  clipPath?: string;
}> = ({frame, x, y, w, h, clipPath}) => {
  const a = FX.scanlineAlpha;
  // snap to even pixels so the scanline phase is stable while the camera moves
  const top = Math.floor(y / 2) * 2;
  const dy = y - top;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, clipPath, overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: -dy,
          width: w,
          height: h + 4,
          backgroundImage: `repeating-linear-gradient(to bottom, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 1px, rgba(0,0,0,${a}) 1px, rgba(0,0,0,${a}) 2px)`,
        }}
      />
      <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'overlay', opacity: FX.noise * 4}}>
        <filter id={`noise${Math.round(x)}`} x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="1" seed={frame + 1} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width={w} height={h} filter={`url(#noise${Math.round(x)})`} />
      </svg>
    </div>
  );
};

// Full-frame CRT for the shots where the camera is pushed in past the bezel:
// scanlines and bloom stay, curvature is dropped, vignette is light.
export const FullFrameCRT: React.FC<{frame: number; children: React.ReactNode}> = ({frame, children}) => (
  <div style={{position: 'absolute', inset: 0, background: '#000'}}>
    <CRTContent frame={frame} w={1920} h={1080} vignette={0.22}>
      {children}
    </CRTContent>
    <ScreenOverlay frame={frame} x={0} y={0} w={1920} h={1080} />
  </div>
);
