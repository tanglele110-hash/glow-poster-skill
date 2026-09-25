#!/usr/bin/env python3
"""Compose the optional horizontal poster layout: python compose.py config.json.

Required: background, output. Optional: canvas [1376,1824], title, subtitle,
greeting (1-2 lines), attribution, font, fonts (title/subtitle/greeting/attribution),
scene_bbox [left,top,right,bottom] as visually measured normalized coordinates,
and overwrite (false by default). Paths resolve against config.json.
Writes PNG and .layout.json. Automatic checks do not replace visual approval.
"""
import argparse
import json
import os
from collections import deque
from functools import lru_cache
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
    from fontTools.ttLib import TTFont
except ImportError as exc:
    raise SystemExit(f'Missing dependency: {exc.name}. Install requirements.txt with this Python interpreter.') from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / 'assets' / 'ChienChia-F.ttf'
FALLBACK_FONT = ROOT / 'assets' / 'Iansui-Regular.ttf'
TITLE_FONT = ROOT / 'assets' / 'qiji.ttf'


class LayoutError(ValueError):
    pass


def local_kaiti_font():
    windows_dir=os.environ.get('WINDIR')
    if windows_dir:
        candidate=Path(windows_dir)/'Fonts/simkai.ttf'
        if candidate.is_file():
            return candidate
    return None


@lru_cache(maxsize=24)
def font_coverage(font_path):
    with TTFont(font_path, lazy=True) as tt:
        return frozenset((tt.getBestCmap() or {}).keys())


def check_coverage(font_paths, texts):
    if isinstance(font_paths,Path):
        font_paths=[font_paths]
    covered=set().union(*(font_coverage(p) for p in font_paths))
    missing = sorted({c for text in texts for c in text if not c.isspace() and ord(c) not in covered})
    if missing:
        raise LayoutError(f'Font stack has no glyphs for: {" ".join(missing)}. '
                          'Keep the requested wording; explicitly choose a font that covers it.')
    return {c:next(p.name for p in font_paths[1:] if ord(c) in font_coverage(p))
            for text in texts for c in text if not c.isspace() and ord(c) not in font_coverage(font_paths[0])}


def detect_glow(bg):
    """Find sustained bright components relative to row-local outer background.

    Row-local baselines tolerate vertical tonal gradients. Filtering and connected
    components reject grain and isolated speckles. No guessed-edge fallback.
    """
    W, H = bg.size
    sw, sh = 240, round(H * 240 / W)
    small = bg.resize((sw, sh)).convert('RGB').filter(ImageFilter.GaussianBlur(1.1))
    arr = np.asarray(small, dtype=float)
    lum = arr @ np.array([.2126, .7152, .0722])
    side = round(sw * .1)
    baseline = np.median(np.concatenate((lum[:, :side], lum[:, -side:]), axis=1), axis=1)
    mask = lum > baseline[:, None] + 18
    mask[:round(sh*.23)] = False
    mask[round(sh*.97):] = False
    mask[:, :round(sw*.1)] = False
    mask[:, round(sw*.9):] = False
    seen = np.zeros(mask.shape, dtype=bool)
    components = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        queue = deque([(int(y), int(x))])
        seen[y, x] = True
        points = []
        while queue:
            cy, cx = queue.popleft()
            points.append((cy, cx))
            for ny, nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
                if 0 <= ny < sh and 0 <= nx < sw and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx] = True
                    queue.append((ny,nx))
        if len(points) >= sw * sh * .002:
            components.extend(points)
    if len(components) < sw * sh * .015:
        raise LayoutError('No reliable central glow detected. Inspect/regenerate the background, '
                          'or supply a visually measured scene_bbox; no estimated fallback is used.')
    ys, xs = zip(*components)
    return [max(0,(min(xs)-2)/sw), max(0,(min(ys)-2)/sh),
            min(1,(max(xs)+3)/sw), min(1,(max(ys)+3)/sh)]


def scene_bounds(bg, override=None):
    box = override if override is not None else detect_glow(bg)
    if not isinstance(box, (list,tuple)) or len(box) != 4 or any(not isinstance(n,(int,float)) for n in box):
        raise LayoutError('scene_bbox must contain four normalized numbers.')
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise LayoutError('Invalid normalized scene_bbox.')
    if top < .255 or bottom > .76 or left < .10 or right > .90:
        raise LayoutError(f'Glow extends into a reserved zone: {box}. Regenerate with the light inside '
                          'x=20-80%, y=30-73%; do not move the poem into the light.')
    W,H=bg.size
    return [round(left*W),round(top*H),round(right*W),round(bottom*H)]


def line_metrics(draw, text, stack, tracking=0):
    runs, boxes, x = [], [], 0.0
    for ch in text:
        font=next((font for font,cmap in stack if ord(ch) in cmap),stack[0][0])
        runs.append((x,ch,font))
        if not ch.isspace():
            boxes.append(draw.textbbox((x,0),ch,font=font,anchor='ls'))
        x += draw.textlength(ch,font=font)+tracking
    if not boxes:
        return (0,0,0,0), runs
    return (min(b[0] for b in boxes),min(b[1] for b in boxes),
            max(b[2] for b in boxes),max(b[3] for b in boxes)),runs


