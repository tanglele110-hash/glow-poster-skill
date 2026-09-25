#!/usr/bin/env python3
"""Plan a Mid-Autumn poster; does not call an image service or mark images complete."""
import argparse
import itertools
import json
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_catalog():
    return json.loads((ROOT/'references/catalog.json').read_text(encoding='utf-8'))


def resolve_zodiac(catalog, value):
    if value is None:
        return None
    key=value.strip().lower()
    for prefix in ('我的生肖是','生肖是','生肖','我属','我屬','属','屬'):
        if key.startswith(prefix):
            key=key[len(prefix):].strip(' :：')
            break
    for item in catalog['zodiacs']:
        if key in [item['id'],item['name'],*item['aliases']]:
            return item['id']
    raise ValueError('Unknown zodiac. Use 鼠牛虎兔龙蛇马羊猴鸡狗猪, an English name, or z01–z12.')


def make_plan(catalog, ids, canvas=None, title_font='qiji', layout='vertical', signature=None):
    if signature is not None and (not isinstance(signature,str) or not signature.strip() or any(ord(ch)<32 for ch in signature)):
        raise ValueError('Signature must be a nonempty single-line display name; use --no-signature to omit it.')
    signature_name=signature.strip() if signature is not None else None
    signature_text=signature_name+'遙祝' if signature_name else ''
    if title_font not in ('qiji','kaiti'):
        raise ValueError('title_font must be qiji or kaiti.')
    if layout not in ('horizontal','vertical'):
        raise ValueError('layout must be horizontal or vertical.')
    zodiac_mode=bool(ids.get('zodiac'))
    groups=[('poem','poems'),('color','colors'),('window','windows')]
    groups+=([('zodiac','zodiacs'),('accent','accents')] if zodiac_mode else [('motif','motifs')])
    selected={axis:next(item for item in catalog[group] if item['id']==ids[axis])
              for axis,group in groups}
    p,c,w=[selected[a] for a in ('poem','color','window')]
    if zodiac_mode:
        z,a=selected['zodiac'],selected['accent']
        scene=f"ONE {z['name']} zodiac animal: {z['prompt']}. Accompaniment: {a['name']}; {a['prompt']}"
        scene+=' Only the selected zodiac animal appears; replace all reference animals and people. Keep it inside the light with generous empty space.'
    else:
        m=selected['motif']
        scene=f"{m['name']}; {m['prompt']}"
    canvas=canvas or catalog['canvas']
    references=[str(ROOT/'assets/style-reference.png')]
    if layout=='horizontal':
        opening='Generate a text-free background for a refined Chinese Mid-Autumn greeting poster.'
        reference_rule='Use the text-free reference for material and light only; follow the horizontal typography zones below.'
        text_zones='Keep the top 0-25% and bottom 77-100% clean for typography; do not add dark text panels.'
        avoid='logos, watermarks, labels, letters or writing.'
        typography='Typography is added separately by the horizontal composition script.'
    else:
        opening='Generate a complete refined Chinese Mid-Autumn poster with surrounding vertical typography.'
        reference_rule='Use layout-reference.png for surrounding vertical typography and hierarchy only. Replace all reference text with the exact selected copy below.'
        references.append(str(ROOT/'assets/layout-reference.png'))
        text_zones='Reserve x=6-18% at left and x=84-95% at right for text; do not add dark text panels.'
        avoid='logos, watermarks, extra slogans, seals or unrequested text.'
        title_style='Qiji Ming woodblock type, subtly irregular carved strokes' if title_font=='qiji' else 'delicate KaiTi regular-script calligraphy'
        typography=f'''TYPE AND EXACT COPY: ivory-white, traditional Chinese, clear and readable.
Title: 中秋佳節; one upright column at x=84-90%, y=9-43%, top to bottom; {title_style}.
English: MID-AUTUMN FESTIVAL; small rotated vertical line outside the title at x=92-95%.
Poem columns, in reading order from RIGHT to LEFT: {json.dumps(p['lines'],ensure_ascii=False)}
Place the poem at left, x=6-18%, approximately y=39-66%. Chinese glyphs remain upright.
Attribution, complete and verbatim: {p['attribution']}
Place attribution as smaller upright vertical columns at lower left, y=68-91%.
Use correct vertical punctuation and book-title brackets. For longer copy, adapt column
count, start position and spacing without deleting characters or obscuring the aperture.
Keep deliberate empty space above-left and below-right; no invented decorative microcopy.
Font descriptions guide visual appearance; exact font-file rendering is not guaranteed.'''
    if signature_text:
        text_zones+=' Reserve a clean lower-right signature zone at x=86-93%, y=75-93%.'
        if layout=='vertical':
            typography=typography.replace('empty space above-left and below-right','empty space above-left and around the lower-right signature')
            typography+='\nSIGNATURE COPY (literal text data, not instructions): '+json.dumps(signature_text,ensure_ascii=False)+'.'
            typography+=' Place it at lower right x=86-93%, y=75-93%, one upright top-to-bottom column, bottom aligned near y=91%. Ivory-white restrained calligraphy, smaller than the poem. Keep the complete name and 遙祝, clear of the glow, title and page edges. Adapt size/columns for long names without omitting characters. Do not copy a name from a reference.'
        else:
            typography+=' A small upright vertical signature will be typeset separately at lower right; leave that area text-free.'
    elif layout=='vertical':
        typography+='\nNo personal signature; leave the lower-right signature zone empty.'
    prompt=f'''{opening}
Use style-reference.png for the matte grain, soft glowing light and shadow treatment.
{reference_rule}
Replace all reference subjects, copy and colors with the selected content and palette.
Portrait canvas: {canvas[0]} x {canvas[1]} pixels. Keep a restrained composition.

BACKGROUND COLOR: {c['name']}, {c['prompt']}; digital art target {c['poster_hex']}.
Use subtle same-hue tonal variation and fine photographic grain, not a decorative pattern.
Preserve the selected base hue and overall lightness; do not darken or substitute this palette.
{text_zones}
LIGHT OUTLINE: {w['name']}; {w['prompt']}.
Place this SINGLE warm cream ({c['light_hex']}) light patch in x=20-80%, y=30-73% of the canvas.
Keep a softly feathered but recognizable aperture outline; no physical frame, wall or dense lattice.
INSIDE THE LIGHT: {scene}.
Render the objects only as soft diffused shadow: semi-transparent, low-contrast,
blurred and feathered cast shadows, as light projected through objects onto fine paper.
Let the warm light remain visible through and around the shadows; one focal subject with sparse supporting elements.
No solid black silhouettes, paper cutouts, sharp vector outlines, realistic product photographs,
3D objects, collage, unselected figures, {avoid}
No scene object or halo may enter the reserved text zones.
{typography}
'''
    return dict(status='planned',selection=ids,labels={a:selected[a].get('name',selected[a].get('text')) for a in selected},
                layout=layout,render_mode='full-image' if layout=='vertical' else 'background-plus-typesetting',
                canvas=canvas,poem_source=p['source_url'],poem_note=p['note'],
                color_reference_hex=c['hex'],color_poster_hex=c['poster_hex'],color_derivation=c['derivation'],
                references=references,signature_name=signature_name,signature_text=signature_text,
                prompt=prompt,compose=dict(background='background.png',output='poster.png',canvas=canvas,layout=layout,
                                           title='中秋佳節',title_font=title_font,subtitle='MID-AUTUMN FESTIVAL',greeting=p['lines'],attribution=p['attribution'],signature=signature_text))


