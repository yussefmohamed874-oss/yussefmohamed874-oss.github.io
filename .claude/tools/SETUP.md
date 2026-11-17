# إعادة تجهيز الأدوات في جلسة جديدة (الكود فقط محفوظ هنا)
المجلد المستهدف: /home/user/montage-tools (خارج مستودع الموقع)

1. نسخ الكود: `cp -r .claude/tools/* /home/user/montage-tools/ && mkdir -p /home/user/montage-tools/{models,work,out,ref}`
2. بيئة بايثون: `python3 -m venv /home/user/montage-tools/.venv && /home/user/montage-tools/.venv/bin/pip install faster-whisper==1.2.1 "av==18.0.0"`  (av 19 يكسر faster-whisper)
3. نموذج Whisper: huggingface.co محجوب ما لم يضيفه المستخدم لإعدادات الشبكة (Allowed domains).
   - بعد السماح: `Systran/faster-whisper-large-v3` في `models/`، وغيّر MODEL_DIR في mt.py.
   - البديل الحالي: حزم npm `@skillninja/shortmovie-telop-model-p0..p3` (whisper small CT2، طرف ثالث) تُجمَّع model.bin.part0..3 بالترتيب إلى models/whisper-small-ct2-int8/model.bin.
4. Remotion: `cd remotion && npm i -E remotion@4.0.250 @remotion/cli@4.0.250 @remotion/renderer@4.0.250 @remotion/three@4.0.250 react@18.3.1 react-dom@18.3.1 three@0.160.0 @react-three/fiber@8.15.19 @fontsource/cairo@5.0.18 typescript@5.4.5 @types/react@18.3.3 @types/react-dom@18.3.0 @types/three@0.160.0`
5. Render: `npx remotion render src/index.tsx Reel ../out/renders/x.mp4 --browser-executable=/opt/pw-browsers/chromium`
   (يحتاج src/data/test.json وclip في public/clips عبر `scripts/prep_clip.sh`)
