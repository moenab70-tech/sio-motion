# Layer prep for cut-out animation (run with the rembg tool's Python: ~/.local/share/uv/tools/rembg/bin/python).
#   python prep_layers.py <image.png> <out_dir> <name> [--fg-only] [--dilate 18]
# Writes <name>-fg.png (subject, RGBA via BiRefNet, MIT) and, unless --fg-only, <name>-bg.png:
# the same image with the subject area rebuilt by push-pull diffusion from the surrounding pixels
# (only ever seen at the edges during small parallax moves, and softened further by camera depth of field).
import sys, os
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove

args = sys.argv[1:]
src, out_dir, name = args[0], args[1], args[2]
fg_only = "--fg-only" in args
dilate = int(args[args.index("--dilate") + 1]) if "--dilate" in args else 18
os.makedirs(out_dir, exist_ok=True)

img = Image.open(src).convert("RGB")
mask = remove(img, session=new_session("birefnet-general"), only_mask=True).convert("L")
fg = img.copy(); fg.putalpha(mask)
fg.save(os.path.join(out_dir, f"{name}-fg.png"))
print("fg", fg.size)

if not fg_only:
    hole = mask.filter(ImageFilter.MaxFilter(dilate | 1)).filter(ImageFilter.GaussianBlur(3))
    h = np.asarray(hole, dtype=np.float32) / 255.0
    # hard zero inside the hole: tiny residual weights would otherwise be re-normalised into a "ghost" of the subject
    known = np.where(h > 0.04, 0.0, 1.0 - h).astype(np.float32)
    rgb = np.asarray(img, dtype=np.float32) / 255.0

    def fill(c, w):
        H, W = w.shape
        if min(H, W) <= 4:
            s = w.sum()
            mean = (c * w[..., None]).sum((0, 1)) / max(s, 1e-6)
            return c * w[..., None] + mean * (1 - w[..., None])
        h2, w2 = (H + 1) // 2, (W + 1) // 2
        cp = np.zeros((h2 * 2, w2 * 2, 3), np.float32); wp = np.zeros((h2 * 2, w2 * 2), np.float32)
        cp[:H, :W] = c * w[..., None]; wp[:H, :W] = w
        C = cp.reshape(h2, 2, w2, 2, 3).sum((1, 3)); Wd = wp.reshape(h2, 2, w2, 2).sum((1, 3))
        small = C / np.maximum(Wd, 1e-6)[..., None]
        coarse = fill(small, np.minimum(Wd, 1.0))
        up = np.repeat(np.repeat(coarse, 2, 0), 2, 1)[:H, :W]
        up = np.asarray(Image.fromarray((np.clip(up, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255.0
        return c * w[..., None] + up * (1 - w[..., None])

    out = fill(rgb, known)
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out_dir, f"{name}-bg.png"))
    print("bg rebuilt, hole px:", int((known < 0.5).sum()))
