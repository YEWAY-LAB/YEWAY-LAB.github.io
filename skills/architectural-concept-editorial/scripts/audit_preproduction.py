#!/usr/bin/env python3
"""Check an architectural proposal content+layout plan before production.
Not a proof of architectural merit or an aesthetic grading tool.
Usage: python scripts/audit_preproduction.py --root path [--release] [--json output.json]
"""
import argparse,csv,json,re,sys
from pathlib import Path
try:import yaml
except Exception: yaml=None
REQUIRED={
 'content_plan.csv':['page_id','architectural_question','factual_thesis','claim_class','evidence_ids','exact_page_copy','argument_dependency','uncertainty','decision_for_reader'],
 'layout_plan.csv':['page_id','visual_role','primary_asset_id','layout_signature','image_geometry','protected_subject','text_zone','title_size_pt','body_size_pt','crop_policy','why_this_composition','asset_readiness'],
 'narrative_graph.csv':['from_page','to_page','architecture_object','logic_edge','essential_reason']}
STATES={'REVIEW_PENDING','REVISION_REQUIRED','APPROVED'}
CLASSES={'SOURCE_FACT','EDITORIAL_INFERENCE','DESIGN_PROPOSAL'}
EMPTY={'','-','—','none','tbd','待填','待定'}
WEAK=[r'诗意[的地]?(?:对话|融合|生长)',r'赋能未来',r'建筑的灵魂',r'让空间生长',r'完美诠释',r'与自然[的]?[深情]*对话',r'以匠心']

