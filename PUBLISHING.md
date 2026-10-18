# 建筑方案型 PPT Skill

**YEWAY-LAB · architectural-concept-editorial · v2.6.2**

面向概念方案、竞赛、方案优化、立面材质深化与建成作品表达。按项目事实、建筑问题、连续叙事和真实图像策划 PPT；使用纯黑/纯白版面、原生可编辑文字和保真图纸。

## 安装

将 `skills/architectural-concept-editorial` 整个文件夹复制到支持 Agent Skills 的工具的技能目录；Codex 常用目录为 `~/.codex/skills/`。重新加载工具后，调用 `$architectural-concept-editorial`。不同客户端的发现与安装入口以其当前文档为准。

示例：

> 使用 $architectural-concept-editorial，将我提供的总图、剖面和建筑图像整理成方案汇报。先完成内容策划和版面分镜，保留真实图纸与建筑几何，默认黑白排版和完整原图。

## 内容

- `SKILL.md`：任务分类、事实与推断区分、内容/版面策划、审查及交付。
- `references/`：建筑文案、证据链、跨页叙事、黑白视觉、反模板和图片保护规则。
- `templates/`：项目简报、素材/证据台账、故事线与逐页分镜空白表。
- `scripts/`：策划结构、叙事、版面重复、图片裁切和缩略墙检查工具。
- `tests/`：黑白规则与图片裁切检查回归测试。

## 依赖与检查

运行辅助脚本需 Python 3.10+；在 Skill 目录安装依赖：

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/audit_preproduction.py --root /path/to/project
python scripts/audit_image_crops.py /path/to/image-manifest.json
```

PPTX 编写、渲染、图像生成和资料连接由运行环境提供。本 Skill 提供工作流与质检辅助，不是独立的一键建筑设计或 PPT 生成器。结构检查通过仍需实际渲染与建筑专业审阅；图片检查读取声明数据，不验证原图真伪。

当前脚本的 `--release` 检查需要 G1/G2 明确的审查记录；自动继续策略应保留实际授权与审查证据，不能伪造批准。

## 分发范围

公开版以 v2.6.2 源包为基础，保留核心规则、脚本与模板，将私人案例阅读记录改为通用机制说明，不包含项目原图、内部审稿、私人 Notion 链接或测试缓存。

本次公开分发未另行授予开源许可证；第三方项目、影像、图纸与商标的权利归原权利人。
