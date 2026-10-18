#!/usr/bin/env python3
"""Architecture editorial audit of source links and story graph. No aesthetic certification.
Usage: python scripts/audit_scheme.py --root /path/to/project --json report.json
"""
import argparse, csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

def read_csv(p):
    if not p.is_file():
        return None
    with p.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def parts(text):
    return [t.strip() for t in re.split(r'[;,|]', text or '') if t.strip()]

def audit(root, strict=False):
    root=Path(root)
    names={'assets':'asset_manifest.csv','evidence':'evidence_ledger.csv','operations':'design_operations.csv','pages':'storyboard_v2.5.csv'}
    data={k:read_csv(root/v) for k,v in names.items()}
    issues=[]
    def issue(level,code,where,detail): issues.append(dict(level=level,code=code,where=str(where),detail=detail))
    for k,v in data.items():
        if v is None: issue('ERROR','FILE_MISSING',names[k],'Required file not found')
    if any(v is None for v in data.values()): return dict(status='FAIL',pages=0,issues=issues)
    assets={a.get('asset_id','').strip():a for a in data['assets']}
    evid={a.get('evidence_id','').strip():a for a in data['evidence']}
    operations={a.get('operation_id','').strip():a for a in data['operations']}
    pages=data['pages']; reasons=defaultdict(list); photo_ids=defaultdict(list); signatures=[]
    for row in data['evidence']:
        eid=row.get('evidence_id','')
        if not row.get('source_pointer','').strip(): issue('ERROR','UNTRACEABLE_EVIDENCE',eid,'No file/page/drawing pointer')
        for aid in parts(row.get('asset_ids','')):
            if aid not in assets: issue('ERROR','MISSING_ASSET',eid,f'Asset {aid} not in manifest')
    for op in data['operations']:
        oid=op.get('operation_id','')
        if not op.get('operation_text','').strip(): issue('ERROR','EMPTY_OPERATION',oid,'Architecture operation missing')
        c=op.get('claim_class','')
        if c not in {'SOURCE_FACT','EDITORIAL_INFERENCE','DESIGN_PROPOSAL'}:
            issue('ERROR','INVALID_CLAIM_CLASS',oid,f'Unexpected claim class {c}')
        if c=='DESIGN_PROPOSAL' and op.get('mode','')=='PRESENT':
            issue('ERROR','MODE_CONFLICT',oid,'PRESENT cannot silently present a proposed geometry change')
        for e in parts(op.get('evidence_ids','')):
            if e not in evid: issue('ERROR','MISSING_EVIDENCE',oid,f'Unknown evidence {e}')
    for i,page in enumerate(pages):
        p=page.get('page','') or str(i+1)
        if not page.get('reader_question','').strip() or not page.get('new_information','').strip():
            issue('ERROR','NO_NEW_INFORMATION',p,'Every page must answer a question and add architectural information')
        oid=page.get('operation_id','').strip()
        if not oid or oid not in operations: issue('ERROR','ORPHAN_PAGE_OPERATION',p,f'Unknown operation {oid}')
        pe=page.get('main_evidence_id','').strip()
        if not pe or pe not in evid: issue('ERROR','NO_PRIMARY_EVIDENCE',p,f'Unknown main evidence {pe}')
        vis=page.get('visual_behavior','')
        if vis not in {'SITUATE','OPERATE','REVEAL','ENTER','VERIFY','DECIDE'}:
            issue('WARN','UNKNOWN_VISUAL_BEHAVIOR',p,vis)
        sig=page.get('visual_signature','').strip().lower()
        signatures.append(sig)
        if sig in {'hero+sidecar','picture+sidebar','photo+sidebar','left-photo-right-text','right-photo-left-text'}:
            reasons['sidebar'].append(p)
        if i>0 and not page.get('previous_to_next','').strip():
            issue('ERROR','NO_CROSS_PAGE_BRIDGE',p,'Page must connect explicitly to prior architectural subject')
        for aid in parts(page.get('asset_ids','')):
            if aid not in assets: issue('ERROR','PAGE_UNKNOWN_ASSET',p,aid)
            if assets.get(aid,{}).get('media_kind','').lower()=='photo':photo_ids[aid].append(p)
        if len(page.get('proof_limit','').strip())<5:
            issue('WARN','NO_PROOF_LIMIT',p,'Evidence limitations not described')
    for aid, locations in photo_ids.items():
        if len(locations)>1:
            reason=[p.get('reuse_reason','') for p in pages if aid in parts(p.get('asset_ids',''))]
            if not all(x.strip() and len(x.strip())>=12 for x in reason):
                issue('ERROR','UNEXPLAINED_PHOTO_REUSE',aid,f'Used in {locations} without per-page semantic reason')
            else: issue('INFO','JUSTIFIED_IMAGE_REUSE',aid,f'Use verified manually: {locations}')
    if len(pages)>=5 and len(reasons['sidebar'])>=3 and len(reasons['sidebar'])/len(pages)>=.4:
        issue('ERROR','TEMPLATE_GRAMMAR_DOMINANCE','deck',f'Hero-plus-sidebar declared in {len(reasons["sidebar"])}/{len(pages)} pages')
    for i in range(max(0,len(signatures)-2)):
        if signatures[i] and signatures[i]==signatures[i+1]==signatures[i+2]:
            issue('ERROR','THREE_IDENTICAL_LAYOUTS',f'{i+1}-{i+3}','Three consecutive pages use identical visual_signature')
    ecount=sum(x['level']=='ERROR' for x in issues)
    return {'status':'FAIL' if ecount else ('REVIEW' if issues else 'STRUCTURALLY_READY'), 'pages':len(pages), 'error_count':ecount, 'warning_count':sum(x['level']=='WARN' for x in issues),'issues':issues,
       'note':'No script can certify architectural geometry, visual elegance, image rights or factual truth.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--json');ap.add_argument('--strict',action='store_true')
    a=ap.parse_args();result=audit(a.root,a.strict)
    txt=json.dumps(result,ensure_ascii=False,indent=2)
    if a.json:Path(a.json).write_text(txt,encoding='utf-8')
    print(txt)
    raise SystemExit(1 if result['error_count'] else 0)
if __name__=='__main__':main()