def audit(root,release=False):
 p=Path(root); issues=[]
 def flag(level,code,where,detail):issues.append({'level':level,'code':code,'where':str(where),'detail':detail})
 tables={}
 for fname,columns in REQUIRED.items():
  f=p/fname
  if not f.exists(): flag('ERROR','PLAN_FILE_MISSING',fname,'Required pre-production file missing');continue
  with f.open(encoding='utf-8-sig',newline='') as fh:
   reader=csv.DictReader(fh); rows=list(reader);have=reader.fieldnames or []
  tables[fname]=rows
  if not rows:flag('ERROR','EMPTY_PLAN',fname,'No pages or narrative edges')
  for k in columns:
   if k not in have:flag('ERROR','COLUMN_MISSING',fname,k)
 if len(tables)!=len(REQUIRED):return {'status':'BLOCKED','issue_count':len(issues),'issues':issues}
 cont=tables['content_plan.csv']; layouts=tables['layout_plan.csv']; edges=tables['narrative_graph.csv']
 # Source ledger is required for a claim-to-original-document trace.
 evf=p/'evidence_ledger.csv'; asf=p/'asset_manifest.csv'; valid_evidence=set(); valid_assets=set()
 if not evf.exists() or not asf.exists():flag('ERROR','SOURCE_REGISTER_MISSING','evidence/asset','Source and asset ledgers are required')
 else:
  try:
   with evf.open(encoding='utf-8-sig',newline='') as eh:
    evrows=list(csv.DictReader(eh));valid_evidence={r.get('evidence_id','').strip() for r in evrows}
   with asf.open(encoding='utf-8-sig',newline='') as ah:
    assetrows=list(csv.DictReader(ah));valid_assets={r.get('asset_id','').strip() for r in assetrows}
   for r in evrows:
    if not r.get('source_pointer','').strip():flag('ERROR','EVIDENCE_SOURCE_MISSING',r.get('evidence_id'),'Original drawing/photo/data source missing')
  except (OSError,ValueError):flag('ERROR','INVALID_REGISTER','source registers','Could not parse evidence or assets')
 cp=[a.get('page_id','').strip() for a in cont]
 lp=[a.get('page_id','').strip() for a in layouts]
 if len(set(cp))!=len(cp):flag('ERROR','DUPLICATE_PAGES','content','Page ID repeats')
 if cp!=lp:flag('ERROR','PAGE_PLAN_MISMATCH','layout','Content and layout page IDs/order must agree')
 for i,r in enumerate(cont):
  pid=r.get('page_id') or i+1
  for field in ['architectural_question','factual_thesis','claim_class','evidence_ids','exact_page_copy','argument_dependency','decision_for_reader']:
   if r.get(field,'').strip().lower() in EMPTY:flag('ERROR','MISSING_'+field.upper(),pid,field)
  if r.get('claim_class') not in CLASSES:flag('ERROR','UNKNOWN_CLAIM_CLASS',pid,r.get('claim_class'))
  for eid in re.split(r'[;,|]',r.get('evidence_ids','')):
   if eid.strip() and eid.strip() not in valid_evidence:flag('ERROR','UNKNOWN_EVIDENCE_ID',pid,eid.strip())
  if i>0 and len(r.get('argument_dependency','').strip())<8:flag('ERROR','WEAK_PAGE_DEPENDENCY',pid,'No concrete transfer from prior page')
  for pat in WEAK:
   if re.search(pat,r.get('factual_thesis','')+' '+r.get('exact_page_copy','')):
    flag('WARN','RHETORICAL_CLICHE',pid,pat)
  if len(r.get('exact_page_copy',''))>210:
   flag('WARN','TEXT_OVERLOAD',pid,'Main page copy >210 characters; split or reduce')
 for i,r in enumerate(layouts):
  pid=r.get('page_id') or i+1
  for field in ['visual_role','primary_asset_id','layout_signature','image_geometry','protected_subject','text_zone','crop_policy','why_this_composition','asset_readiness']:
   if r.get(field,'').strip().lower() in EMPTY:flag('ERROR','MISSING_LAYOUT_FIELD',pid,field)
  for aid in re.split(r'[;,|]',r.get('primary_asset_id','')+';'+r.get('secondary_asset_ids','')):
   if aid.strip() and aid.strip() not in valid_assets:flag('ERROR','UNKNOWN_IMAGE_ASSET',pid,aid.strip())
  for field in ['title_size_pt','body_size_pt']:
   try:
    x=float(r.get(field))
    if not 13<=x<=66:flag('WARN','FONT_READABILITY',pid,f'{field}:{x}')
   except (TypeError,ValueError):flag('ERROR','INVALID_FONT_SIZE',pid,field)
  if r.get('asset_readiness')!='READY':
   flag('WARN','ASSET_NOT_READY',pid,r.get('asset_readiness'))
 for i in range(max(0,len(layouts)-2)):
  keys=[r.get('layout_signature','').lower().strip() for r in layouts[i:i+3]]
  if len(set(keys))==1:flag('WARN','REPEATED_LAYOUT_RUN',f'{i+1}-{i+3}',keys[0])
 for j,r in enumerate(edges):
  f,t=r.get('from_page',''),r.get('to_page','')
  if f not in cp or t not in cp:flag('ERROR','INVALID_NARRATIVE_EDGE',j+1,f'{f}->{t}')
  if len(r.get('essential_reason','').strip())<8:flag('ERROR','NO_CAUSAL_EDGE',j+1,f'{f}->{t}')
 for i in range(len(cp)-1):
  if not any(r.get('from_page')==cp[i] and r.get('to_page')==cp[i+1] for r in edges):
   flag('ERROR','ADJACENT_BRIDGE_MISSING',cp[i]+'->'+cp[i+1],'No adjacent continuity evidence')
 f=p/'approval_record.yaml'
 if not f.exists():flag('ERROR','APPROVAL_FILE_MISSING','approval_record.yaml','No approval record');ap={}
 else:
  try:ap=yaml.safe_load(f.read_text(encoding='utf-8')) or {}
  except Exception:flag('ERROR','APPROVAL_PARSE_ERROR','approval_record.yaml','Malformed YAML');ap={}
 for gate in ['g1_content_status','g2_layout_status']:
  if ap.get(gate) not in STATES:flag('ERROR','INVALID_APPROVAL_STATE',gate,str(ap.get(gate)))
 approved=(ap.get('g1_content_status')=='APPROVED' and ap.get('g2_layout_status')=='APPROVED' and bool(ap.get('content_approval_evidence')) and bool(ap.get('layout_approval_evidence')))
 if release and not approved:
  flag('ERROR','PRODUCTION_NOT_AUTHORIZED','G1/G2','User has not explicitly approved both content and visual plans')
 if ap.get('production_started') and not approved:flag('ERROR','PRODUCTION_PREMATURE','approval_record.yaml','production_started was set before approval')
 ec=sum(a['level']=='ERROR' for a in issues);wc=sum(a['level']=='WARN' for a in issues)
 return {'status':'BLOCKED' if ec else ('PLANNED_AWAITING_APPROVAL' if not approved else ('PLANNED_WITH_WARNINGS' if wc else 'RELEASED')),'page_count':len(cont),'error_count':ec,'warning_count':wc,'approved_for_production':approved and ec==0,'issues':issues,'note':'Machine checks structural pre-production data only, not architectural truth or editorial aesthetic quality.'}

def main():
 ar=argparse.ArgumentParser();ar.add_argument('--root',required=True);ar.add_argument('--json');ar.add_argument('--release',action='store_true');args=ar.parse_args()
 res=audit(args.root,args.release)
 if args.json:Path(args.json).write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(res,ensure_ascii=False,indent=2))
 return int(res.get('error_count',1)>0)
if __name__=='__main__':sys.exit(main())
