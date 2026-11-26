import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

function crc32(buffer, start, end) {
  let crc = 0xffffffff;
  for (let i = start; i < end; i++) {
    crc ^= buffer[i];
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}

try {
  const repoDir = dirname(fileURLToPath(import.meta.url));
  const source = join(repoDir, 'assets', 'entry.png');
  const png = readFileSync(source);
  if (png.length > 1048576) throw new Error(`PNG is ${png.length} bytes; limit is 1048576`);
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (png.length < 45 || !png.subarray(0, 8).equals(signature)) throw new Error('assets/entry.png has no valid PNG signature');

  let offset = 8;
  let width = 0;
  let height = 0;
  let sawIdat = false;
  let sawIend = false;
  let chunkIndex = 0;
  while (offset < png.length) {
    if (offset + 12 > png.length) throw new Error('PNG ends inside a chunk header');
    const length = png.readUInt32BE(offset);
    const typeStart = offset + 4;
    const dataStart = offset + 8;
    const chunkEnd = dataStart + length;
    if (chunkEnd + 4 > png.length) throw new Error('PNG ends inside a chunk');
    const type = png.toString('ascii', typeStart, typeStart + 4);
    const storedCrc = png.readUInt32BE(chunkEnd);
    if (crc32(png, typeStart, chunkEnd) !== storedCrc) throw new Error(`PNG ${type} chunk has a bad CRC`);
    if (chunkIndex === 0) {
      if (type !== 'IHDR' || length !== 13) throw new Error('PNG does not start with a valid IHDR chunk');
      width = png.readUInt32BE(dataStart);
      height = png.readUInt32BE(dataStart + 4);
      if (!width || !height || width > 1024 || height > 1024) {
        throw new Error(`PNG dimensions ${width}x${height} must be between 1x1 and 1024x1024`);
      }
    } else if (type === 'IHDR') {
      throw new Error('PNG contains more than one IHDR chunk');
    }
    if (type === 'IDAT') sawIdat = true;
    if (type === 'IEND') {
      if (length !== 0 || !sawIdat || chunkEnd + 4 !== png.length) throw new Error('PNG has an invalid or incomplete IEND');
      sawIend = true;
      offset = chunkEnd + 4;
      break;
    }
    offset = chunkEnd + 4;
    chunkIndex++;
  }
  if (!sawIdat || !sawIend || offset !== png.length) throw new Error('PNG is incomplete or has no image data');

  const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
  mkdirSync(outputDir, { recursive: true });
  writeFileSync(join(outputDir, 'entry.png'), png);
} catch (error) {
  console.error(`Entry failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
}
