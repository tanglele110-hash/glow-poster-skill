#!/usr/bin/env python3
"""Verify plans, real typography renders and failure boundaries; not image-model QA."""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from plan import load_catalog, make_plan, select_ids, resolve_zodiac, ROOT

spec=importlib.util.spec_from_file_location('glow_compose',ROOT/'assets/compose.py')
compose_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose_module)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify(out):
    out=out.resolve()
    require(not out.is_relative_to(ROOT),'Verification output must be outside the package.')
    out.mkdir(parents=True,exist_ok=True)
    require(not (out/'verification.json').exists(),'Use a new verification directory.')
    catalog=load_catalog()
    fixture_ids=dict(poem='p07',color='c01',window='w02',motif='m01')
    require('default_ids' not in catalog,'Fixed preset remains in the catalog.')
    for key,count in [('poems',20),('colors',6),('windows',5),('motifs',8)]:
        values=catalog[key]
        require(len(values)==count and len({x['id'] for x in values})==count,f'Invalid {key} catalog.')
    for poem in catalog['poems']:
        require(''.join(poem['lines'])==poem['text'],f'Changed wording: {poem["id"]}')
        require(poem['source_url'].startswith('https://'),'Missing source URL.')
    classic_count=len(catalog['poems'])*len(catalog['colors'])*len(catalog['windows'])*len(catalog['motifs'])
    zodiac_count=len(catalog['poems'])*len(catalog['colors'])*len(catalog['windows'])*len(catalog['accents'])
    ids=select_ids(catalog,{},classic_count,20260925)
    require(len({tuple(v.values()) for v in ids})==classic_count,'Duplicate plan combinations.')
    for selection in ids:
        plan=make_plan(catalog,selection)
        for axis in ('color','window','motif'):
            require(plan['labels'][axis] in plan['prompt'],f'Ignored {axis} selection.')
        p=next(x for x in catalog['poems'] if x['id']==selection['poem'])
        require(plan['compose']['greeting']==p['lines'] and plan['compose']['attribution']==p['attribution'],'Lost poem attribution.')
    sample=select_ids(catalog,{'poem':'p01'},20,91)
    require(all(p['poem']=='p01' for p in sample),'Random selection overwrote an explicit axis.')
    require(sample==select_ids(catalog,{'poem':'p01'},20,91),'Seed is not reproducible.')
    require(len(catalog['zodiacs'])==12 and len(catalog['accents'])==8,'Incomplete zodiac library.')
    zodiac_plans=0
    for z in catalog['zodiacs']:
        for alias in [z['id'],z['name'],*z['aliases'],'生肖是'+z['name'],'我属'+z['name']]:
            require(resolve_zodiac(catalog,alias)==z['id'],'Zodiac alias not recognized.')
        choices=select_ids(catalog,{'zodiac':z['name']},zodiac_count,42)
        require(len({tuple(v.values()) for v in choices})==zodiac_count,'Duplicate zodiac combinations.')
        for choice in choices:
            plan=make_plan(catalog,choice)
            require(choice['zodiac']==z['id'] and 'motif' not in choice,'Zodiac was changed or mixed with legacy mode.')
            require(z['prompt'] in plan['prompt'],'Missing animal anatomy constraints.')
            a=next(a for a in catalog['accents'] if a['id']==choice['accent'])
            require(a['prompt'] in plan['prompt'],'Accompaniment lost.')
            require(plan['compose']['title']=='中秋佳節','Festival changed.')
            zodiac_plans+=1
    fixed={'zodiac':'龍','poem':'p01','color':'c01','window':'w02','accent':'a01'}
    expected=dict(fixed,zodiac='z05')
    require(select_ids(catalog,fixed,1,42)==[expected],'Explicit zodiac combination changed.')
    draws=[select_ids(catalog,{'zodiac':'dragon'},seed=n)[0] for n in range(64)]
    require(all(d['zodiac']=='z05' for d in draws),'Randomization changed the requested zodiac.')
    for axis in ('poem','color','window','accent'):
        require(len({d[axis] for d in draws})>1,f'Unspecified {axis} is locked.')
    unseeded=[select_ids(catalog,{'zodiac':'兔'})[0] for _ in range(16)]
    require(len({tuple(d.values()) for d in unseeded})>1,'Unseeded requests keep returning a fixed preset.')
    explicit={'zodiac':'兔','color':'c04','window':'w05'}
    partial=select_ids(catalog,explicit,20,17)
    require(all(d['zodiac']=='z04' and d['color']=='c04' and d['window']=='w05' for d in partial),'Explicit axes were changed.')
    vertical_checks=0
    for poem in catalog['poems']:
        choice=dict(expected,poem=poem['id'])
        vertical=make_plan(catalog,choice,layout='vertical')
        require(vertical['render_mode']=='full-image','Wrong vertical workflow.')
        require(vertical['compose']['greeting']==poem['lines'],'Vertical copy changed.')
        require(poem['attribution'] in vertical['prompt'],'Vertical attribution lost.')
        require(all(line in vertical['prompt'] for line in poem['lines']),'Vertical poem lost.')
        require(len(vertical['references'])==2,'Vertical layout reference missing.')
        require('text-free' not in vertical['prompt'],'Contradictory vertical prompt.')
        vertical_checks+=1
    for c in catalog['colors']:
        require(c['rgb']==list(bytes.fromhex(c['hex'][1:])),'HEX/RGB mismatch.')
        require(c['hex']==c['poster_hex'],'Unexpected color adaptation.')
        require('source_file' not in c,'Palette still depends on source images.')

    signed=make_plan(catalog,expected,signature='樂樂')
    unsigned=make_plan(catalog,expected)
    require(signed['selection']==unsigned['selection'],'Signature changed content selection.')
    require(signed['compose']['signature']=='樂樂遙祝' and '樂樂遙祝' in signed['prompt'],'Signature missing from full-image copy.')
    require(unsigned['compose']['signature']=='' and '樂樂' not in unsigned['prompt'],'Example signature leaked into unsigned plan.')
    for name,flags in [('signed',['--signature','樂樂']),('unsigned',['--no-signature'])]:
        folder=out/('cli-'+name)
        subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'--zodiac','鼠','--seed','42',*flags,'--out-dir',str(folder)],check=True,capture_output=True,text=True,encoding='utf-8')
        saved=json.loads((folder/'plan.json').read_text(encoding='utf-8'))
        require(saved['signature_choice']==('provided' if name=='signed' else 'declined'),'Signature choice not recorded.')
    missing=out/'cli-missing-choice'
    result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'--zodiac','鼠','--out-dir',str(missing)],capture_output=True,text=True,encoding='utf-8')
    require(result.returncode!=0 and not missing.exists() and 'Ask whether' in result.stderr,'CLI bypasses signature intake.')

    def config(name,**updates):
        plan=make_plan(catalog,fixture_ids,layout='horizontal')
        cfg=plan['compose']|{'background':str(ROOT/'assets/style-reference.png'),'output':str(out/f'{name}.png')}
        cfg.update(updates)
        path=out/f'{name}.json'
        path.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return path

    rendered=[]
    for p in catalog['poems']:
        report=compose_module.compose(config(p['id'],greeting=p['lines'],attribution=p['attribution']))
        with Image.open(report['output']) as img:
            require(list(img.size)==catalog['canvas'] and img.format=='PNG','Wrong PNG dimensions/format.')
        printed=[x['text'] for x in report['text'] if x['role']=='greeting']
        require(Path(report['font_files']['title'][0]).name=='qiji.ttf','Default title font is not Qiji.')
        require(printed==p['lines'],'Rendering altered the poem.')
        require(all(x['bbox'][1]>report['scene_bbox_pixels'][3] for x in report['text'] if x['role'] in ('greeting','attribution')),'Footer overlaps the light.')
        rendered.append({'id':p['id'],'output':report['output'],'fallbacks':report['font_fallbacks']})
    compose_module.compose(config('strict-3x4',canvas=[1440,1920]))
    compose_module.compose(config('scaled',canvas=[900,1200]))
    signature_report=compose_module.compose(config('signed-horizontal',signature='樂樂遙祝'))
    require(''.join(r['text'] for r in signature_report['text'] if r['role']=='signature')=='樂樂遙祝','Rendered signature changed.')
    kai_path=compose_module.local_kaiti_font()
    if kai_path:
        kai=compose_module.compose(config('title-kaiti',title_font='kaiti'))
        require(Path(kai['font_files']['title'][0]).name=='simkai.ttf','KaiTi option was ignored.')
    qiji_map=compose_module.font_coverage(compose_module.TITLE_FONT)
    require(all(ord(c) in qiji_map for c in '中秋佳節'),'Qiji title has missing glyphs.')

    # Synthetic fixtures test detection math only; they are not poster artwork.
    color_checks=[]
    for c in catalog['colors']:
        bg=Image.new('RGB',(900,1200),c['poster_hex'])
        ImageDraw.Draw(bg).ellipse((210,390,690,850),fill=c['light_hex'])
        box=compose_module.scene_bounds(bg)
        require(abs(box[3]-850)<30,f'Incorrect glow edge on {c["id"]}')
        color_checks.append(c['id'])

    guards=[]
    def rejects(name,action):
        try:
            action()
        except (compose_module.LayoutError,ValueError):
            guards.append(name)
        else:
            raise AssertionError(f'Expected rejection: {name}')
    rejects('unknown selection',lambda: select_ids(catalog,{'poem':'p99'}))
    rejects('vertical config in horizontal composer',lambda: compose_module.compose(config('bad-vertical',layout='vertical')))
    rejects('unknown layout',lambda: make_plan(catalog,fixture_ids,layout='unknown'))
    rejects('unknown title font',lambda: compose_module.compose(config('bad-title-font',title_font='unknown')))
    rejects('unknown zodiac',lambda: select_ids(catalog,{'zodiac':'凤凰'}))
    rejects('mixed scene modes',lambda: select_ids(catalog,{'zodiac':'龙','motif':'m01'}))
    rejects('accent without zodiac',lambda: select_ids(catalog,{'accent':'a01'}))
    rejects('unknown accent',lambda: select_ids(catalog,{'zodiac':'龙','accent':'a99'}))
    rejects('batch exceeds unique combinations',lambda: select_ids(catalog,{'poem':'p01'},classic_count//len(catalog['poems'])+1,1))
    rejects('overwrite',lambda: compose_module.compose(out/'p07.json'))
    rejects('long text',lambda: compose_module.compose(config('bad-long',greeting=['中秋'*80])))
    rejects('empty signature name',lambda: make_plan(catalog,expected,signature=' '))
    rejects('multiline signature name',lambda: make_plan(catalog,expected,signature='樂\n樂'))
    rejects('signature overflow',lambda: compose_module.compose(config('bad-signature-long',signature='名字'*30+'遙祝')))
    rejects('signature missing glyph',lambda: compose_module.compose(config('bad-signature-glyph',signature='\U0010ffff遙祝')))
    rejects('missing glyph',lambda: compose_module.compose(config('bad-glyph',greeting=['中秋\U0010ffff'])))
    rejects('fallback disabled',lambda: compose_module.compose(config('bad-fallback',greeting=['此夜若無月，','一年虛過秋。'],fallback_fonts=[])))
    rejects('glow in footer',lambda: compose_module.compose(config('bad-glow',scene_bbox=[.2,.3,.8,.82])))
    rejects('no measured glow',lambda: compose_module.scene_bounds(Image.new('RGB',(900,1200),'#529CA6')))
    wrong=out/'wrong-ratio.png'; Image.new('RGB',(1000,1000),'#529CA6').save(wrong)
    rejects('wrong aspect ratio',lambda: compose_module.compose(config('bad-ratio',background=str(wrong))))
    for name in ('bad-long','bad-glyph','bad-fallback','bad-glow','bad-ratio'):
        require(not (out/f'{name}.png').exists(),'Failed layout emitted a poster.')
    result=dict(status='passed',signature_checks=['CLI intake required','signed and unsigned CLI plans','selection unchanged','full-image signature copy','horizontal signature render','empty/multiline/overflow/missing-glyph rejection'],planned_combinations=classic_count,zodiac_planned_combinations=zodiac_plans,vertical_plan_checks=vertical_checks,poem_renders=rendered,additional_canvas_checks=2,
                color_detection_fixtures=color_checks,rejection_checks=guards,
                scope='Local catalog, font and layout checks. All poem renders use the original reference background. No new AI motif/shape/color image was generated.')
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return dict(status=result['status'],plans=classic_count,poem_renders=len(rendered),extra_canvas_checks=2,
                color_detection_checks=len(color_checks),rejection_checks=len(guards))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',required=True,type=Path)
    print(json.dumps(verify(parser.parse_args().out_dir),ensure_ascii=False))
