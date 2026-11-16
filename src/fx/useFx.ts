import { useCurrentFrame } from "remotion";
import { defaultFx, type Fx } from "../config/fx";

/** Merges FX overrides with defaults and exposes a speed-scaled frame. */
export const useFx = (fx?: Partial<Fx>) => {
  const settings = { ...defaultFx, ...fx };
  const intensity = Math.max(0, Math.min(1, settings.intensity));
  const frame = useCurrentFrame() * settings.speed;
  return { ...settings, intensity, frame };
};
