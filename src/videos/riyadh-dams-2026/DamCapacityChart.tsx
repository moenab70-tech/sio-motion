import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILIES } from "../../lib/fonts";
import { EASE, ramp } from "../../lib/motion";
import { formatNumber } from "../../lib/numbers";
import { DAM_LAYOUT as L, DAM_STYLE as S } from "../dams-2026/config";
import { CHART_DAMS, REPORT, SCENE_MEDIA, type Dam, type SceneMedia } from "./data";
import { Footage, HeaderLogos, Quantity, type SceneProps } from "./shared";

export type DamCapacityChartProps = SceneProps & { title?: string; dams?: Dam[]; media?: SceneMedia };

const TRACK = 1080 - 2 * L.safeSide; // full bar width = the largest value (linear scale from 0)
const ROW_GAP = 8; // frames between rows
const GROW = 40;

/** Scene 3 — horizontal bar chart, bars grow right → left (RTL) from zero, true linear scale, max highlighted. */
export const DamCapacityChart: React.FC<DamCapacityChartProps> = ({ title = REPORT.chartTitle, dams = CHART_DAMS, media = SCENE_MEDIA.chart, transparent, showLogos = true }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const out = 1 - ramp(frame, durationInFrames - 14, 14, EASE.in);
  const max = Math.max(...dams.map((d) => d.storageCapacity));
  const titleT = ramp(frame, 6, 22);

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {!transparent && <Footage media={media} frames={durationInFrames} dim={0.62} blur={6} />}
      {showLogos && <HeaderLogos />}

      <div style={{ position: "absolute", right: L.safeSide, left: L.safeSide, top: L.safeTop + L.logoCircle + 130, opacity: out }}>
        <div style={{ opacity: titleT, transform: `translateY(${(1 - titleT) * 24}px)` }}>
          <div style={{ width: 110, height: 8, backgroundColor: "#0071B8", borderRadius: 4, marginBottom: 24 }} />
          {/* balanced 2 lines: split before «من حيث» when present */}
          <div style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: 800, fontSize: 72, lineHeight: 1.4, color: "#fff" }}>
            {title.includes(" من حيث") ? (
              <>
                {title.split(" من حيث")[0]}
                <br />
                <span style={{ fontSize: "0.78em", fontWeight: 700 }}>من حيث{title.split(" من حيث")[1]}</span>
              </>
            ) : (
              title
            )}
          </div>
        </div>

        <div style={{ marginTop: 90, display: "flex", flexDirection: "column", gap: 62 }}>
          {dams.map((d, i) => {
            const top = d.storageCapacity === max;
            const enter = ramp(frame, 22 + i * ROW_GAP, 18);
            const g = ramp(frame, 26 + i * ROW_GAP, GROW, EASE.count);
            const w = (d.storageCapacity / max) * TRACK * g;
            return (
              <div key={d.rank} style={{ opacity: enter }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12, color: "#fff" }}>
                  <span style={{ fontFamily: FONT_FAMILIES.NotoKufiArabic, fontWeight: top ? 800 : 700, fontSize: top ? 50 : 44 }}>سد {d.name}</span>
                  <span style={{ fontFamily: FONT_FAMILIES.IBMPlexSansArabic, fontWeight: 700, fontSize: top ? 50 : 42 }}>
                    <Quantity text={formatNumber(Math.round(d.storageCapacity * g), { digits: "latin" })} unit="م³" unitScale={0.62} />
                  </span>
                </div>
                {/* track + bar (bar anchored right = zero) */}
                <div style={{ position: "relative", height: top ? 58 : 42, width: TRACK, backgroundColor: "rgba(255,255,255,0.10)", borderRadius: 4 }}>
                  <div
                    style={{
                      position: "absolute",
                      right: 0,
                      top: 0,
                      bottom: 0,
                      width: w,
                      borderRadius: 4,
                      background: top ? "linear-gradient(to left, #0071B8, #2AA3E8)" : "rgba(180,214,240,0.78)",
                      boxShadow: top ? "0 0 0 2px rgba(255,255,255,0.35) inset" : undefined,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
