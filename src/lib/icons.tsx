import React from "react";
import {
  Award, Briefcase, Building2, Calendar, Clock, Droplets, Factory, Globe, GraduationCap,
  HeartHandshake, Leaf, MapPin, Percent, ShieldCheck, Target, TrendingUp, Users, Wallet, Zap,
} from "lucide-react";

// Icon names usable in any template config.
export const ICONS = {
  users: Users, growth: TrendingUp, building: Building2, leaf: Leaf, target: Target, award: Award,
  globe: Globe, partnership: HeartHandshake, education: GraduationCap, factory: Factory,
  shield: ShieldCheck, briefcase: Briefcase, energy: Zap, water: Droplets, calendar: Calendar,
  percent: Percent, location: MapPin, clock: Clock, wallet: Wallet,
} as const;

export type IconName = keyof typeof ICONS;

export const Icon: React.FC<{ name: IconName; size: number; color: string; strokeWidth?: number }> = ({ name, size, color, strokeWidth = 1.6 }) => {
  const C = ICONS[name] ?? ICONS.target;
  return <C size={size} color={color} strokeWidth={strokeWidth} absoluteStrokeWidth={false} />;
};
