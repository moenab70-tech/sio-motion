import React from "react";
import { Composition, Folder } from "remotion";
import { DAM_VIDEO } from "../dams-2026/config";
import { checkData, DAMS, TIMING } from "./data";
import { DamProfile } from "./DamProfile";
import { RainfallOutro } from "./RainfallOutro";
import { BrandOutro } from "./BrandOutro";
import { EndCard } from "./EndCard";
import { masterFrames, RiyadhDamsReport } from "./RiyadhDamsReport";
import { RainfallIntro } from "./RainfallIntro";
import { RainfallStats } from "./RainfallStats";
import { DamCapacityChart } from "./DamCapacityChart";
import type { SceneProps } from "./shared";

checkData();

const byDuration = ({ props }: { props: Record<string, unknown> }) => ({ durationInFrames: Math.max(1, Math.round((props as SceneProps).durationInSeconds * DAM_VIDEO.fps)) });
const scene = (id: string, component: React.FC<any>, sec: number, extra: object = {}) => (
  <>
    <Composition id={id} component={component} defaultProps={{ durationInSeconds: sec, ...extra }} calculateMetadata={byDuration} {...DAM_VIDEO} durationInFrames={1} />
    {/* transparent version: text & graphics only → ProRes 4444 alpha (render without PREVIEW=1) */}
    <Composition id={`${id}-Alpha`} component={component} defaultProps={{ durationInSeconds: sec, transparent: true, ...extra }} calculateMetadata={byDuration} {...DAM_VIDEO} durationInFrames={1} />
  </>
);

export const RiyadhDamsRoot: React.FC = () => (
  <Folder name="Riyadh-Dams-Nov2026">
    <Composition id="RD-Master" component={RiyadhDamsReport} defaultProps={{ withMusic: true }} {...DAM_VIDEO} durationInFrames={masterFrames()} />
    <Composition id="RD-Master-NoMusic" component={RiyadhDamsReport} defaultProps={{ withMusic: false }} {...DAM_VIDEO} durationInFrames={masterFrames()} />
    {scene("RD-Intro", RainfallIntro, TIMING.intro)}
    {scene("RD-Stats", RainfallStats, TIMING.stats)}
    {scene("RD-Chart", DamCapacityChart, TIMING.chart)}
    {scene("RD-Outro", RainfallOutro, TIMING.outro)}
    {scene("RD-EndCard", EndCard, TIMING.endCard)}
    <Composition id="RD-BrandOutro" component={BrandOutro} defaultProps={{ durationInSeconds: TIMING.brandOutro }} {...DAM_VIDEO} durationInFrames={TIMING.brandOutro * DAM_VIDEO.fps} />
    <Folder name="Dams">
      {DAMS.map((d) => (
        <React.Fragment key={d.rank}>{scene(`RD-Dam-${String(d.rank).padStart(2, "0")}`, DamProfile, d.seconds, { dam: d })}</React.Fragment>
      ))}
    </Folder>
  </Folder>
);
