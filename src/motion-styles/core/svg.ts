// Small SVG helpers (no existing equivalents in src/lib).

/** Draw-on stroke: pass pathLength={1} on the element and spread this. */
export const drawOn = (p: number): { strokeDasharray: number; strokeDashoffset: number } => ({ strokeDasharray: 1, strokeDashoffset: 1 - Math.max(0, Math.min(1, p)) });

/** Closed smooth path through points (Catmull-Rom → cubic Bézier). Deterministic, pure geometry. */
export const smoothClosedPath = (pts: [number, number][]) => {
  const n = pts.length;
  let d = `M ${pts[0][0].toFixed(2)} ${pts[0][1].toFixed(2)}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C ${c1[0].toFixed(2)} ${c1[1].toFixed(2)}, ${c2[0].toFixed(2)} ${c2[1].toFixed(2)}, ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;
  }
  return `${d} Z`;
};

/** Isometric projection (2:1). x→right-down, y→left-down, z→up. */
export const iso = (x: number, y: number, z: number, unit: number): [number, number] => [(x - y) * unit * 0.866, (x + y) * unit * 0.5 - z * unit];
