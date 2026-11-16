import React from "react";
import { Composition, Folder } from "remotion";
import { DamRainfallReport, type DamRainfallReportProps } from "./DamRainfallReport";
import { DAM_VIDEO, harimla, sulbukh } from "./config";
import { ContactSheet, SHEET, type ContactSheetProps } from "./ContactSheet";

// Length follows the `duration` prop (also when edited in the Studio props panel).
const byDuration = ({ props }: { props: DamRainfallReportProps }) => ({
  durationInFrames: Math.max(1, Math.round(props.duration * DAM_VIDEO.fps)),
});

export const DamsRoot: React.FC = () => (
  <Folder name="Dams-2026">
    <Composition id="Dam-Harimla" component={DamRainfallReport} defaultProps={harimla} calculateMetadata={byDuration} {...DAM_VIDEO} durationInFrames={1} />
    <Composition id="Dam-Sulbukh" component={DamRainfallReport} defaultProps={sulbukh} calculateMetadata={byDuration} {...DAM_VIDEO} durationInFrames={1} />
    <Composition
      id="Dam-ContactSheet"
      component={ContactSheet}
      defaultProps={{ clips: [], cols: 6 } as ContactSheetProps}
      calculateMetadata={({ props }: { props: ContactSheetProps }) => ({
        width: props.cols * (SHEET.cellW + SHEET.gap) + SHEET.gap,
        height: Math.max(1, props.clips.length) * (SHEET.cellH + SHEET.label + SHEET.gap) + SHEET.gap,
      })}
      width={100}
      height={100}
      fps={30}
      durationInFrames={1}
    />
  </Folder>
);
