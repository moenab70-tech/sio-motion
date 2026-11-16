import React from "react";
import { Composition, Folder } from "remotion";
import { VIDEO } from "../../config/brand";
import { hasadConfig, sceneFrames, totalFrames, type HasadConfig } from "./config";
import { HasadVideo, SceneClip, type SceneClipProps } from "./HasadVideo";
import { HasadAudioTrial, type AudioTrialProps } from "./AudioTrial";
import { trialAudio, TRIAL_SECONDS } from "./audio.trial";
import { finalAudio } from "./audio.final";
import { SparkScene, SPARK_FRAMES } from "./opening/SparkScene";
import { OpeningWithAudio, OpeningPlusFilm, OPENING_PLUS_FILM_FRAMES } from "./opening/Compositions";
import { OPENING_FRAMES } from "./opening/timing";
import { OpeningBlenderV6, OpeningBlenderV6PlusFilm, OpeningBlenderV6_2, OPENING_V6_PLUS_FILM_FRAMES } from "./opening/OpeningBlenderV6";
import { withVoDurations } from "../../audio/AudioMix";

const FPS = hasadConfig.fps; // 25 fps for the initiative film
const size = { width: VIDEO.width, height: VIDEO.height };

// Length follows the scene list in config.ts (and any edit made in the Studio props panel).
export const HasadRoot: React.FC = () => (
  <>
    <Folder name="Initiative">
      {/* «بصمة إنجاز & نمو» — full film, picture only */}
      <Composition
        id="Initiative-Film"
        component={HasadVideo}
        defaultProps={hasadConfig}
        calculateMetadata={({ props }: { props: HasadConfig }) => ({ durationInFrames: totalFrames(props), fps: props.fps })}
        {...size}
        fps={FPS}
        durationInFrames={totalFrames(hasadConfig)}
      />
      {/* Full film + music & sfx (combined MP4 preview); audioSolo = music | sfx → separate audio stems */}
      <Composition
        id="Initiative-Film-Final"
        component={HasadAudioTrial}
        defaultProps={{ audioSolo: "all", mix: finalAudio } as AudioTrialProps}
        {...size}
        fps={FPS}
        durationInFrames={totalFrames(hasadConfig)}
      />
    </Folder>
    <Folder name="Initiative-Scenes">
      {/* Each scene on its own (no transitions, no audio) for editing in Premiere */}
      {hasadConfig.scenes.map((s, i) => (
        <Composition
          key={s.id}
          id={`Initiative-${s.id}`}
          component={SceneClip}
          defaultProps={{ cfg: hasadConfig, index: i } as SceneClipProps}
          {...size}
          fps={FPS}
          durationInFrames={sceneFrames(hasadConfig)[i]}
        />
      ))}
    </Folder>
    <Folder name="Productions">
      <Composition
        id="Hasad-Audio-Trial-15s"
        component={HasadAudioTrial}
        defaultProps={{ audioSolo: "all", mix: trialAudio } as AudioTrialProps}
        calculateMetadata={async ({ props }: { props: AudioTrialProps }) => ({ props: { ...props, mix: await withVoDurations(props.mix) } })}
        {...size}
        fps={FPS}
        durationInFrames={TRIAL_SECONDS * FPS}
      />
      {/* Animated openings (30 fps, unchanged) */}
      <Composition id="Hasad-Opening-S01-Spark" component={SparkScene} {...size} fps={VIDEO.fps} durationInFrames={SPARK_FRAMES} />
      <Composition id="Hasad-Opening-20s" component={OpeningWithAudio} defaultProps={{ audioSolo: "all" as const }} {...size} fps={VIDEO.fps} durationInFrames={OPENING_FRAMES} />
      <Composition id="Hasad-Opening-Plus-Film" component={OpeningPlusFilm} defaultProps={{ audioSolo: "all" as const }} {...size} fps={VIDEO.fps} durationInFrames={OPENING_PLUS_FILM_FRAMES} />
      <Composition id="Hasad-Opening-Blender-v6-20s" component={OpeningBlenderV6} defaultProps={{ audioSolo: "all" as const }} {...size} fps={VIDEO.fps} durationInFrames={OPENING_FRAMES} />
      <Composition id="Hasad-Opening-Blender-v6-2-20s" component={OpeningBlenderV6_2} defaultProps={{ audioSolo: "all" as const }} {...size} fps={VIDEO.fps} durationInFrames={OPENING_FRAMES} />
      <Composition id="Hasad-Opening-Blender-v6-Plus-Film" component={OpeningBlenderV6PlusFilm} defaultProps={{ audioSolo: "all" as const }} {...size} fps={VIDEO.fps} durationInFrames={OPENING_V6_PLUS_FILM_FRAMES} />
    </Folder>
  </>
);
