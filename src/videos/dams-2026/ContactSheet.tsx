import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";

// Dev tool: one row per clip, `cols` frames evenly spaced (with timestamps) — for choosing shots & framing.
// npx remotion still src/videos/dams-2026/entry.ts Dam-ContactSheet out.jpg --props='{"clips":[{"src":"…","duration":19}]}'
export type ContactSheetProps = { clips: { src: string; duration: number }[]; cols: number };

export const SHEET = { cellW: 384, cellH: 216, gap: 8, label: 26 };

export const ContactSheet: React.FC<ContactSheetProps> = ({ clips, cols }) => (
  <AbsoluteFill style={{ backgroundColor: "#1d1d1d", padding: SHEET.gap, display: "flex", flexDirection: "column", gap: SHEET.gap }}>
    {clips.map((c) => (
      <div key={c.src} style={{ display: "flex", gap: SHEET.gap }}>
        {Array.from({ length: cols }, (_, i) => {
          const t = (c.duration * (i + 0.5)) / cols;
          return (
            <div key={i} style={{ width: SHEET.cellW, height: SHEET.cellH + SHEET.label, position: "relative" }}>
              <OffthreadVideo src={staticFile(c.src)} trimBefore={Math.round(t * 30)} muted style={{ width: SHEET.cellW, height: SHEET.cellH, objectFit: "cover" }} />
              <div style={{ color: "#ffd84a", font: "600 18px monospace", height: SHEET.label, lineHeight: `${SHEET.label}px` }}>
                {c.src.split("/").pop()} · {t.toFixed(1)}s
              </div>
            </div>
          );
        })}
      </div>
    ))}
  </AbsoluteFill>
);
