#!/bin/zsh
# Exports every deliverable of the Riyadh dams report. Run from the project root:  zsh src/videos/riyadh-dams-2026/export-all.sh
set -e
E=src/videos/riyadh-dams-2026/entry.ts
X=exports/riyadh-dams-2026
mkdir -p $X/sections $X/dams $X/alpha
H() { PREVIEW=1 npx remotion render $E $1 $2 --crf=16 --jpeg-quality=95 --log=error; echo "done $2"; }   # H.264 MP4
A() { npx remotion render $E $1 $2 --log=error; echo "done $2"; }                                         # ProRes 4444 + alpha (global config)
H RD-Master $X/Riyadh_Dams_Rainfall_Report_Nov2026.mp4
H RD-Master-NoMusic $X/Riyadh_Dams_Rainfall_Report_Nov2026_NoMusic.mp4
H RD-Intro $X/sections/01_Intro.mp4
H RD-Stats $X/sections/02_Stats.mp4
H RD-Chart $X/sections/03_Chart.mp4
H RD-Outro $X/sections/04_Outro.mp4
H RD-EndCard $X/sections/05_EndCard.mp4
names=(Harimla AlGhat AlBarah Sulbukh AlFuhaihil KhanqatUrwa AlKalbi AlHariqAlWashm Rughbah Uthaythiyah AlTamriyah AlKharuiyah AlDahinah)
for i in {1..13}; do n=$(printf %02d $i); H RD-Dam-$n $X/dams/Dam_${n}_${names[$i]}.mp4; done
A RD-Intro-Alpha $X/alpha/01_Intro_Alpha.mov
A RD-Stats-Alpha $X/alpha/02_Stats_Alpha.mov
A RD-Chart-Alpha $X/alpha/03_Chart_Alpha.mov
A RD-Outro-Alpha $X/alpha/04_Outro_Alpha.mov
A RD-EndCard-Alpha $X/alpha/05_EndCard_Alpha.mov
for i in {1..13}; do n=$(printf %02d $i); A RD-Dam-$n-Alpha $X/alpha/Dam_${n}_${names[$i]}_Alpha.mov; done
echo ALL DONE