def fit_lines(draw, lines, font_paths, width, max_size, min_size, gap, max_height=None, tracking_ratio=0):
    for size in range(round(max_size),round(min_size)-1,-1):
        stack=[(ImageFont.truetype(str(p),size),font_coverage(p)) for p in font_paths]
        tracking=round(size*tracking_ratio,2)
        metrics=[line_metrics(draw,line,stack,tracking) for line in lines]
        height=sum(m[0][3]-m[0][1] for m in metrics)+gap*max(0,len(lines)-1)
        if max((m[0][2]-m[0][0] for m in metrics),default=0)<=width and (max_height is None or height<=max_height):
            return dict(size=size,metrics=metrics,height=height,gap=gap)
    raise LayoutError('Text does not fit at the minimum readable size. Supply shorter copy or a separate layout; '
                      'no truncation or hidden overflow is allowed.')


def render_lines(draw, lines, layout, y, W, role, alpha=255, center_x=None):
    records=[]
    for text,(box,runs) in zip(lines,layout['metrics']):
        width,height=box[2]-box[0],box[3]-box[1]
        x=(W/2 if center_x is None else center_x)-width/2
        for offset,run,font in runs:
            draw.text((x-box[0]+offset,y-box[1]),run,font=font,anchor='ls',fill=(255,255,255,alpha))
        records.append(dict(role=role,text=text,font_size=layout['size'],
                            bbox=[round(x,2),round(y,2),round(x+width,2),round(y+height,2)]))
        y+=height+layout['gap']
    return records


def contrast(bg, bbox):
    x0,y0,x1,y1=[round(n) for n in bbox]
    pixels=np.asarray(bg.crop((x0,y0,x1,y1)).resize((32,12)).convert('RGB'),dtype=float)/255
    linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)
    lum=linear @ np.array([.2126,.7152,.0722])
    return round(float(1.05/(np.percentile(lum,90)+.05)),2)


