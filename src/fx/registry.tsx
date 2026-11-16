// Template registry for FX wrappers and scene sequences (reuses existing templates unchanged).
import type React from "react";
import { CinematicTitle } from "../templates/CinematicTitle";
import { StatCounter } from "../templates/StatCounter";
import { InfographicCards } from "../templates/InfographicCards";
import { ProjectCard } from "../templates/ProjectCard";
import { LowerThird } from "../templates/LowerThird";
import { FxTitle } from "./FxTitle";
import { Bars3D } from "./Bars3D";

export const TEMPLATE_COMPONENTS = {
  CinematicTitle,
  StatCounter,
  InfographicCards,
  ProjectCard,
  LowerThird,
  FxTitle,
  Bars3D,
} as const;

export type TemplateKey = keyof typeof TEMPLATE_COMPONENTS;

/** Scene = a registered template + its props (must include durationInSeconds). */
export type Scene = { template: TemplateKey; props: Record<string, unknown> & { durationInSeconds: number } };

export const renderScene = (scene: Scene) => {
  const C = TEMPLATE_COMPONENTS[scene.template] as React.FC<Record<string, unknown>>;
  return <C {...scene.props} />;
};
