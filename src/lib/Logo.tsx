import React from "react";
import { Img, staticFile } from "remotion";
import { AUTO_PREFERENCE, DEFAULT_FORM, defaultLogo, LOGOS, type LogoAsset, type LogoForm, type LogoVariant } from "../config/logos";

export type LogoProps = {
  form?: LogoForm;
  variant?: LogoVariant | "auto";
  background?: "dark" | "light"; // used when variant is "auto"
  /** Set ONE of height / width; the other follows the original aspect ratio. */
  height?: number;
  width?: number;
  /** true = size and align to the artwork itself, ignoring the file's empty margin (file is not modified). */
  trimMargin?: boolean;
  opacity?: number; // only whole-logo opacity; no effects are ever applied
  style?: React.CSSProperties; // positioning only
};

/** Picks the asset. "auto" tries AUTO_PREFERENCE for the background; an explicit variant must exist. */
export const resolveLogo = (form: LogoForm, variant: LogoVariant | "auto", background: "dark" | "light"): { asset: LogoAsset; variant: LogoVariant } => {
  const options = variant === "auto" ? AUTO_PREFERENCE[background] : [variant];
  for (const v of options) {
    const asset = LOGOS[form][v];
    if (asset) return { asset, variant: v };
  }
  const available = Object.keys(LOGOS[form]).join(", ");
  throw new Error(`Logo "${form}/${variant}" has no official file. Available for "${form}": ${available}.`);
};

/**
 * Official logo, rendered exactly as supplied:
 * aspect ratio locked, colours untouched, no shadow / filter / blend / per-part animation.
 */
export const Logo: React.FC<LogoProps> = ({
  form: formProp,
  variant = defaultLogo.variant,
  background = defaultLogo.background,
  height,
  width,
  trimMargin = true,
  opacity = 1,
  style,
}) => {
  const form = formProp ?? DEFAULT_FORM[background];
  const { asset } = resolveLogo(form, variant, background);
  const box = trimMargin ? asset.content : { x: 0, y: 0, w: asset.width, h: asset.height };
  // uniform scale from a single dimension → proportions can never be distorted
  const scale = width !== undefined ? width / box.w : (height ?? 120) / box.h;

  return (
    <div
      aria-label="Saudi Irrigation Organization logo"
      style={{
        ...style,
        width: box.w * scale,
        height: box.h * scale,
        overflow: "hidden",
        position: style?.position ?? "relative",
        flexShrink: 0,
        opacity,
        // guard: never inherit visual effects from a parent template
        filter: "none",
        textShadow: "none",
        mixBlendMode: "normal",
      }}
    >
      <Img
        src={staticFile(asset.file)}
        style={{
          position: "absolute",
          left: -box.x * scale,
          top: -box.y * scale,
          width: asset.width * scale,
          height: asset.height * scale,
          maxWidth: "none",
        }}
      />
    </div>
  );
};
