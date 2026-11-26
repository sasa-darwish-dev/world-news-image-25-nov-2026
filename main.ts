import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// The checked-in artwork makes each execution independent of fonts and browsers.
const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
const repoDir = dirname(fileURLToPath(import.meta.url));
mkdirSync(outputDir, { recursive: true });
copyFileSync(join(repoDir, 'assets', 'entry.png'), join(outputDir, 'entry.png'));
