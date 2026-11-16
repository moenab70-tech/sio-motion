// Preview: all five templates in sequence over a placeholder background.
import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from "remotion";
import { VIDEO } from "../config/brand";
import * as D from "../config/defaults";
import { StatCounter } from "../templates/StatCounter";
import { CinematicTitle } from "../templates/CinematicTitle";
import { LowerThird } from "../templates/LowerThird";
import { InfographicCards } from "../templates/InfographicCards";
import { ProjectCard } from "../templates/ProjectCard";
import { SectionTransition } from "../templates/SectionTransition";

export type ShowreelProps = { showBackground: boolean };

const sec = (s: number) => Math.round(s * VIDEO.fps);

// Each section; transitions overlap the cut between sections (cut = transition midpoint).
const sections = [
  { el: <CinematicTitle {...D.titleWithLogo} />, d: D.cinematicTitle.durationInSeconds },
  { el: <StatCounter {...D.statRow} />, d: D.statRow.durationInSeconds, transition: D.transitionPanels },
  { el: <InfographicCards {...D.infographic} />, d: D.infographic.durationInSeconds, transition: D.transitionSweep },
  { el: <ProjectCard {...D.projectWithLogo} />, d: D.projectCard.durationInSeconds, transition: D.transitionShutter },
  { el: <><StatCounter {...D.statSingle} verticalPosition="center" /></>, d: D.statSingle.durationInSeconds, transition: D.transitionSweep },
  { el: <LowerThird {...D.lowerThirdWithLogo} />, d: D.lowerThird.durationInSeconds, transition: D.transitionPanels },
];

export const showreelDuration = sections.reduce((a, x) => a + sec(x.d), 0);

const Background: React.FC = () => {
  const f = useCurrentFrame();
  const x = interpolate(f, [0, showreelDuration], [30, 70]);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(circle at ${x}% 40%, #1d3354 0%, #0c1626 45%, #05090f 100%)` }}>
      <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)", backgroundSize: "80px 80px" }} />
    </AbsoluteFill>
  );
};

export const Showreel: React.FC<ShowreelProps> = ({ showBackground }) => {
  let at = 0;
  return (
    <AbsoluteFill>
      {showBackground && <Background />}
      {sections.map((x, i) => {
        const from = at;
        at += sec(x.d);
        const tr = x.transition;
        const trLen = tr ? sec(tr.durationInSeconds) : 0;
        return (
          <React.Fragment key={i}>
            <Sequence from={from} durationInFrames={sec(x.d)} name={`Section ${i + 1}`}>
              {x.el}
            </Sequence>
            {tr && (
              <Sequence from={from - Math.floor(trLen / 2)} durationInFrames={trLen} name={`Transition → ${i + 1}`}>
                <SectionTransition {...tr} />
              </Sequence>
            )}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
