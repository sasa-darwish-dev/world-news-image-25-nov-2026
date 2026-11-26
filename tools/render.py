#!/usr/bin/env python3
"""Offline SVG renderer. Layout mirrors entry.html; text and icons come from it.

Use installed librsvg/Cairo directly: Chromium cannot launch within this
workspace's socket sandbox. No browser, network, or web server is needed.
"""
from copy import deepcopy
import ctypes as C
from ctypes.util import find_library
from pathlib import Path
from lxml import etree, html
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'assets' / 'entry.png'


def element(parent, tag, **attrs):
    return etree.SubElement(parent, tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, content, size, weight=400, colour='#172c34', spacing=0, condensed=True):
    face = 'DejaVuSansCondensed' if condensed else 'DejaVuSans'
    font = ImageFont.truetype(f"{face}{'-Bold' if weight >= 600 else ''}.ttf", size)
    width = font.getlength(content) + spacing * (len(content) - 1)
    if x + width > (488 if x == 56 else 984):
        raise ValueError(f'Text overflows: {content} ({width:.1f}px)')
    node = element(parent, 'text', x=x, y=y, font_size=size, font_weight=weight,
                   fill=colour, letter_spacing=spacing,
                   font_family='DejaVu Sans', font_stretch='condensed' if condensed else 'normal')
    node.text = content


def render(vector):
    """Only in-process SVG/Cairo calls, with explicit C argument signatures."""
    rsvg = C.CDLL(find_library('rsvg-2'))
    cairo = C.CDLL(find_library('cairo'))
    gobject = C.CDLL(find_library('gobject-2.0'))
    rsvg.rsvg_handle_new_from_data.argtypes = [C.c_char_p, C.c_size_t, C.c_void_p]
    rsvg.rsvg_handle_new_from_data.restype = C.c_void_p
    rsvg.rsvg_handle_render_cairo.argtypes = [C.c_void_p, C.c_void_p]
    rsvg.rsvg_handle_render_cairo.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    gobject.g_object_unref.argtypes = [C.c_void_p]
    handle = rsvg.rsvg_handle_new_from_data(vector, len(vector), None)
    if not handle:
        raise RuntimeError('Invalid SVG')
    surface = cairo.cairo_image_surface_create(0, 1024, 1024)
    context = cairo.cairo_create(surface)
    try:
        if not rsvg.rsvg_handle_render_cairo(handle, context):
            raise RuntimeError('SVG render failed')
        if cairo.cairo_surface_write_to_png(surface, str(DEST).encode()):
            raise RuntimeError('PNG write failed')
    finally:
        cairo.cairo_destroy(context)
        cairo.cairo_surface_destroy(surface)
        gobject.g_object_unref(handle)


def main():
    source = html.parse(str(ROOT / 'tools' / 'entry.html'))
    svg = etree.Element('svg', nsmap={None: 'http://www.w3.org/2000/svg'},
                        width='1024', height='1024', viewBox='0 0 1024 1024')
    element(svg, 'style').text = '.line{fill:none;stroke:currentColor;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}'
    element(svg, 'rect', width=1024, height=1024, fill='#f3f0e9')
    text(svg, 32, 108, 'WORLD NEWS', 86, 800, spacing=-5, condensed=False)
    text(svg, 32, 158, 'WEDNESDAY 25 NOVEMBER 2026', 30, 700, spacing=.3)
    element(svg, 'rect', x=32, y=176, width=960, height=4, fill='#172c34')
    globe = deepcopy(source.xpath('//svg[@class="globe"]')[0])
    globe.attrib.pop('viewbox', None)
    globe.attrib.update(dict(x='906', y='35', width='82', height='82', viewBox='0 0 100 100'))
    svg.append(globe)
    for index, article in enumerate(source.xpath('//article')):
        x = 32 + (index % 2) * 488
        y = 202 + (index // 2) * 266
        accent = article.get('style').split(':')[1]
        element(svg, 'rect', x=x, y=y, width=472, height=250, fill='#fffdf8', stroke='#d4d6cf')
        element(svg, 'rect', x=x, y=y, width=472, height=5, fill=accent)
        region = article.xpath('.//div[@class="region"]')[0].text
        country = article.xpath('.//div[@class="country"]')[0].text
        text(svg, x+24, y+45, region, 26, 800, accent, 1.4, False)
        text(svg, x+24, y+80, country, 26, 800)
        icon = deepcopy(article.xpath('.//svg')[0])
        icon.attrib.update(dict(x=str(x+346), y=str(y+19), width='105', height='88', color=accent))
        icon.set('viewBox', icon.attrib.pop('viewbox', '0 0 110 92'))
        svg.append(icon)
        headline = article.xpath('.//h2')[0]
        lines = [headline.text] + [br.tail for br in headline]
        assert len(' '.join(lines).split()) <= 6
        for row, line in enumerate(lines):
            text(svg, x+24, y+140+row*46, line, 40, 700, spacing=-1.2)
        detail = article.xpath('.//p[@class="detail"]')[0].text
        assert len(detail.split()) <= 10
        spacing = float(article.xpath('.//p[@class="detail"]')[0].get("data-spacing", "-.45"))
        text(svg, x+24, y+226, detail, 26, spacing=spacing)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    vector = etree.tostring(svg, xml_declaration=True, encoding='utf-8')
    (ROOT / 'assets' / 'entry.svg').write_bytes(vector)
    render(vector)
    with Image.open(DEST) as im:
        im.convert('RGB').save(DEST, optimize=True, compress_level=9)
    with Image.open(DEST) as im:
        assert im.size == (1024, 1024)
        im.resize((300, 300), Image.Resampling.LANCZOS).save(ROOT / 'tools' / 'preview.png')
    assert DEST.stat().st_size <= 1024 * 1024
    print(f'{DEST.relative_to(ROOT)}: 1024×1024, {DEST.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
