// 15-second audio trial: the first 15 s of «حصاد التميز 2026» + voice-over, music and sfx.
import React from "react";
import { AbsoluteFill, useVideoConfig } from "remotion";
import { AudioMix, type AudioMixConfig, type AudioSolo } from "../../audio/AudioMix";
import { hasadConfig } from "./config";
import { HasadVideo } from "./HasadVideo";

export type AudioTrialProps = { audioSolo: AudioSolo; mix: AudioMixConfig };

export const HasadAudioTrial: React.FC<AudioTrialProps> = ({ audioSolo, mix }) => {
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill>
      <HasadVideo {...hasadConfig} />
      <AudioMix mix={mix} solo={audioSolo} durationInFrames={durationInFrames} />
    </AbsoluteFill>
  );
};
