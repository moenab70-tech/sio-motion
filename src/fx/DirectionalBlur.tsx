import React, { useId } from "react";

/**
 * Real directional motion blur (SVG Gaussian blur with separate X/Y amounts).
 * Blurs colour AND alpha, so it stays correct on transparent backgrounds.
 * Drive x/y from element velocity (px/frame) — see velocityBlur().
 */
export const DirectionalBlur: React.FC<{ x: number; y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, children, style }) => {
  const id = `dblur-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  if (x < 0.05 && y < 0.05) return <div style={style}>{children}</div>;
  return (
    <>
      <svg width="0" height="0" style={{ position: "absolute" }} aria-hidden>
        <filter id={id} x="-50%" y="-50%" width="200%" height="200%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation={`${x.toFixed(2)} ${y.toFixed(2)}`} />
        </filter>
      </svg>
      <div style={{ ...style, filter: `url(#${id})` }}>{children}</div>
    </>
  );
};

/** Converts a per-frame displacement (px) into a blur amount, like a 180° film shutter. */
export const velocityBlur = (deltaPx: number, intensity: number, enabled = true) =>
  enabled ? Math.min(40, Math.abs(deltaPx) * 0.5 * (0.4 + intensity * 1.2)) : 0;
