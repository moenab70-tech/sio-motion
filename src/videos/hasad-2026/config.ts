// ─────────────────────────────────────────────────────────────
// «بصمة إنجاز & نمو» (temporary title until the wording is confirmed; formerly «حصاد التميز 2026»)
// The film's single config file. All texts, durations and images are edited here (or from the Props panel in Remotion Studio).
//
// The film is a list of scenes (scenes) that play in order. To add a new achievement later:
// copy an "award" scene, change its texts and images, and put it in the right place in the list. The durations, transitions,
// sound effects and the separate per-scene export all follow the list automatically.
//
// Images: path relative to the public/ folder (e.g. "media/images/hasad-2026/x.jpg").
//   • Images are never generated, replaced or stretched: each is shown whole at its original ratio inside a uniform frame.
//   • ratio = width ÷ height of the original image. Update it when you swap the image.
//   • caption = optional text under the frame (e.g. to state the certificate type).
// "\n" inside any text = start a new line. Durations are in seconds.
// ─────────────────────────────────────────────────────────────

export type PhotoSlot = { src: string | null; label: string; ratio?: number; caption?: string };
/** A group of photos shown together side by side (1–2 photos); groups follow each other within the scene. */
export type PhotoGroup = PhotoSlot[];

type Base = {
  /** Short English name used for the per-scene export file (e.g. S03-international). */
  id: string;
  /** Scene name in the Studio timeline. */
  name: string;
  seconds: number;
  /** Transition into this scene from the previous one (ignored for the first scene). */
  transition?: "wipe" | "blur";
};

export type Scene =
  | (Base & { kind: "intro"; title: string; subtitle: string; showLogo: boolean; logoHeight: number })
  | (Base & { kind: "about"; kicker: string; lines: string[] })
  | (Base & { kind: "section"; title: string; subtitle?: string })
  | (Base & { kind: "award"; kicker: string; title: string; items: string[]; photos: PhotoGroup[] })
  | (Base & { kind: "cards"; kicker: string; cards: { title: string; body: string }[] })
  | (Base & {
      kind: "outro"; title: string; tagline: string; showLogo: boolean; logoHeight: number;
      /** Time after the closing line. If brandOutro exists, the official outro plays in it (keep it equal to the clip's length). */
      holdSeconds: number;
      /** The organization's official outro (white logo with transparency, over the film's background). null = clean space for Premiere. */
      brandOutro: { src: string } | null;
    });

export type HasadConfig = {
  fps: number;
  transitionSeconds: number;
  /** Calm gold particles in the background (0 = off). */
  particles: number;
  /** Warm light glow behind the intro and outro (0 = off). */
  lightLeak: number;
  /** Fixed logo at the top right for the whole film. show=false = leave it empty to place your logo in Premiere. */
  cornerLogo: { show: boolean; height: number };
  scenes: Scene[];
};

const IMG = "media/images/hasad-2026";
export const INITIATIVE_TITLE = "بصمة إنجاز & نمو";

