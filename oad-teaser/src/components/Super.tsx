import React from 'react';
import {COLORS, SUPERS, SUPER_STYLE, SuperDef} from '../config';
import {PIXEL_FONT} from './util';

// Green fill, purple hard drop shadow, thin dark outline around both.
const shadow = () => {
  const o = SUPER_STYLE.outline;
  const d = SUPER_STYLE.shadowOffset;
  const ring = (cx: number, cy: number, r: number, c: string) => {
    const out: string[] = [];
    for (let dx = -r; dx <= r; dx++) {
      for (let dy = -r; dy <= r; dy++) {
        if (dx === 0 && dy === 0) continue;
        if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue;
        out.push(`${cx + dx}px ${cy + dy}px 0 ${c}`);
      }
    }
    return out;
  };
  const extrude: string[] = [];
  for (let i = 1; i <= d; i++) extrude.push(`${i}px ${i}px 0 ${COLORS.purple}`);
  // first entries paint on top: purple extrusion, then the dark outline around
  // the fill and around the shadow
  return [
    ...extrude,
    ...ring(0, 0, o, COLORS.superOutline),
    ...ring(0, 0, o - 1, COLORS.superOutline),
    ...ring(d, d, o, COLORS.superOutline),
    ...ring(d, d, o - 1, COLORS.superOutline),
  ].join(', ');
};

const One: React.FC<{frame: number; def: SuperDef}> = ({frame, def}) => {
  const t = frame - def.from;
  let text = def.text;
  let flash = false;
  if (def.mode === 'type') {
    const n = Math.ceil((def.text.length * Math.min(t + 1, SUPER_STYLE.typeFrames)) / SUPER_STYLE.typeFrames);
    text = def.text.slice(0, n);
  } else {
    flash = t < SUPER_STYLE.flashFrames;
  }
  return (
    <>
    <div
      style={{
        position: 'absolute',
        left: 0,
        width: 1920,
        top: def.y - def.size * 2.4,
        height: def.size * 4.8,
        background: `linear-gradient(to bottom, rgba(0,0,0,0), rgba(2,3,10,${SUPER_STYLE.scrim}) 38%, rgba(2,3,10,${SUPER_STYLE.scrim}) 62%, rgba(0,0,0,0))`,
      }}
    />
    <div
      style={{
        position: 'absolute',
        left: 1920 * SUPER_STYLE.safeMargin,
        width: 1920 * (1 - 2 * SUPER_STYLE.safeMargin),
        top: def.y - def.size / 2,
        height: def.size,
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      {/* fixed-width box so typed-on text grows from the left without re-centering */}
      <div
        style={{
          fontFamily: PIXEL_FONT,
          fontSize: def.size,
          lineHeight: `${def.size}px`,
          width: def.text.length * def.size,
          whiteSpace: 'pre',
          textAlign: 'left',
          color: flash ? '#FFFFFF' : COLORS.green,
          textShadow: flash ? `0 0 30px #fff, 0 0 60px #fff` : shadow(),
        }}
      >
        {text}
      </div>
    </div>
    </>
  );
};

export const Supers: React.FC<{frame: number}> = ({frame}) => (
  <>
    {SUPERS.filter((s) => frame >= s.from && frame < s.to).map((s) => (
      <One key={s.text} frame={frame} def={s} />
    ))}
  </>
);
