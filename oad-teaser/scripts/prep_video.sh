#!/usr/bin/env bash
# Converts the raw screen recordings to 30 fps CFR, no audio, cropped to the
# active picture with the browser scrollbar removed.
# Drop new recordings into assets/video/ with the same file names and re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
# Brief: active picture is crop=1920:888:0:96. The scrollbar occupies x >= 1903,
# so we keep 1900 px of width. Coordinates stay left/top anchored.
CROP="crop=1900:888:0:96"
mkdir -p assets/video/prepped
for n in home_hero this_week roadmap_scroll; do
  ffmpeg -v error -y -i "assets/video/$n.mp4" -an \
    -vf "fps=30,$CROP" -c:v libx264 -preset slow -crf 12 -g 1 \
    -pix_fmt yuv420p -movflags +faststart "assets/video/prepped/$n.mp4"
  echo "$n: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames,r_frame_rate,width,height -of csv=p=0 assets/video/prepped/$n.mp4)"
done
