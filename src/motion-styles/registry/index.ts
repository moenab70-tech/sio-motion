// Central Motion Styles registry. To add a style: create styles/<Name>.tsx, add presets, then registerStyle(...) below.
// Production templates (src/templates, src/fx) are never touched by this registry.
import * as P from "../presets";
import { KineticType } from "../styles/KineticType";
import { Blueprint } from "../styles/Blueprint";
import { Isometric } from "../styles/Isometric";
import { Holographic } from "../styles/Holographic";
import { ParticleText } from "../styles/ParticleText";
import { LiquidMorph } from "../styles/LiquidMorph";
import { SplitFlap } from "../styles/SplitFlap";
import type { MotionStyleBaseProps } from "../core/types";
import type { MotionStyleDef } from "./types";

const registry: MotionStyleDef<any>[] = []; // eslint-disable-line @typescript-eslint/no-explicit-any

export const registerStyle = <Pr extends MotionStyleBaseProps>(def: MotionStyleDef<Pr>) => {
  if (registry.some((d) => d.id === def.id)) throw new Error(`Motion style "${def.id}" is already registered`);
  registry.push(def);
};

export const getStyles = () => registry as MotionStyleDef<MotionStyleBaseProps>[];

registerStyle({ id: "KineticType", name: { ar: "الطباعة الحركية", en: "Kinetic Typography" }, description: "Staggered word reveals, masking, directional movement, line transitions.", component: KineticType, durationInFrames: 240, supportsTransparency: true, presets: P.kinetic, notes: "Arabic always animates whole words." });
registerStyle({ id: "Blueprint", name: { ar: "المخطط الهندسي", en: "Blueprint" }, description: "Animated grid, schematic draw-on, dimension lines, callouts.", component: Blueprint, durationInFrames: 240, supportsTransparency: true, presets: P.blueprint });
registerStyle({ id: "Isometric", name: { ar: "المنظور الأيزومتري", en: "Isometric" }, description: "Isometric facility built in sequence with camera move and labels.", component: Isometric, durationInFrames: 240, supportsTransparency: true, presets: P.isometric });
registerStyle({ id: "Holographic", name: { ar: "الواجهة الهولوغرافية", en: "Holographic" }, description: "Translucent data panels, scan line, typed rows, sparkline, gauge.", component: Holographic, durationInFrames: 240, supportsTransparency: true, presets: P.holographic, notes: "Panels are semi-transparent by design (alpha preserved)." });
registerStyle({ id: "Particles", name: { ar: "الجزيئات", en: "Particles" }, description: "Deterministic particles forming text, then dispersing along a path.", component: ParticleText, durationInFrames: 240, supportsTransparency: true, presets: P.particles, notes: "Text rasterised once per render worker; cap with maxParticles." });
registerStyle({ id: "LiquidMorph", name: { ar: "التحول السائل", en: "Liquid Morph" }, description: "Organic blob morphs used as fluid masks (pure SVG geometry).", component: LiquidMorph, durationInFrames: 240, supportsTransparency: true, presets: P.liquid });
registerStyle({ id: "SplitFlap", name: { ar: "اللوحة القلّابة", en: "Split-Flap" }, description: "Mechanical flip board: words (Arabic), characters (English), digit counters.", component: SplitFlap, durationInFrames: 210, supportsTransparency: true, presets: P.splitFlap, notes: "Arabic flips whole words to preserve shaping." });

// ── Phase 2 · batch 1 ──
import * as P2 from "../presets/phase2";
import { FlowLines } from "../styles/FlowLines";
import { NetworkMap } from "../styles/NetworkMap";
import { Timeline } from "../styles/Timeline";
import { ProcessFlow } from "../styles/ProcessFlow";
import { Charts } from "../styles/Charts";

