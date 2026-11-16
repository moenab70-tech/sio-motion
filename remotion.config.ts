// Render defaults.
// • Normal renders: ProRes 4444 with alpha → drop straight onto a Premiere timeline.
// • PREVIEW=1 (used by `npm run render:preview`): small H.264 MP4 for review/sharing (no alpha).
import { Config } from "@remotion/cli/config";

Config.setOverwriteOutput(true);

if (process.env.PREVIEW === "1") {
  Config.setCodec("h264");
  Config.setVideoImageFormat("jpeg");
  Config.setPixelFormat("yuv420p");
  Config.setCrf(18);
} else {
  Config.setVideoImageFormat("png"); // PNG frames keep transparency
  Config.setCodec("prores");
  Config.setProResProfile("4444");
  Config.setPixelFormat("yuva444p10le"); // 4:4:4 + alpha (ProRes stores it at 12-bit internally)
}
