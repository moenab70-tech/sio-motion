#!/bin/zsh
# Delivery for the Blender v6 opening (run from the repo root after scripts/final_v6.py --render).
#  - verifies every shot's PNG frame count against opening/timing.ts
#  - per-shot ProRes 422 HQ (.mov, Premiere) + H.264 review copies
#  - full 20 s: final MP4 with music+sfx, clean ProRes 422 HQ, audio stems (src/audio/tools/export.mjs)
#  - decode check of every output (missing/corrupt frames) + frame counts
set -e
cd /Users/mohammadalqurain/Documents/Remotion-MotionGraphics
NAME=hasad-opening-blender-v6
SRC=public/media/opening/blender_v6
OUT=exports/$NAME
mkdir -p $OUT/shots
typeset -A LEN; LEN=(1A 90 1B 96 2A 66 2B 102 3A 84 3B 90 4A 120)
echo "== frame check"
for s in 1A 1B 2A 2B 3A 3B 4A; do
  n=$(ls $SRC/$s/f_*.png | wc -l | tr -d ' ')
  [ "$n" = "${LEN[$s]}" ] && echo "ok $s $n" || { echo "MISSING $s $n/${LEN[$s]}"; exit 1; }
done
echo "== per-shot exports"
for s in 1A 1B 2A 2B 3A 3B 4A; do
  npx remotion ffmpeg -hide_banner -loglevel error -y -framerate 30 -i $SRC/$s/f_%04d.png \
    -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -vendor apl0 $OUT/shots/${NAME}_shot_${s}_ProRes422HQ.mov
  npx remotion ffmpeg -hide_banner -loglevel error -y -framerate 30 -i $SRC/$s/f_%04d.png \
    -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p $OUT/shots/${NAME}_shot_${s}.mp4
  echo "ok shot $s"
done
echo "== full composition (picture + music + sfx)"
node src/audio/tools/export.mjs --entry=src/videos/hasad-2026/entry.ts --id=Hasad-Opening-Blender-v6-20s \
  --name=$NAME --lufs=-16 --only=final,clean,stems --stems=music,sfx
echo "== verification"
for f in $OUT/*.mp4 $OUT/*.mov $OUT/shots/*.mov; do
  frames=$(npx remotion ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height,r_frame_rate -of csv=p=0 "$f")
  errs=$(npx remotion ffmpeg -hide_banner -v error -i "$f" -f null - 2>&1 | wc -l | tr -d ' ')
  echo "$(basename $f): $frames decode_errors=$errs"
done
echo "DELIVERY_DONE"
