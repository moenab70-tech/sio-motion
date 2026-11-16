// Separate Remotion root for the Motion Styles library (isolated from src/Root.tsx production templates).
import React from "react";
import { Composition, Folder } from "remotion";
import { VIDEO } from "../../config/brand";
import { getStyles } from "../registry";
import type { MotionStyleBaseProps } from "../core/types";
import { AllStylesGallery, StyleGallery, allStylesDuration } from "./StyleGallery";

const meta = (fallback: number) => ({ props }: { props: MotionStyleBaseProps }) => ({ durationInFrames: props.durationInFrames ?? fallback });

export const MotionStylesRoot: React.FC = () => (
  <>
    <Folder name="Gallery">
      <Composition id="MS-Gallery-All" component={AllStylesGallery} {...VIDEO} durationInFrames={allStylesDuration()} />
      {getStyles().map((d) => (
        <Composition key={d.id} id={`MS-Gallery-${d.id}`} component={StyleGallery} defaultProps={{ styleId: d.id }} {...VIDEO} durationInFrames={d.durationInFrames} />
      ))}
    </Folder>
    {getStyles().map((d) => (
      <Folder key={d.id} name={d.id}>
        <Composition id={`MS-${d.id}-Institutional`} component={d.component} defaultProps={d.presets.institutional} calculateMetadata={meta(d.durationInFrames)} {...VIDEO} durationInFrames={d.durationInFrames} />
        <Composition id={`MS-${d.id}-Experimental`} component={d.component} defaultProps={d.presets.experimental} calculateMetadata={meta(d.durationInFrames)} {...VIDEO} durationInFrames={d.durationInFrames} />
        <Composition id={`MS-${d.id}-English`} component={d.component} defaultProps={d.presets.english} calculateMetadata={meta(d.durationInFrames)} {...VIDEO} durationInFrames={d.durationInFrames} />
      </Folder>
    ))}
  </>
);
