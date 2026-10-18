from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent.parent
SCRIPT=ROOT/'scripts/audit_image_crops.py'
def run(items):
 with tempfile.TemporaryDirectory() as d:
  path=Path(d)/'manifest.json';path.write_text(json.dumps(items),encoding='utf8')
  return subprocess.run([sys.executable,str(SCRIPT),str(path)],capture_output=True,text=True)
def test_normal_contain():
 assert run([{'asset':'building.jpg','crop_fraction':0,'resize_method':'contain/no-crop'}]).returncode==0
def test_missing_crop_data_rejected():
 assert run([{'asset':'building.jpg','resize_method':'contain/no-crop'}]).returncode!=0
def test_unapproved_crop_rejected():
 assert run([{'asset':'building.jpg','crop_fraction':0.51,'resize_method':'approved-ROI'}]).returncode!=0
def test_crop_requires_roi_approval():
 assert run([{'asset':'building.jpg','crop_fraction':0.02,'resize_method':'approved-ROI','crop_authorized':True,'roi_evidence':'detail window A','approved_by':'architect'}]).returncode==0
