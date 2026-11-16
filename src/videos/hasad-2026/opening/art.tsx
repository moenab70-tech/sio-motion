// «من فكرة إلى إنجاز» — illustration kit (hand-authored SVG, rigged for real part animation).
// Style: cinematic chiaroscuro 2D — dusk window light + warm desk lamp, rim-lit figures, SIO navy & gold.
import React from "react";

export const P = {
  night0: "#060D18", night1: "#0B1626", night2: "#13284A",
  skyTop: "#1B3557", skyMid: "#3E6189", horizon: "#D39A5C", sun: "#F6CF8E",
  gold: "#C8A45D", warm: "#F5D9A0", rim: "#F0C784",
  ink: "#070D17", skinDark: "#1A2232",
  paper: "#EFE6D2", paperShade: "#D9CDB3", graphite: "#2E2A26",
  thobe: "#ECE8DF", thobeShade: "#B9B4A8", skin: "#8A5A3C", skinLight: "#A8714C",
};

/** Seated employee in profile (facing right), silhouette with lamp rim light. Rig: head tilt, breath, forearm IK to wrist. */
export const SeatedFigure: React.FC<{ wrist: { x: number; y: number }; headTilt: number; breath: number; id: string }> = ({ wrist, headTilt, breath, id }) => {
  const elbow = { x: 1108, y: 692 };
  const dx = wrist.x - elbow.x, dy = wrist.y - elbow.y;
  const len = Math.hypot(dx, dy), ang = (Math.atan2(dy, dx) * 180) / Math.PI;
  const head = "M 1114 404 C 1108 372, 1078 352, 1046 356 C 1010 360, 990 388, 988 420 C 984 470, 970 520, 940 575 L 1010 585 C 1040 560, 1070 548, 1092 540 L 1096 452 C 1100 430, 1106 418, 1114 404 Z";
  const face = "M 1100 418 C 1110 420, 1116 428, 1117 440 L 1121 452 C 1123 462, 1131 470, 1135 478 C 1133 484, 1126 486, 1122 487 C 1125 492, 1124 497, 1121 500 C 1123 504, 1122 509, 1118 512 C 1121 522, 1116 536, 1100 542 L 1094 542 L 1096 452 Z";
  const body = "M 1088 538 C 1110 548, 1128 575, 1134 610 C 1140 650, 1138 690, 1128 718 L 1130 770 L 950 770 C 945 700, 950 640, 965 600 C 975 575, 1000 560, 1030 552 Z";
  const upperArm = "M 1040 570 C 1075 560, 1100 600, 1112 640 L 1130 690 C 1120 708, 1095 708, 1085 698 L 1050 620 Z";
  const fore = `M 0 -19 C 40 -21, ${len - 24} -15, ${len - 4} -12 L ${len} 12 C ${len - 24} 14, 40 20, 0 20 Z`;
  const rimMask = `rim-${id}`;
  return (
    <g>
      <defs>
        <linearGradient id={`${rimMask}-g`} x1="1030" x2="1140" y1="0" y2="0" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#000" /><stop offset="1" stopColor="#fff" />
        </linearGradient>
        <mask id={rimMask} maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"><rect width="1920" height="1080" fill={`url(#${rimMask}-g)`} /></mask>
        <filter id={`${rimMask}-glow`} x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" /></filter>
      </defs>
      {/* chair back */}
      <path d="M 905 520 C 915 515, 935 515, 942 525 L 958 770 L 928 770 Z" fill="#0A1322" />
      <g transform={`translate(0 ${breath * 2}) `}>
        <path d={body} fill={P.ink} />
        <path d={upperArm} fill="#0B1220" />
        {/* forearm + hand + pencil follow the wrist */}
        <g transform={`translate(${elbow.x} ${elbow.y}) rotate(${ang})`}>
          <path d={fore} fill="#0B1220" />
          <path d={`M ${len - 6} -13 L ${len + 2} -13 L ${len + 2} 13 L ${len - 4} 13 Z`} fill="#1C2433" />
          <g transform={`translate(${len} 0) rotate(${-ang + 8})`}>
            <path d="M 0 -12 C 10 -18, 26 -16, 34 -8 C 40 -2, 42 6, 36 12 C 28 18, 12 18, 0 12 Z" fill="#0E1626" />
            <line x1="22" y1="-4" x2="56" y2="16" stroke="#3A3326" strokeWidth="4" strokeLinecap="round" />
            <line x1="52" y1="14" x2="58" y2="18" stroke={P.gold} strokeWidth="3" strokeLinecap="round" />
          </g>
        </g>
        {/* head (tilts around the neck) */}
        <g transform={`rotate(${headTilt} 1070 535)`}>
          <path d={face} fill={P.skinDark} />
          <path d={head} fill={P.ink} />
          <path d="M 1000 392 C 1030 372, 1080 368, 1108 384" fill="none" stroke="#02050A" strokeWidth="9" strokeLinecap="round" />
          <path d="M 998 406 C 1030 386, 1080 382, 1106 398" fill="none" stroke="#02050A" strokeWidth="7" strokeLinecap="round" />
          <path d="M 1103 455 C 1107 452, 1112 452, 1115 456" fill="none" stroke="#000" strokeWidth="2.4" strokeLinecap="round" />
          <circle cx="1111" cy="457" r="1.3" fill={P.warm} opacity="0.85" />
          {/* rim light on the lamp side */}
          <g mask={`url(#${rimMask})`} filter={`url(#${rimMask}-glow)`} opacity="0.95">
            <path d={face} fill="none" stroke={P.rim} strokeWidth="2.6" />
            <path d={head} fill="none" stroke={P.rim} strokeWidth="2.2" opacity="0.7" />
          </g>
        </g>
        <g mask={`url(#${rimMask})`} filter={`url(#${rimMask}-glow)`} opacity="0.8">
          <path d={body} fill="none" stroke={P.rim} strokeWidth="2.4" />
          <path d={upperArm} fill="none" stroke={P.rim} strokeWidth="1.8" />
        </g>
      </g>
    </g>
  );
};