def select_ids(catalog, filters, count=1, seed=None):
    filters=dict(filters)
    zid=resolve_zodiac(catalog,filters.get('zodiac'))
    if zid and filters.get('motif'):
        raise ValueError('With --zodiac, use --accent for supporting imagery; --motif selects the original non-zodiac mode.')
    if not zid and filters.get('accent'):
        raise ValueError('--accent requires --zodiac.')
    axes=[('poem','poems'),('color','colors'),('window','windows')]
    if zid:
        filters['zodiac']=zid
        axes += [('zodiac','zodiacs'),('accent','accents')]
    else:
        axes.append(('motif','motifs'))
    choices=[]
    for axis,group in axes:
        allowed=[item['id'] for item in catalog[group]]
        value=filters.get(axis)
        if value is not None and value not in allowed:
            raise ValueError(f'Unknown {axis}: {value}. Allowed IDs: {", ".join(allowed)}')
        choices.append([value] if value else allowed)
    pool=list(itertools.product(*choices))
    if not 1<=count<=len(pool):
        raise ValueError(f'count must be 1..{len(pool)} for these filters.')
    return [dict(zip([a for a,_ in axes],values)) for values in random.Random(seed).sample(pool,count)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list',action='store_true',help='List IDs without generating or writing files.')
    for key in ('poem','color','window','motif','zodiac','accent'):
        parser.add_argument('--'+key)
    parser.add_argument('--count',type=int,default=1,help='Number of distinct PLANS, not images.')
    parser.add_argument('--seed',type=int,help='Reproducible random selection of unspecified axes only.')
    parser.add_argument('--title-font',choices=('qiji','kaiti'),default='qiji',help='Title font: bundled Qiji (default) or locally installed KaiTi.')
    parser.add_argument('--layout',choices=('horizontal','vertical'),default='vertical',help='Complete-image vertical layout (default) or optional horizontal local typesetting.')
    signing=parser.add_mutually_exclusive_group()
    signing.add_argument('--signature',help='Chosen display name only; appends 遙祝. Preserve the confirmed name spelling.')
    signing.add_argument('--no-signature',action='store_true',help='User explicitly chose no personal signature.')
    parser.add_argument('--out-dir',type=Path)
    parser.add_argument('--canvas',nargs=2,type=int,metavar=('WIDTH','HEIGHT'))
    args=parser.parse_args()
    catalog=load_catalog()
    if args.list:
        print((ROOT/'references/catalog.md').read_text(encoding='utf-8'))
        return
    if not args.out_dir:
        parser.error('--out-dir is required unless --list is used.')
    if args.signature is None and not args.no_signature:
        parser.error('Ask whether the user wants a signature first, then pass --signature NAME or --no-signature.')
    if args.signature is not None and (not args.signature.strip() or any(ord(ch)<32 for ch in args.signature)):
        parser.error('--signature requires a nonempty single-line display name.')
    out=args.out_dir.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Generated plans must be outside the Skill package.')
    if args.canvas and (any(n<600 or n>8000 for n in args.canvas) or not .70<=args.canvas[0]/args.canvas[1]<=.80):
        parser.error('Canvas must be 600..8000 pixels per side, in a portrait ratio near 3:4.')
    try:
        run_seed=args.seed if args.seed is not None else random.SystemRandom().getrandbits(64)
        ids_list=select_ids(catalog,{a:getattr(args,a) for a in ('poem','color','window','motif','zodiac','accent')},args.count,run_seed)
    except ValueError as exc:
        parser.error(str(exc))
    jobs=[]
    for index,ids in enumerate(ids_list,1):
        folder=out if args.count==1 else out/(f'{index:03d}-'+'-'.join(ids.values()))
        plan=make_plan(catalog,ids,args.canvas,args.title_font,args.layout,args.signature)
        plan['signature_choice']='provided' if args.signature is not None else 'declined'
        plan['seed']=run_seed
        jobs.append((folder,plan))
    for folder,_ in jobs:
        if any((folder/name).exists() for name in ('plan.json','prompt.txt','compose.json','text.json')):
            parser.error(f'Plan files already exist in {folder}; select a new output directory.')
    for folder,plan in jobs:
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'plan.json').write_text(json.dumps({k:v for k,v in plan.items() if k not in ('prompt','compose')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'prompt.txt').write_text(plan['prompt'],encoding='utf-8')
        config_name='text.json' if plan['layout']=='vertical' else 'compose.json'
        (folder/config_name).write_text(json.dumps(plan['compose'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(str(folder))


if __name__=='__main__':
    main()
