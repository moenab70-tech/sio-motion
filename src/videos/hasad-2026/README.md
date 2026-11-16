# Initiative film «بصمة إنجاز & نمو» (provisional title; formerly «حصاد التميز 2026»)

1920×1080 · **25fps** · RTL · solid navy background. The film is a **list of scenes** in `config.ts` (`scenes`).

## Order (Corporate Communications directions)
1. Intro: initiative name · 2. About the initiative · 3. «منجزات دولية» (international achievements) title · 4. USA – PMI · 5. France – ICID/WatSave
6. International accreditations – Eng. Abdulrahman Al-Thumairi (the certificate is a training-workshop attendance certificate, and its caption says so) · 7. International accreditations – Dr. Wadha Al-Rashidi
8. «منجزات محلية» (local achievements) title · 9. Nadhee index · 10. Outro + the official outro (`sio-social-outro-4444.mov`, 5 s) over the film background

## Adding a new achievement later
Copy an `award` scene in `config.ts`, change its text and images, and place it in the list. The total length, the transitions, the sound-effect timings and the separate per-scene export all update automatically.

## Images
`public/media/images/hasad-2026/`. Original images, never generated. Each one is shown whole at its original ratio inside **uniform frames** (same size and inner margin) over a blurred copy of itself.
- `wocat-workshop-certificate-thumairi.png`: from the original PDF (200 dpi); only the black scanning strip at the bottom was trimmed.
- `wadha-alrashedi-jury-member.png`: the original as-is. `...-detail.png`: a crop of the same image (the person + name + title) so the text reads clearly.

## Compositions (entry: `src/videos/hasad-2026/entry.ts`)
- `Initiative-Film`: picture only · `Initiative-Film-Final`: picture + music + sound effects (`audioSolo`: all | music | sfx)
- `Initiative-S01-intro` … `Initiative-S10-outro`: each scene on its own, without transitions or audio (for Premiere)

## Export
- Combined preview: `PREVIEW=1 npx remotion render src/videos/hasad-2026/entry.ts Initiative-Film-Final out/initiative-2026/preview.mp4`
- Separate scenes (ProRes 422 HQ): `npx remotion render src/videos/hasad-2026/entry.ts Initiative-S01-intro out/initiative-2026/scenes/S01-intro.mov --codec=prores --prores-profile=hq --pixel-format=yuv422p10le --image-format=png --muted`
- Separate audio: `npx remotion render ... Initiative-Film-Final out/.../music.wav --codec=wav --props='{"audioSolo":"music"}'` (and likewise `sfx`)

## Backup
A copy of the files from before this update: `backups/hasad-2026-before-basma/`.
