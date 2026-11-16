#!/bin/zsh
# Delivery for the Blender v6.2 opening (run after scripts/final_v6_2.py --render). v6 outputs are untouched.
# Quality chain: Blender PNG (lossless, 8-bit sRGB) -> ONE encode per deliverable.
#   per shot : PNG -> ProRes 422 HQ (10-bit, BT.709)            and PNG -> H.264 (CRF 14, High, BT.709)
#   full     : Remotion PNG frames -> ProRes 422 HQ clean master (BT.709)
#              master + mix -> ProRes 422 HQ with PCM 24-bit audio (video stream copied, no re-encode)
#              master -> H.264 CRF 14 + AAC 320k (single lossy pass from the 10-bit master; replaces the old
#              JPEG-intermediate path in export.mjs)
#   audio    : export.mjs --only=stems -> mastered mix (-16 LUFS, -1 dBTP) + music / sfx stems, 48 kHz 24-bit
set -e
cd /Users/mohammadalqurain/Documents/Remotion-MotionGraphics
NAME=hasad-opening-blender-v6-2
ID=Hasad-Opening-Blender-v6-2-20s
OUT=exports/$NAME
mkdir -p $OUT/shots
typeset -A LEN DIR
LEN=(1A 90 1B 96 2A 66 2B 102 3A 84 3B 90 4A 120)
DIR=(1A blender_v6_2 1B blender_v6_2 2A blender_v6_2 2B blender_v6_2 3A blender_v6 3B blender_v6_2 4A blender_v6_2)
C709=(-color_primaries bt709 -color_trc bt709 -colorspace bt709)
ff() { npx remotion ffmpeg -hide_banner -loglevel error -y "$@"; }
echo "== frame check"
for s in 1A 1B 2A 2B 3A 3B 4A; do
  n=$(ls public/media/opening/${DIR[$s]}/$s/f_*.png | wc -l | tr -d ' ')
  [ "$n" = "${LEN[$s]}" ] && echo "ok $s $n (${DIR[$s]})" || { echo "MISSING $s $n/${LEN[$s]}"; exit 1; }
done
echo "== per-shot exports (Premiere)"
for s in 1A 1B 2A 2B 3A 3B 4A; do
  IN=public/media/opening/${DIR[$s]}/$s/f_%04d.png
  ff -framerate 30 -i $IN -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv422p10le" -c:v prores_ks -profile:v 3 -vendor apl0 $C709 \
     $OUT/shots/${NAME}_shot_${s}_ProRes422HQ.mov
  ff -framerate 30 -i $IN -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -preset slow -crf 14 -profile:v high -tune film \
     -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" $C709 -movflags +faststart $OUT/shots/${NAME}_shot_${s}.mp4
  echo "ok shot $s"
done
echo "== full composition: clean ProRes 422 HQ master"
npx remotion render src/videos/hasad-2026/entry.ts $ID $OUT/${NAME}_Clean_ProRes422HQ.mov --log=error \
  --config=src/audio/tools/remotion.export.config.ts --muted --codec=prores --prores-profile=hq --image-format=png \
  --pixel-format=yuv422p10le --color-space=bt709 --props='{"audioSolo":"all"}'
echo "== audio: mastered mix + stems"
node src/audio/tools/export.mjs --entry=src/videos/hasad-2026/entry.ts --id=$ID --name=$NAME --lufs=-16 --only=stems --stems=music,sfx
echo "== master with audio + H.264 from the master"
ff -i $OUT/${NAME}_Clean_ProRes422HQ.mov -i $OUT/${NAME}_Mix_48k24.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -shortest \
   $OUT/${NAME}_Master_ProRes422HQ.mov
ff -i $OUT/${NAME}_Clean_ProRes422HQ.mov -i $OUT/${NAME}_Mix_48k24.wav -map 0:v -map 1:a \
   -vf "format=yuv420p" -c:v libx264 -preset slow -crf 14 -profile:v high -tune film -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" $C709 \
   -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart $OUT/${NAME}_Final.mp4
echo "== verification"
for f in $OUT/*.mp4 $OUT/*.mov $OUT/shots/*.mov $OUT/shots/*.mp4; do
  info=$(npx remotion ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height,r_frame_rate,pix_fmt,color_space,bit_rate -of csv=p=0 "$f")
  errs=$(npx remotion ffmpeg -hide_banner -v error -i "$f" -f null - 2>&1 | wc -l | tr -d ' ')
  echo "$(basename $f): $info decode_errors=$errs"
done
npx remotion ffmpeg -hide_banner -nostats -i $OUT/${NAME}_Final.mp4 -vn -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input Integrated|Input True Peak" || true
echo "DELIVERY_DONE"