/** Close-up writing hand (top view): white thobe sleeve, cuff, skin, pencil. Origin = pencil tip; points up-right. */
export const WritingHand: React.FC<{ lift: number; grip: number }> = ({ lift, grip }) => (
  <g>
    {/* cast shadow on the paper (grows as the pencil lifts) */}
    <g transform={`translate(${16 + lift * 26} ${24 + lift * 34})`} opacity={0.32 - lift * 0.08} filter="url(#soft8)">
      <HandShape shadow grip={grip} />
    </g>
    <g transform={`translate(${-lift * 4} ${-lift * 10}) scale(${1 + lift * 0.03})`}>
      <HandShape grip={grip} />
    </g>
  </g>
);

const HandShape: React.FC<{ shadow?: boolean; grip: number }> = ({ shadow, grip }) => {
  const f = (c: string) => (shadow ? "#000" : c);
  return (
    <g transform="rotate(-52)">
      {/* sleeve + cuff */}
      <path d="M 420 -78 L 1100 -170 L 1100 230 L 445 76 Z" fill={f("url(#sleeve)")} />
      <path d="M 360 -64 L 424 -80 L 446 78 L 372 70 Z" fill={f(P.thobe)} />
      {!shadow && <path d="M 366 -60 L 376 68" stroke={P.thobeShade} strokeWidth="3" opacity="0.6" />}
      {/* pencil */}
      <path d="M 0 0 L 34 -8 L 34 8 Z" fill={f("#3B342C")} />
      <path d="M 34 -8 L 70 -11 L 70 11 L 34 8 Z" fill={f("#D9B98A")} />
      <path d="M 70 -11 L 430 -11 L 430 11 L 70 11 Z" fill={f("#C99A3A")} />
      {!shadow && <path d="M 70 -3 L 430 -3" stroke="#E7BC5E" strokeWidth="5" />}
      {!shadow && <path d="M 70 6 L 430 6" stroke="#9C7426" strokeWidth="4" />}
      {/* hand */}
      <g transform={`rotate(${grip * 3} 200 0)`}>
        <path d="M 120 -18 C 150 -62, 232 -88, 302 -72 C 342 -62, 362 -40, 372 -10 L 374 52 C 330 72, 260 74, 200 57 C 165 46, 140 30, 125 14 Z" fill={f(P.skin)} />
        <path d="M 100 -14 C 120 -32, 172 -40, 212 -31 C 224 -21, 214 -12, 202 -10 C 170 -10, 130 -4, 108 2 Z" fill={f(P.skinLight)} />
        <path d="M 140 10 C 152 32, 192 46, 232 41 C 243 35, 238 24, 227 22 C 200 22, 170 14, 150 0 Z" fill={f("#7A4E33")} />
        {!shadow && <>
          <path d="M 200 -30 C 230 -46, 270 -52, 300 -46" stroke="#B98258" strokeWidth="3" fill="none" opacity="0.7" strokeLinecap="round" />
          <path d="M 196 -24 C 202 -26, 208 -26, 212 -24" stroke="#5C3A26" strokeWidth="2" fill="none" />
          <path d="M 300 -60 C 330 -50, 350 -30, 356 -8" stroke="#6B4530" strokeWidth="2" fill="none" opacity="0.5" />
        </>}
      </g>
    </g>
  );
};

/** Shared SVG defs used by the close-ups. */
export const Defs: React.FC = () => (
  <defs>
    <filter id="soft8" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8" /></filter>
    <filter id="soft3"><feGaussianBlur stdDeviation="3" /></filter>
    <filter id="pencilTex" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" />
    </filter>
    <linearGradient id="sleeve" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stopColor={P.thobe} /><stop offset="1" stopColor={P.thobeShade} />
    </linearGradient>
  </defs>
);
