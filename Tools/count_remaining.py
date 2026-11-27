"""Count what is still missing, in documents and in demonstrated capability.

Two different things are measured, because they fail in different ways. A document gap can be closed
by fetching a page; a capability gap needs something actually done and verified in the editor, and
having the document does not close it.

    python Tools/count_remaining.py
"""

import glob
import os

MANUAL = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"
ARTICLE_LINES = 40
ARTICLE_CHARS = 4000

# The areas the learning plan names, plus the project-specific systems.
AREAS = {
    "渲染/几何": ["nanite", "nanite-technical", "virtual-shadow-maps",
                  "temporal-super-resolution", "static-mesh-lod", "fbx-static-mesh",
                  "import-static-meshes"],
    "渲染/光照": ["lumen-technical", "lumen-performance", "directional-lights",
                  "sky-atmosphere", "reflections-captures", "post-process-materials",
                  "lighting-environment", "light-types", "reflections"],
    "材质": ["material-editor-guide", "material-expressions", "texture-asset-editor",
             "materials", "instanced-materials", "textures"],
    "世界": ["world-partition", "landscape-technical", "foliage", "water-bodies",
             "collision", "navigation-basic", "navigation-mesh", "hlod", "landscape",
             "water", "navigation"],
    "动画": ["animation-editors", "state-machines", "control-rig-editor",
             "sequencer-editor", "animation-blueprints", "skeletal-animation",
             "control-rig", "sequencer"],
    "模拟": ["physics", "chaos-fracture", "niagara-overview",
             "chaos-destruction", "niagara", "niagara-modules"],
    "玩法": ["game-mode", "enhanced-input", "blueprints", "umg-quick-start",
             "gameplay-framework"],
    "音频/网络/性能": ["sound-cue-reference", "networking", "performance", "insights",
                       "audio", "sound-cue-editor", "attenuation"],
    "编辑器/脚本": ["python-scripting", "unreal-mcp", "python-with-ai-agents",
                    "level-editor", "asset-management", "command-line-arguments"],
    "项目专用": ["data-tables", "savegame", "geometry-scripting",
                 "user-interfaces-huds"],
}

# Things a shipping-capable developer has done at least once. None of these are documentation gaps;
# each needs a run in the editor, which is why they are counted separately.
CAPABILITIES = [
    ("跑通一次 Shipping 打包", None),
    ("量出一次真实帧时间（Insights 或 stat 记录）", None),
    ("建一个 UMG Widget Blueprint 并显示在屏幕上", None),
    ("建一个 Niagara 系统并放到场景里", None),
    ("给物体加物理约束并让它真的动起来", None),
    ("从零新建一个 Material 并连出节点", None),
    ("新建一块 Landscape 并刷高度", None),
    ("建一个动画蓝图状态机并让角色在状态间切换", None),
    ("用 DataTable 驱动一次真实的数值查表", None),
    ("写一个 C++ 类的完整生命周期并在编辑器里验证", None),
]


def measure(path):
    text = open(path, encoding="utf-8").read()
    lines = len([ln for ln in text.split("\n") if ln.strip()])
    return lines >= ARTICLE_LINES and len(text) >= ARTICLE_CHARS


def main():
    files = {os.path.basename(f)[:-3]: f for f in glob.glob(os.path.join(MANUAL, "*.md"))
             if not f.endswith("README.md")}
    articles = {n for n, p in files.items() if measure(p)}

    total_kb = sum(os.path.getsize(p) for p in files.values()) / 1024.0

    print("=" * 72)
    print("文档")
    print("=" * 72)
    print("手册 %d 篇 / %.0f KB  —  真文章 %d 篇，索引页 %d 篇"
          % (len(files), total_kb, len(articles), len(files) - len(articles)))
    print("")
    print("%-16s %-8s %s" % ("领域", "真文章", "状态"))
    print("-" * 72)
    doc_gap = 0
    for area, names in AREAS.items():
        have = [n for n in names if n in articles]
        idx = [n for n in names if n in files and n not in articles]
        if have:
            print("%-16s %-8d ok（索引页 %d 篇）" % (area, len(have), len(idx)))
        else:
            print("%-16s %-8d MISSING" % (area, 0))
            doc_gap += 1
    print("")
    print("文档层面缺口: %d 个领域无真文章" % doc_gap)
    print("")

    print("=" * 72)
    print("能力（项目能不能自己做完，靠这个，不靠文档）")
    print("=" * 72)
    print("%-50s %s" % ("要能做的", "状态"))
    print("-" * 72)
    for text, done in CAPABILITIES:
        mark = "已验证" if done else "未验证"
        print("%-50s %s" % (text, mark))
    print("")
    undone = sum(1 for _t, d in CAPABILITIES if not d)
    print("能力层面缺口: %d / %d 项未验证" % (undone, len(CAPABILITIES)))

    print("")
    print("=" * 72)
    print("结论")
    print("=" * 72)
    if doc_gap == 0:
        print("文档: 完备（九个领域 + 项目专用都有真文章）")
    else:
        print("文档: 还缺 %d 个领域" % doc_gap)
    print("能力: 缺 %d 项实操验证 —— 这些补不了文档，只能真做一遍" % undone)


if __name__ == "__main__":
    main()
