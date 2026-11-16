import { cancelRender, continueRender, delayRender, staticFile } from "remotion";
import { loadFont as loadKufi } from "@remotion/google-fonts/NotoKufiArabic";
import { loadFont as loadPlex } from "@remotion/google-fonts/IBMPlexSansArabic";
import { loadFont as loadTajawal } from "@remotion/google-fonts/Tajawal";
import { loadFont as loadCairo } from "@remotion/google-fonts/Cairo";
import { numberFont, type FontName } from "../config/brand";

// Google fonts are fetched at render time; Remotion waits for them.
const kufi = loadKufi("normal", { weights: ["300", "400", "500", "700", "800"], subsets: ["arabic", "latin"] });
const plex = loadPlex("normal", { weights: ["300", "400", "500", "600", "700"], subsets: ["arabic", "latin"] });
const tajawal = loadTajawal("normal", { weights: ["300", "400", "500", "700", "800"], subsets: ["arabic", "latin"] });
const cairo = loadCairo("normal", { weights: ["300", "400", "600", "700", "800"], subsets: ["arabic", "latin"] });

// Local number font (from public/), limited to digits & number symbols via unicode-range.
// Declared for every weight so the browser never synthesises a fake bold.
if (numberFont && typeof document !== "undefined") {
  const handle = delayRender(`Loading number font ${numberFont.file}`);
  const face = new FontFace(numberFont.family, `url("${staticFile(numberFont.file)}") format("opentype")`, {
    unicodeRange: numberFont.unicodeRange,
    weight: "100 900",
    style: "normal",
  });
  face
    .load()
    .then((loaded) => {
      document.fonts.add(loaded);
      continueRender(handle);
    })
    .catch((err) => cancelRender(err));
}

const stack = (family: string) => (numberFont ? `"${numberFont.family}", "${family}"` : `"${family}"`);

export const FONT_FAMILIES: Record<FontName, string> = {
  NotoKufiArabic: stack(kufi.fontFamily),
  IBMPlexSansArabic: stack(plex.fontFamily),
  Tajawal: stack(tajawal.fontFamily),
  Cairo: stack(cairo.fontFamily),
};
