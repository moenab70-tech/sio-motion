// ─────────────────────────────────────────────────────────────
// FX system defaults. Every FX template accepts `fx` to override.
// Keep it restrained: effects support the information, never compete with it.
// ─────────────────────────────────────────────────────────────

export type Fx = {
  intensity: number; // 0–1 global strength (blur amount, glow, particle opacity, light)
  speed: number; // animation speed multiplier (1 = normal, 0.8 = slower, 1.2 = faster)
  motionBlur: boolean; // directional blur from real element velocity
  glow: boolean; // soft accent halo on large text (never on the logo)
  lightSweep: boolean; // one highlight pass across titles after they land
  particles: boolean; // floating depth particles behind the content
};

export const defaultFx: Fx = {
  intensity: 0.5,
  speed: 1,
  motionBlur: true,
  glow: true,
  lightSweep: true,
  particles: false,
};