export const hasadConfig: HasadConfig = {
  fps: 25,
  transitionSeconds: 0.9,
  particles: 0.35,
  lightLeak: 0, // tested: tilts the navy background toward olive, so it's off by default
  cornerLogo: { show: false, height: 150 },

  scenes: [
    // 1 – Intro: initiative name (the logo appears in the official outro at the end)
    {
      kind: "intro", id: "S01-intro", name: "1 · المقدمة", seconds: 7,
      title: INITIATIVE_TITLE,
      subtitle: "المؤسسة العامة للري",
      showLogo: false, // the logo was removed from the intro (it now appears in the official outro at the end)
      logoHeight: 190,
    },

    // 2 – Introducing the initiative
    {
      kind: "about", id: "S02-about", name: "2 · التعريف بالمبادرة", seconds: 11, transition: "blur",
      kicker: "التعريف بالمبادرة",
      lines: [
        "تقدير جهود منسوبي المؤسسة وشركائها",
        "ترسيخ ثقافة التميز",
        "الاحتفاء بالإنجازات",
      ],
    },

    // 3 – International achievements (standalone title)
    { kind: "section", id: "S03-international", name: "3 · منجزات دولية", seconds: 4, transition: "wipe", title: "منجزات دولية" },

    // 4 – USA: PMI award
    {
      kind: "award", id: "S04-award-usa-pmi", name: "4 · أمريكا – جائزة PMI", seconds: 10, transition: "wipe",
      kicker: "الولايات المتحدة الأمريكية",
      title: "جائزة أفضل مشروع\nفي فئة الاستدامة",
      items: ["ضمن جوائز قمة المشاريع PMI لعام 2026م"],
      photos: [
        [{ src: `${IMG}/pmi-stage-sustainability-winner.jpg`, label: "إعلان الفوز", ratio: 4160 / 2774 }],
        [{ src: `${IMG}/pmi-team-trophy.jpg`, label: "تسلّم الجائزة", ratio: 4160 / 2774 }],
        [
          { src: `${IMG}/pmi-trophy-closeup.jpg`, label: "مجسم الجائزة", ratio: 3120 / 4160 },
          { src: `${IMG}/pmi-delegation-trophy.jpg`, label: "وفد المؤسسة", ratio: 3024 / 4032 },
        ],
      ],
    },

    // 5 – France: ICID awards (the certificates state Marseille, France, October 2026)
    {
      kind: "award", id: "S05-award-france-icid", name: "5 · فرنسا – ICID و WatSave", seconds: 12, transition: "wipe",
      kicker: "فرنسا",
      title: "ICID و WatSave",
      items: ["إدراج واحة الأحساء في قائمة WHIS", "جائزة ترشيد المياه"],
      photos: [
        [
          { src: `${IMG}/icid-whis-alahsa-certificate.jpg`, label: "شهادة WHIS – واحة الأحساء", ratio: 702 / 1280 },
          { src: `${IMG}/icid-watsave-certificate.jpg`, label: "شهادة WatSave", ratio: 818 / 1280 },
        ],
        [{ src: `${IMG}/icid-ceremony-02.jpg`, label: "تسليم الجائزة", ratio: 1280 / 960 }],
        [{ src: `${IMG}/icid-ceremony-01.jpg`, label: "تسليم الجائزة", ratio: 582 / 512 }],
      ],
    },

    // 6 – International accreditations: Eng. Abdulrahman Al-Thumairi
    // The certificate shown is a training-workshop attendance certificate (not an expert accreditation) — the caption says so.
    {
      kind: "award", id: "S06-accreditation-althumairi", name: "6 · الاعتمادات الدولية – م. عبدالرحمن الثميري", seconds: 10, transition: "blur",
      kicker: "الاعتمادات الدولية",
      title: "اعتماد المهندس\nعبدالرحمن الثميري",
      items: ["خبيرًا لدى المنصة العالمية WOCAT"],
      photos: [
        [{ src: `${IMG}/wocat-workshop-certificate-thumairi.png`, label: "شهادة حضور ورشة العمل التدريبية", ratio: 3116 / 2252, caption: "شهادة حضور ورشة عمل تدريبية – منصة WOCAT" }],
      ],
    },

    // 7 – International accreditations: Dr. Wadha Al-Rashidi (original image + a detail crop of the same image)
    {
      kind: "award", id: "S07-accreditation-alrashidi", name: "7 · الاعتمادات الدولية – د. وضحى الرشيدي", seconds: 10, transition: "wipe",
      kicker: "الاعتمادات الدولية",
      title: "اعتماد الدكتورة\nوضحى الرشيدي",
      items: ["محكمًا دوليًا في جائزة الابتكار\nالعالمية في استدامة المياه"],
      photos: [
        [{ src: `${IMG}/wadha-alrashedi-jury-member.png`, label: "عضو لجنة التحكيم", ratio: 3032 / 5354 }],
        [{ src: `${IMG}/wadha-alrashedi-jury-member-detail.png`, label: "عضو لجنة التحكيم", ratio: 1840 / 2560 }],
      ],
    },

    // 8 – Local achievements (standalone title)
    { kind: "section", id: "S08-local", name: "8 · منجزات محلية", seconds: 4, transition: "blur", title: "منجزات محلية" },

    // 9 – Nadhee index (text only, no image)
    {
      kind: "award", id: "S09-nadhee-index", name: "9 · مؤشر نضيء", seconds: 8, transition: "wipe",
      kicker: "",
      title: "مؤشر «نضيء»\nلنضج إدارة البيانات",
      items: ["بلوغ مرحلة التعريف وفق قياس سدايا"],
      photos: [],
    },

    // 10 – Outro: back to the initiative name + a general line on continuing achievements, then the official outro
    {
      kind: "outro", id: "S10-outro", name: "10 · الخاتمة + الاوترو الرسمي", seconds: 6, transition: "blur",
      title: INITIATIVE_TITLE,
      tagline: "إنجازات نفخر بها.. وعطاء يستمر",
      showLogo: false,
      logoHeight: 240,
      holdSeconds: 5, // = length of the official outro
      // The organization's official outro (5 s, ProRes 4444 with transparency) — the same clip used in the dams project
      brandOutro: { src: "media/riyadh-dams-2026/outro/sio-social-outro-4444.mov" },
    },
  ],
};

// ── Timing (everything is derived from the list) ─────────────────────────
export const transitionFrames = (c: HasadConfig) => Math.round(c.transitionSeconds * c.fps);
const holdOf = (s: Scene) => (s.kind === "outro" ? s.holdSeconds : 0);
/** Length of each scene in frames (the hold after the outro is counted in the last scene). */
export const sceneFrames = (c: HasadConfig) => c.scenes.map((s) => Math.round((s.seconds + holdOf(s)) * c.fps));
/** Start of each scene on the full timeline (frames), accounting for the transition overlaps. */
export const sceneStarts = (c: HasadConfig) => {
  const tf = transitionFrames(c);
  let t = 0;
  return sceneFrames(c).map((d) => {
    const s = t;
    t += d - tf;
    return s;
  });
};
export const holdFrames = (c: HasadConfig) => Math.round(c.scenes.reduce((a, s) => a + holdOf(s), 0) * c.fps);
export const totalFrames = (c: HasadConfig) => sceneFrames(c).reduce((a, b) => a + b, 0) - transitionFrames(c) * Math.max(0, c.scenes.length - 1);
