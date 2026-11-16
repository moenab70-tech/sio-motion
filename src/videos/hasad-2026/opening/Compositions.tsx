// Opening compositions: standalone opening (picture + audio) and opening + approved film.
// The approved film components/config are imported read-only; nothing in them changes.
import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { AudioMix, type AudioSolo } from "../../../audio/AudioMix";
import { hasadConfig as hasadBase, totalFrames } from "../config";
import { finalAudioFor } from "../audio.final";
// The openings run at 30 fps → embed the film re-timed at 30 fps (everything in config is in seconds).
const hasadConfig = { ...hasadBase, fps: 30 };
import { HasadVideo } from "../HasadVideo";
import { OpeningFilm } from "./OpeningFilm";
import { openingAudio } from "./audio";
import { OPENING_FRAMES } from "./timing";

const OPENING_AUDIO_FRAMES = OPENING_FRAMES + 45; // score tail overlaps the film's first 1.5 s

export const OpeningWithAudio: React.FC<{ audioSolo: AudioSolo }> = ({ audioSolo }) => (
  <AbsoluteFill>
    <OpeningFilm />
    <AudioMix mix={openingAudio} durationInFrames={OPENING_FRAMES} solo={audioSolo} />
  </AbsoluteFill>
);

export const OpeningPlusFilm: React.FC<{ audioSolo: AudioSolo }> = ({ audioSolo }) => (
  <AbsoluteFill>
    <Sequence durationInFrames={OPENING_FRAMES} name="Opening · من فكرة إلى إنجاز"><OpeningFilm /></Sequence>
    <Sequence from={OPENING_FRAMES} name="Film · بصمة إنجاز & نمو"><HasadVideo {...hasadConfig} /></Sequence>
    <Sequence durationInFrames={OPENING_AUDIO_FRAMES} name="Opening audio"><AudioMix mix={openingAudio} durationInFrames={OPENING_AUDIO_FRAMES} solo={audioSolo} /></Sequence>
    <Sequence from={OPENING_FRAMES} name="Film audio"><AudioMix mix={finalAudioFor(hasadConfig)} durationInFrames={totalFrames(hasadConfig)} solo={audioSolo} /></Sequence>
  </AbsoluteFill>
);

export const OPENING_PLUS_FILM_FRAMES = OPENING_FRAMES + totalFrames(hasadConfig);
