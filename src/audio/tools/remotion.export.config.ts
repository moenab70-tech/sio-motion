// Neutral render config for src/audio/tools/export.mjs (codecs are passed explicitly per output).
// The project's remotion.config.ts forces ProRes 4444 by default, which blocks WAV/MP4 renders.
import { Config } from "@remotion/cli/config";

Config.setOverwriteOutput(true);
