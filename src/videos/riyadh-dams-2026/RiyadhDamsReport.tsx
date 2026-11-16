import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { AUDIO, DAMS, TIMING } from "./data";
import { RainfallIntro } from "./RainfallIntro";
import { RainfallStats } from "./RainfallStats";
import { DamCapacityChart } from "./DamCapacityChart";
import { DamProfile } from "./DamProfile";
import { RainfallOutro } from "./RainfallOutro";
import { EndCard } from "./EndCard";

// Master: Intro → Stats → Chart → 13 dams (capacity order) → Outro → SIO end card (EndCard). Everything comes from data.ts.

export type RiyadhDamsReportProps = { withMusic: boolean };

const FPS = 30;
const f = (s: number) => Math.round(s * FPS);

type Part = { key: string; frames: number; node: (sec: number) => React.ReactNode; fadeIn: number };

const parts = (): Part[] => [
  { key: "intro", frames: f(TIMING.intro), fadeIn: 0, node: (s) => <RainfallIntro durationInSeconds={s} /> },
  { key: "stats", frames: f(TIMING.stats), fadeIn: TIMING.sectionFade, node: (s) => <RainfallStats durationInSeconds={s} /> },
  { key: "chart", frames: f(TIMING.chart), fadeIn: TIMING.sectionFade, node: (s) => <DamCapacityChart durationInSeconds={s} /> },
  ...DAMS.map((d, i) => ({
    key: `dam-${d.rank}`,
    frames: f(d.seconds),
    fadeIn: i === 0 ? TIMING.sectionFade : TIMING.damFade,
    node: (s: number) => <DamProfile durationInSeconds={s} dam={d} />,
  })),
  { key: "outro", frames: f(TIMING.outro), fadeIn: TIMING.sectionFade, node: (s) => <RainfallOutro durationInSeconds={s} /> },
  // SIO end card in the report's look (replaces the supplied 16:9 social outro, which BrandOutro.tsx still renders on its own)
  { key: "brand", frames: f(TIMING.endCard), fadeIn: TIMING.sectionFade, node: (s) => <EndCard durationInSeconds={s} /> },
];

export const masterFrames = () => parts().reduce((a, p) => a + p.frames - p.fadeIn, 0);

export const RiyadhDamsReport: React.FC<RiyadhDamsReportProps> = ({ withMusic }) => {
  const { durationInFrames } = useVideoConfig();
  const list = parts();
  // section starts (for the soft whoosh): where each section's crossfade begins
  const starts: number[] = [];
  let t = 0;
  list.forEach((p, i) => {
    if (i > 0) t -= p.fadeIn;
    if (["stats", "chart", "dam-1", "outro"].includes(p.key)) starts.push(t);
    t += p.frames;
  });
  const end = durationInFrames;
  const music = (fr: number) =>
    interpolate(fr, [0, 20, f(TIMING.intro + TIMING.stats), end - 60, end], [0, AUDIO.music.start, AUDIO.music.peak, AUDIO.music.peak, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const amb = (fr: number) => AUDIO.ambience.volume * interpolate(fr, [0, 20, end - 45, end], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TransitionSeries>
        {list.map((p, i) => (
          <React.Fragment key={p.key}>
            {i > 0 && <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: p.fadeIn })} />}
            <TransitionSeries.Sequence durationInFrames={p.frames}>{p.node(p.frames / FPS)}</TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>
      {withMusic && <Audio src={staticFile(AUDIO.music.src)} volume={music} />}
      <Audio src={staticFile(AUDIO.ambience.src)} loop volume={amb} />
      {starts.map((s) => (
        <Sequence key={s} from={Math.max(0, s - 6)} durationInFrames={45}>
          <Audio src={staticFile(AUDIO.transition.src)} volume={AUDIO.transition.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
