#!/bin/sh
# Real render of tools/entry.html at 1024x1024 in headless Chrome -> assets/entry.png
D=$(cd "$(dirname "$0")/.." && pwd)
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1024,1024 --screenshot=/tmp/_n25.png "file://$D/tools/entry.html" >/dev/null 2>&1
convert /tmp/_n25.png -strip -colors 256 PNG8:"$D/assets/entry.png" 2>/dev/null || cp /tmp/_n25.png "$D/assets/entry.png"
