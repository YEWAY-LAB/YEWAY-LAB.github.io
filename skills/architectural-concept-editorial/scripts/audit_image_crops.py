#!/usr/bin/env python3
"""Zero-crop image framing audit for architectural editorial storyboard manifests.

Input is JSON list with `crop_fraction` per image placement plus source dimensions.
Presence of explicit provenance/approval is mandatory for any crop > 0.
This DOES NOT establish geometric source authenticity, only declared crop integrity.
"""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--report');a=p.parse_args()
data=json.loads(Path(a.manifest).read_text(encoding='utf8'))
errors=[]
for i,x in enumerate(data):
 c=x.get('crop_fraction',None)
 if c is None:errors.append(f'{i}: missing crop_fraction');continue
 if float(c)<0 or float(c)>1: errors.append(f'{i}: invalid fraction={c}')
 if float(c)>0:
  if not (x.get('crop_authorized') is True and x.get('roi_evidence') and x.get('approved_by')):
   errors.append(f'{i}: unauthorized image crop {100*float(c):.1f}%: {x.get("asset","")}')
 if x.get('resize_method') not in ('contain/no-crop','no-crop','approved-ROI'):
  errors.append(f'{i}: bad rendering policy {x.get("resize_method")}')
out={'placements':len(data),'crop_placements':sum(float(x.get('crop_fraction') or 0)>0 for x in data),'errors':errors,'passed':not errors}
if a.report:Path(a.report).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
