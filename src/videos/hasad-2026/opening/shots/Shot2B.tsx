// 2B v2 — Perseverance time-lapse (top-down, locked camera, 1:1 desk plate). Real paper texture sheets land one
// after another; each carries its own Grease Pencil drawing (Blender): a crossed-out attempt, an erased attempt,
// a better one, and the final drawing traced in gold. Light travels from night-blue to dawn.
import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { SHEET_LAND } from "../linework";
import { Plate } from "./Shot1B";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.2, 0.9, 0.3, 1);
const POS = [{ x: 520, y: 250, rot: -9 }, { x: 820, y: 300, rot: 6 }, { x: 640, y: 420, rot: -3 }, { x: 700, y: 330, rot: 1.5 }];

export const Shot2B: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const dawn = interpolate(f, [40, len], [0, 1], clamp);
  const sweep = interpolate(f, [0, len], [-0.4, 1.2], clamp);
  return (
    <AbsoluteFill style={{ background: "#0A0705", overflow: "hidden" }}>
      <Plate src="media/opening/assets/P-2B-desk.png" />
      {POS.map((p, i) => {
        const lf = f - SHEET_LAND[i];
        if (lf < -6) return null;
        const land = interpolate(lf, [-6, 6], [0, 1], { ...clamp, easing: ease });
        const erase = i === 1 ? interpolate(f, [48, 58], [0, 1], clamp) : 0;
        return (
          <div key={i} style={{ position: "absolute", left: p.x + (1 - land) * 120, top: p.y - (1 - land) * 160, width: 620, height: 440,
            transform: `rotate(${p.rot + (1 - land) * 10}deg)`, opacity: Math.min(1, land * 1.6),
            boxShadow: `${14 - 6 * land}px ${22 - 8 * land}px ${30 - 10 * land}px rgba(0,0,0,0.5)` }}>
            <Img src={staticFile("media/opening/layers/paper-sheet.png")} style={{ width: 620, height: 440, display: "block" }} />
            <Img src={staticFile(`media/opening/lines/2B-sheet${i}/f_${String(Math.min(102, Math.max(1, f + 1))).padStart(4, "0")}.png`)}
              style={{ position: "absolute", inset: 0, width: 620, height: 440, mixBlendMode: i === 3 ? "normal" : "multiply" }} />
            {i === 1 && erase > 0 && (
              <svg width={620} height={440} style={{ position: "absolute", inset: 0 }}>
                {Array.from({ length: 22 }).map((_, k) => <circle key={k} cx={200 + random(`e${k}`) * 230} cy={250 + random(`f${k}`) * 100} r={1.5 + random(`g${k}`) * 2.5} fill="#8E867C" opacity={Math.min(1, erase * 2) * 0.75} />)}
              </svg>
            )}
          </div>
        );
      })}
      <AbsoluteFill style={{ mixBlendMode: "soft-light", background: `linear-gradient(110deg, transparent ${sweep * 100 - 25}%, rgba(${Math.round(120 + 120 * dawn)},${Math.round(150 + 50 * dawn)},${Math.round(220 - 120 * dawn)},0.55) ${sweep * 100}%, transparent ${sweep * 100 + 25}%)` }} />
      <AbsoluteFill style={{ background: `rgba(255,190,110,${dawn * 0.16})`, mixBlendMode: "screen" }} />
    </AbsoluteFill>
  );
};
