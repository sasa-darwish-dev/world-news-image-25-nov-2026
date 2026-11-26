# world-news-image-25-nov-2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/sasa-darwish-dev/world-news-image-25-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/sasa-darwish-dev/world-news-image-25-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A dense editorial front page for Wednesday 25 November 2026: 34 stories from that day's reports by Reuters, AP, BBC, Al Jazeera, Xinhua and others. Three lead stories (US tariff proposal, the AI-led market sell-off, Pakistan's first astronaut on China's Tiangong station), ten mid stories, 21 regional briefs, five key numbers, a numbered world map and a date check. Everything was reported on 25 November 2026 and the facts are listed in `tools/facts.json`.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```


## Notes

Run with Node 22:

```sh
node main.ts
```

The program copies the bundled artwork to `/output/entry.png`. Set `MAKEFUN_OUTPUT_DIR` to choose another directory:

```sh
MAKEFUN_OUTPUT_DIR=out node main.ts
```

To regenerate the 1024 x 1024 PNG from `tools/entry.html` (self-contained HTML and inline SVG, installed fonts only), run `sh tools/render.sh` with headless Google Chrome and ImageMagick. `main.ts` checks that the PNG is valid, at most 1024 x 1024 and at most 1 MiB, then copies it to the output directory. Everything runs offline.