def compose(config_path):
    config_path=Path(config_path).resolve()
    cfg=json.loads(config_path.read_text(encoding='utf-8-sig'))
    if cfg.get('layout','horizontal')!='horizontal':
        raise LayoutError('compose.py supports horizontal layout only. Use the vertical complete-image prompt and text manifest.')
    base=config_path.parent
    def resolve(value):
        p=Path(value)
        return (p if p.is_absolute() else base/p).resolve()
    for key in ('background','output'):
        if not isinstance(cfg.get(key),str) or not cfg[key]:
            raise LayoutError(f'Missing or invalid {key}.')
    background,output=resolve(cfg['background']),resolve(cfg['output'])
    report_path=output.with_suffix('.layout.json')
    if output.suffix.lower() != '.png':
        raise LayoutError('Output must have a .png extension.')
    if output == background or output.is_relative_to(ROOT):
        raise LayoutError('Output must be outside the Skill package and must not replace the background.')
    if not cfg.get('overwrite',False) and (output.exists() or report_path.exists()):
        raise LayoutError(f'Output already exists: {output}. Use a new path or explicitly set overwrite=true.')
    greeting=cfg.get('greeting',[])
    if not isinstance(greeting,list) or not 1<=len(greeting)<=2 or any(not isinstance(t,str) or not t.strip() for t in greeting):
        raise LayoutError('greeting must be one or two nonempty lines; explicit line breaks are preserved.')
    texts={'title':[cfg.get('title','中秋佳節')],'subtitle':[cfg.get('subtitle','MID-AUTUMN FESTIVAL')],
           'greeting':greeting,'attribution':[cfg.get('attribution','')],'signature':[cfg.get('signature','')]}
    if any(not isinstance(t,str) or '\n' in t or '\r' in t for lines in texts.values() for t in lines):
        raise LayoutError('Each text field must be one string without embedded newlines.')
    default_font=resolve(cfg['font']) if cfg.get('font') else DEFAULT_FONT
    role_fonts=cfg.get('fonts',{})
    title_preset=cfg.get('title_font','qiji')
    if title_preset not in ('qiji','kaiti'):
        raise LayoutError('title_font must be qiji or kaiti; use fonts.title for a custom font path.')
    if 'title' not in role_fonts:
        title_font=TITLE_FONT if title_preset=='qiji' else local_kaiti_font()
        if title_font is None or not title_font.is_file():
            raise LayoutError(f'Title font unavailable: {title_font}. Choose an installed font with fonts.title.')
        role_fonts=dict(role_fonts,title=str(title_font))
    fallback=[resolve(p) for p in cfg.get('fallback_fonts',[])] if 'fallback_fonts' in cfg else [FALLBACK_FONT]
    fonts={role:[resolve(role_fonts[role]) if role in role_fonts else default_font]+fallback for role in texts}
    substitutions={}
    for role,lines in texts.items():
        substitutions[role]=check_coverage(fonts[role],lines)
    with Image.open(background) as original:
        bg=ImageOps.exif_transpose(original).convert('RGB')
    canvas=cfg.get('canvas',list(bg.size))
    if not isinstance(canvas,list) or len(canvas)!=2 or any(type(n) is not int or n<600 or n>8000 for n in canvas):
        raise LayoutError('canvas must be [width,height], each between 600 and 8000 pixels.')
    W,H=canvas
    if not .70<=W/H<=.80:
        raise LayoutError('This reference layout supports portrait ratios near 3:4 only.')
    input_size=list(bg.size)
    if abs((bg.width/bg.height)/(W/H)-1)>.025:
        raise LayoutError(f'Background ratio {bg.size} differs too much from canvas {canvas}; regenerate without stretching.')
    if bg.size!=(W,H):
        bg=ImageOps.fit(bg,(W,H),method=Image.Resampling.LANCZOS)
    scene=scene_bounds(bg,cfg.get('scene_bbox'))
    img=bg.copy()
    draw=ImageDraw.Draw(img,'RGBA')
    records=[]
    max_width=.86*W
    # Horizontal layout positions use visible ink bounds, independent of font ascenders.
    top_end=0
    for role,y,size,minimum,tracking,alpha in (
        ('title',.080*H,.105*W,.085*W,0,255),
        ('subtitle',.186*H,.036*W,.028*W,.389,235),
    ):
        lines=[t for t in texts[role] if t]
        if lines:
            lay=fit_lines(draw,lines,fonts[role],max_width,size,minimum,0,tracking_ratio=tracking)
            row=render_lines(draw,lines,lay,y,W,role,alpha)
            if records and y<top_end+.01*H:
                raise LayoutError('Title and subtitle overlap.')
            records+=row
            top_end=row[-1]['bbox'][3]
    if top_end+.025*H>scene[1]:
        raise LayoutError('Glow is too close to the header; regenerate the background.')
    signature=cfg.get('signature','')
    if signature:
        max_width=.74*W
    attrs=[t for t in texts['attribution'] if t]
    attr_layout=fit_lines(draw,attrs,fonts['attribution'],max_width,.030*W,.022*W,0) if attrs else None
    attr_height=attr_layout['height'] if attr_layout else 0
    attr_gap=.020*H if attrs else 0
    poem_top=max(.783*H,scene[3]+.038*H)
    available=.925*H-poem_top-attr_gap-attr_height
    quote_layout=fit_lines(draw,greeting,fonts['greeting'],max_width,.055*W,.042*W,.014*H,max_height=available)
    records+=render_lines(draw,greeting,quote_layout,poem_top,W,'greeting')
    if attrs:
        records+=render_lines(draw,attrs,attr_layout,poem_top+quote_layout['height']+attr_gap,W,'attribution',235)
    if signature:
        chars=list(signature)
        signing=fit_lines(draw,chars,fonts['signature'],.045*W,.027*W,.020*W,.004*H,max_height=.18*H)
        rows=render_lines(draw,chars,signing,.925*H-signing['height'],W,'signature',235,center_x=.91*W)
        for row in rows:
            a=row['bbox']
            for b in [scene]+[r['bbox'] for r in records]:
                if a[0]<b[2]+.01*W and a[2]>b[0]-.01*W and a[1]<b[3]+.01*H and a[3]>b[1]-.01*H:
                    raise LayoutError('Signature collides with text or glow; adjust the layout without deleting copy.')
        records+=rows
    for r in records:
        x0,y0,x1,y1=r['bbox']
        if x0<.06*W or x1>.94*W or y0<.05*H or y1>.94*H:
            raise LayoutError(f'Text leaves the safe area: {r["role"]}.')
        r['white_contrast_p90']=contrast(bg,r['bbox'])
        if r['white_contrast_p90']<1.8:
            raise LayoutError(f'White text is too faint in the {r["role"]} zone '
                              f'(contrast {r["white_contrast_p90"]}). Keep the selected base color; review a typography adjustment with the user.')
    report=dict(status='automatic_checks_passed_visual_review_required',canvas=canvas,input_size=input_size,
                background=str(background),output=str(output),scene_bbox_pixels=scene,
                scene_detection='manual_measured' if cfg.get('scene_bbox') is not None else 'row_local_components',
                text=records,font_fallbacks=substitutions,
                font_files={role:[str(p) for p in paths] for role,paths in fonts.items()},
                checks=dict(glyph_coverage=True,safe_margins=True,scene_clearance=True,no_truncation=True),
                visual_review_required=['window shape and motif match selection','soft translucent cast shadows',
                                        'no generated background letters','wording and author match the selection',
                                        'white text comfortably readable at normal viewing size'])
    output.parent.mkdir(parents=True,exist_ok=True)
    img.save(output,format='PNG')
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config')
    args=parser.parse_args()
    try:
        result=compose(args.config)
    except (LayoutError,KeyError,OSError,ValueError) as exc:
        parser.exit(2,f'Compose failed: {exc}\n')
    print(json.dumps(dict(output=result['output'],canvas=result['canvas'],status=result['status']),ensure_ascii=False))
