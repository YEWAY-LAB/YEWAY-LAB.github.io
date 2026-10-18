#!/usr/bin/env python3
"""Geometry-only PowerPoint layout signatures. Flags repetitive compositions; not a style score."""
import argparse, json, statistics
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

def inspect(path):
    p=Presentation(str(path)); W=p.slide_width;H=p.slide_height;AREA=W*H
    slides=[]; sidecar=[]
    for i,s in enumerate(p.slides,1):
        pics=[];txt=[]
        for sh in s.shapes:
            x,y,w,h=sh.left,sh.top,sh.width,sh.height
            if sh.shape_type==MSO_SHAPE_TYPE.PICTURE:
                pics.append((x,y,w,h))
            elif sh.has_text_frame and sh.text.strip():
                txt.append((x,y,w,h,sh.text.strip().replace('\n',' ')[:48]))
        biggest=max(pics,key=lambda a:a[2]*a[3],default=None)
        biggest_area=(biggest[2]*biggest[3]/AREA) if biggest else 0
        in_left=in_right=0;extent=None
        if biggest:
            img_middle=(biggest[0]+biggest[2]/2)/W
            for x,y,w,h,content in txt:
                t_mid=(x+w/2)/W
                if t_mid < biggest[0]/W-0.015:in_left+=1
                if t_mid > (biggest[0]+biggest[2])/W+0.015:in_right+=1
            if (0.30<=biggest_area<=.83 and max(in_left,in_right)>=2 and
              (biggest[2]/W)>=.52):
                extent='main-image-plus-sidecar'
                sidecar.append(i)
        notes=[]
        if biggest_area<.22 and pics:notes.append('No image over 22% slide area')
        if len(pics)>=5:notes.append('Five-plus image placements require a relevance review')
        slides.append({'page':i,'picture_count':len(pics),'text_count':len(txt),'main_image_fraction':round(biggest_area,3),
          'main_image_rect': [round(biggest[j]/(W if j%2==0 else H),3) for j in range(4)] if biggest else None,
          'text_fully_outside_image_left':in_left,'text_fully_outside_image_right':in_right,
          'signature_warning':extent,'warnings':notes})
    ratio=len(sidecar)/len(slides) if slides else 0
    warnings=[]
    if len(slides)>=5 and len(sidecar)>=3 and ratio>=.40:
        warnings.append({'code':'DOMINANT_SIDECAR_COMPOSITION','pages':sidecar,'ratio':round(ratio,3),'note':'Mirroring this motif does not create a new editorial grammar.'})
    return {'source_file':str(path),'page_count':len(slides),'sidecar_pages':sidecar,'warnings':warnings,
           'slides':slides,'disclaimer':'Image geometry is only a screening signal; visual and architectural review are mandatory.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pptx');ap.add_argument('--json');a=ap.parse_args()
    ret=inspect(a.pptx);out=json.dumps(ret,ensure_ascii=False,indent=2)
    if a.json:Path(a.json).write_text(out,encoding='utf-8')
    print(out)
if __name__=='__main__':main()
