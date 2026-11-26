# Wednesday 25 November 2026 — World news

A dense, self-contained editorial front page covering 37 stories from the verified 25 November fact list: three lead reports, thirteen illustrated mid-tier stories and twenty-one source-tagged briefs. It includes six key numbers, a UTC timeline, region counts, a numbered map and a date-check footer. Story copy is written directly into the HTML; rendering does not load the fact file or use the network.

Render the 1024 × 1024 PNG with local Google Chrome and ImageMagick:

```sh
sh tools/render.sh
```

The Node 22 entry point validates `assets/entry.png` and copies it to `/output/entry.png`, or to the directory set by `MAKEFUN_OUTPUT_DIR`.
