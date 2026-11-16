// 4 ─ Project information card: location, duration, budget, progress
import React from "react";
import { AbsoluteFill } from "remotion";
import { useTemplate, riseStyle, type CommonProps, type LogoSlot } from "../lib/brand";
import { Logo } from "../lib/Logo";
import { AnimatedNumber } from "../lib/AnimatedNumber";
import { Icon, type IconName } from "../lib/icons";
import { EASE, ramp } from "../lib/motion";
import { localizeDigits, percentSign } from "../lib/numbers";

export type ProjectCardProps = CommonProps & {
  tag?: string; // e.g. "مشروع بنية تحتية"
  projectName: string;
  location: string;
  duration: string; // free text, digits are localized: "18 شهراً"
  budget: { value: number; currency: string; compact?: boolean; decimals?: number };
  progress: number; // 0–100
  status?: string; // e.g. "قيد التنفيذ"
  labels?: { location?: string; duration?: string; budget?: string; progress?: string };
  layout: "card" | "wide";
  side?: "center" | "start" | "end";
  logo?: LogoSlot; // top corner of the card (fade only)
};

export const ProjectCard: React.FC<ProjectCardProps> = (props) => {
  const t = useTemplate(props);
  const { palette: c, font, digits, frame, s, out } = t;
  const L = { location: "الموقع", duration: "مدة التنفيذ", budget: "الميزانية", progress: "نسبة الإنجاز", ...props.labels };
  const wide = props.layout === "wide";

  const shell = t.enter(0, 0, 1.0);
  const divider = ramp(frame, s(0.5), s(1.0), EASE.inOut);
  const count = ramp(frame, s(1.0), s(2.0), EASE.count);
  const bar = ramp(frame, s(1.2), s(2.2), EASE.count);

  const rows: { icon: IconName; label: string; value: React.ReactNode }[] = [
    { icon: "location", label: L.location, value: localizeDigits(props.location, digits) },
    { icon: "clock", label: L.duration, value: localizeDigits(props.duration, digits) },
    {
      icon: "wallet",
      label: L.budget,
      value: <AnimatedNumber value={props.budget.value} progress={count} digits={digits} compact={props.budget.compact} decimals={props.budget.decimals} suffix={props.budget.currency} suffixScale={0.7} suffixColor={c.textMuted} />,
    },
  ];

  const progressBlock = (
    <div style={{ ...riseStyle(t.enter(4, 0.55), out, 14), width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 14 }}>
        <span style={{ fontSize: 28, color: c.textMuted }}>{L.progress}</span>
        <span style={{ fontFamily: font.display, fontSize: 48, fontWeight: 700, color: c.accent }}>
          <AnimatedNumber value={props.progress} progress={bar} digits={digits} suffix={percentSign(digits)} suffixScale={0.7} />
        </span>
      </div>
      <div style={{ height: 12, borderRadius: 6, background: c.track, overflow: "hidden", display: "flex" }}>
        <div style={{ width: `${Math.min(100, props.progress) * bar}%`, borderRadius: 6, background: `linear-gradient(${t.rtl ? 270 : 90}deg, ${c.accent}, ${c.secondary})` }} />
      </div>
    </div>
  );

  const header = (
    <div style={{ ...riseStyle(t.enter(0, 0.25), out, 16), paddingInlineEnd: props.logo && !wide ? 150 : 0 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 10 }}>
        {props.tag && <span style={{ fontSize: 24, fontWeight: 500, color: c.accent, border: `1px solid ${c.accent}`, borderRadius: 999, padding: "2px 18px" }}>{props.tag}</span>}
        {props.status && (
          <span style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 24, color: c.textMuted }}>
            <span style={{ width: 10, height: 10, borderRadius: 5, background: c.secondary }} />
            {props.status}
          </span>
        )}
      </div>
      <div style={{ fontFamily: font.display, fontSize: wide ? 50 : 58, fontWeight: 700, color: c.text, lineHeight: 1.45 }}>{localizeDigits(props.projectName, digits)}</div>
    </div>
  );

  const infoRow = (r: (typeof rows)[number], i: number) => (
    <div key={i} style={{ ...riseStyle(t.enter(i + 1, 0.55), out, 14), display: "flex", alignItems: "center", gap: 20 }}>
      <div style={{ width: 64, height: 64, borderRadius: 18, background: c.track, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <Icon name={r.icon} size={32} color={c.accent} />
      </div>
      <div>
        <div style={{ fontSize: 24, color: c.textMuted, lineHeight: 1.4 }}>{r.label}</div>
        <div style={{ fontSize: 34, fontWeight: 600, color: c.text, lineHeight: 1.45 }}>{r.value}</div>
      </div>
    </div>
  );

  const justify = props.side === "start" ? "flex-start" : props.side === "end" ? "flex-end" : "center";

  return (
    <AbsoluteFill style={{ direction: t.dir, fontFamily: font.body, justifyContent: wide ? "flex-end" : "center", alignItems: wide ? "center" : justify, padding: wide ? "0 120px 110px" : "0 150px" }}>
      <div
        style={{
          width: wide ? "100%" : 820,
          background: c.panel,
          border: `1px solid ${c.panelBorder}`,
          borderRadius: 32,
          padding: wide ? "34px 48px" : "48px 54px",
          boxShadow: `0 30px 80px ${c.shadow}`,
          opacity: shell * out,
          transform: `translateY(${(1 - shell) * 60 - (1 - out) * 20}px)`,
          clipPath: `inset(0 0 ${(1 - shell) * 30}% 0 round 32px)`,
          position: "relative",
        }}
      >
        {props.logo && !wide && (
          <Logo {...props.logo} height={props.logo.height ?? 110} opacity={t.enter(0, 0.3) * out} style={{ position: "absolute", top: 44, insetInlineEnd: 48 }} />
        )}
        {wide ? (
          <>
            <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
              {props.logo && <Logo {...props.logo} height={props.logo.height ?? 100} opacity={t.enter(0, 0.3) * out} />}
              <div style={{ flex: 1, minWidth: 0 }}>{header}</div>
              <div style={{ width: 520, flexShrink: 0 }}>{progressBlock}</div>
            </div>
            <div style={{ height: 1.5, background: c.panelBorder, margin: "26px 0", transform: `scaleX(${divider})`, transformOrigin: t.rtl ? "right" : "left" }} />
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 32 }}>{rows.map(infoRow)}</div>
          </>
        ) : (
          <>
            {header}
            <div style={{ height: 1.5, background: c.panelBorder, margin: "30px 0", transform: `scaleX(${divider})`, transformOrigin: t.rtl ? "right" : "left" }} />
            <div style={{ display: "flex", flexDirection: "column", gap: 26, marginBottom: 38 }}>{rows.map(infoRow)}</div>
            {progressBlock}
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};
