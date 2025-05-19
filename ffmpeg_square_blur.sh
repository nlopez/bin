#!/usr/bin/env bash
set -euo pipefail
set -o xtrace

# Check if mediainfo is installed
if ! command -v mediainfo &> /dev/null; then
  echo "Error: mediainfo is not installed. Please install it and try again."
  exit 1
fi

infile="${1}"
infile="$(readlink -f "${infile}")"


# Allow x & y dimensions to be passed as arguments
x="${2:-$(mediainfo "${infile}" --Output=JSON | jq -r '.media.track[] | select(.["@type"] == "Image") | [(.Width|tonumber), (.Height|tonumber)] | max')}"
y="${3:-$x}"

outfile="${infile%.*}_${x}x${y}_boxblur25.${infile##*.}"


# transparent background
# ffmpeg -i "$1" -vf "scale='if(gt(iw,ih),max(ih\,iw),-1)':'if(gt(iw,ih),-1,max(ih\,iw))',pad=iw:iw:(ow-iw)/2:(oh-ih)/2:color=0x00000000,boxblur=10:1" -pix_fmt rgba -update true -frames:v 1 "${1%.*}_square.png"

# blurred background
ffmpeg -y -v verbose -i "$infile" \
-filter_complex "[0:v]split=2[blur][vid]; \
[blur]scale=${x}:${y}:force_original_aspect_ratio=increase,crop=${x}:${y},boxblur=25[bg]; \
[vid]scale=${x}:${y}:force_original_aspect_ratio=decrease[ov]; \
[bg][ov]overlay=(W-w)/2:(H-h)/2" \
-update true -frames:v 1 "$outfile"

optipng "$outfile"