registerStyle({ id: "FlowLines", name: { ar: "مسارات التدفق", en: "Flow Lines" }, description: "Pipe/canal network with travelling flow pulses and live flow-rate labels.", component: FlowLines, durationInFrames: 240, supportsTransparency: true, presets: P2.flow, notes: "Layout mirrors in RTL so water flows in the reading direction." });
registerStyle({ id: "NetworkMap", name: { ar: "خريطة الشبكة", en: "Network Map" }, description: "Stations connected by links with travelling data pulses and a pulsing hub.", component: NetworkMap, durationInFrames: 240, supportsTransparency: true, presets: P2.network });
registerStyle({ id: "Timeline", name: { ar: "الخط الزمني", en: "Timeline" }, description: "Milestones along an axis drawn from the reading-start side, with a progress marker.", component: Timeline, durationInFrames: 240, supportsTransparency: true, presets: P2.timeline });
registerStyle({ id: "ProcessFlow", name: { ar: "مخطط العمليات", en: "Process Flow" }, description: "Icon steps with drawn connectors and a travelling active highlight.", component: ProcessFlow, durationInFrames: 240, supportsTransparency: true, presets: P2.process });
registerStyle({ id: "Charts", name: { ar: "الرسوم البيانية", en: "Charts" }, description: "Animated line / area / bars / donut charts with axes and counting values.", component: Charts, durationInFrames: 240, supportsTransparency: true, presets: P2.charts, notes: "Category axis stays left→right in RTL by default (mirrorX to reverse)." });

// ── Phase 2 · batch 2 ──
import * as P2b from "../presets/phase2b";
import { SplitCompare } from "../styles/SplitCompare";
import { LineArt } from "../styles/LineArt";
import { GeometricPattern } from "../styles/GeometricPattern";
import { Topographic } from "../styles/Topographic";

registerStyle({ id: "SplitCompare", name: { ar: "المقارنة", en: "Split Compare" }, description: "Before/after with a sweeping divider, counting values and a delta badge.", component: SplitCompare, durationInFrames: 210, supportsTransparency: true, presets: P2b.compare });
registerStyle({ id: "LineArt", name: { ar: "الرسم الخطي", en: "Line Art" }, description: "Icons and a connecting line drawn stroke by stroke, then labelled.", component: LineArt, durationInFrames: 210, supportsTransparency: true, presets: P2b.lineArt, notes: "Icon draw-on uses a 100-unit dash (icons are ≤100 units long)." });
registerStyle({ id: "GeometricPattern", name: { ar: "الزخارف الهندسية", en: "Geometric Patterns" }, description: "Islamic-inspired 8-point star lattice built outward around a title medallion.", component: GeometricPattern, durationInFrames: 240, supportsTransparency: true, presets: P2b.geometric });
registerStyle({ id: "Topographic", name: { ar: "الخطوط الكنتورية", en: "Topographic" }, description: "Contour lines from a deterministic terrain with a rising water level.", component: Topographic, durationInFrames: 240, supportsTransparency: true, presets: P2b.topo, notes: "Marching squares on a 96×54 grid, computed once per instance." });

// ── Phase 2 · batch 3 ──
import * as P2c from "../presets/phase2c";
import { RadarScan } from "../styles/RadarScan";
import { DataStream } from "../styles/DataStream";
import { ParallaxLayers } from "../styles/ParallaxLayers";
import { SwissGrid } from "../styles/SwissGrid";

registerStyle({ id: "RadarScan", name: { ar: "المسح الراداري", en: "Radar Scan" }, description: "Rotating sweep with trail, blips revealed by the beam, alert ring and status list.", component: RadarScan, durationInFrames: 240, supportsTransparency: true, presets: P2c.radar });
registerStyle({ id: "DataStream", name: { ar: "تدفق البيانات", en: "Data Stream" }, description: "Restrained digit streams that dim and resolve into KPI counters.", component: DataStream, durationInFrames: 240, supportsTransparency: true, presets: P2c.stream, notes: "Glyphs change every 4 frames (deterministic)." });
registerStyle({ id: "ParallaxLayers", name: { ar: "الطبقات العمقية", en: "Parallax Layers" }, description: "Procedural landscape layers moving at depth-dependent speeds (2.5D).", component: ParallaxLayers, durationInFrames: 240, supportsTransparency: true, presets: P2c.parallax, notes: "Lower half is mostly opaque by design." });
registerStyle({ id: "SwissGrid", name: { ar: "الطباعة الشبكية", en: "Swiss Grid" }, description: "Strict 12-column grid, giant number, ruled blocks, snappy motion.", component: SwissGrid, durationInFrames: 210, supportsTransparency: true, presets: P2c.swiss });
