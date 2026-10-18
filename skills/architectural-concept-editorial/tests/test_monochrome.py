from pathlib import Path
from PIL import Image

def test_skill_has_monochrome_gate():
 s=(Path(__file__).resolve().parents[1]/"SKILL.md").read_text()
 assert "背景只用白或黑" in s
 assert "真实项目照片保留原本颜色" in s
 assert "正式生成前的黑白墙面审稿" in s
