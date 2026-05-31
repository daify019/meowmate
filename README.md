# Desktop Cat Pal / 桌面猫咪伙伴 / MeowMate

MeowMate 是一个轻量桌面猫咪伙伴原型，使用 Python + PySide6 实现透明、置顶、可拖动的桌面宠物窗口。当前版本包含完整产品文档、交互设计与模块化代码骨架。猫咪外观已从程序化绘制切换为图片帧动画资源，后续可继续替换为更高精度的手绘精灵图、Spine 或 Lottie 动画资源。

当前项目已统一到 `D:\codex\desk pet`。运行时配置保存在项目目录下的 `data/settings.json`，避免写入 C 盘用户目录。

## 快速开始

```powershell
cd "D:\codex\desk pet"
conda env create -f environment.yml
conda activate meowmate
python -m src.meowmate.main
```

如果环境已经存在：

```powershell
cd "D:\codex\desk pet"
conda env update -f environment.yml --prune
conda activate meowmate
python -m src.meowmate.main
```

## 项目结构

```text
docs/
  PRD.md                    产品需求文档
  INTERACTION_DESIGN.md     核心交互、状态、成长和 UI 设计
src/meowmate/
  main.py                   应用入口
  domain/                   猫咪品种、性格、动作和状态模型
  services/                 状态机、行为调度、本地存储
  ui/                       桌面宠物窗口、设置面板、新手引导
```

## 当前功能

- 首次启动猫咪选择：暹罗猫、美短猫、布偶猫、黑猫、狸花猫、玳瑁猫。
- 透明置顶桌面宠物窗口。
- 左键点击反馈，左键拖动移动，右键菜单。
- 图片帧动画外观：使用 OpenGameArt CC0 猫咪精灵图，并按品种动态调色。
- 自然动作衔接：静止、行走、睡觉、开心、不高兴、特殊动作之间使用缓动过渡和淡入混合。
- 设置面板：猫咪品种、置顶、缩放、移动速度、互动强度、静音。
- 本地保存用户选择与宠物成长数据。

## 扩展方式

新增猫咪品种主要修改 `src/meowmate/domain/cat_catalog.py`。新增动作状态主要修改 `CatAction`、状态机权重以及 `CatWidget._clip_for` 的动作资源映射。
