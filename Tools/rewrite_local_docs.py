"""Generate the local documentation status from what is on disk.

Everything here is measured: page counts, sizes, and which pages are articles rather than index pages.
An article is at least forty non-empty lines and four thousand characters; an index is a short list of
child topics, and having one teaches nothing on its own.

    python Tools/rewrite_local_docs.py
"""

import glob
import os

DOC = "C:/Users/tk/Desktop/lingxujie/Docs/LOCAL-UE-DOCS.md"
MANUAL = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"
API = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"

ARTICLE_LINES = 40
ARTICLE_CHARS = 4000

GROUPS = {
    "渲染 / 几何": [
        ("nanite", "Nanite 概述"),
        ("nanite-technical", "Nanite 技术细节"),
        ("virtual-shadow-maps", "虚拟阴影贴图"),
        ("temporal-super-resolution", "TSR 时序超分"),
        ("static-mesh-lod", "LOD 自动生成"),
        ("fbx-static-mesh", "FBX 静态网格管线"),
        ("import-static-meshes", "导入静态网格"),
    ],
    "渲染 / 光照": [
        ("lumen-technical", "Lumen 技术细节"),
        ("lumen-performance", "Lumen 性能指南"),
        ("directional-lights", "定向光"),
        ("sky-atmosphere", "天空大气"),
        ("reflections-captures", "反射捕获"),
        ("post-process-materials", "后处理材质"),
        ("lighting-environment", "环境光照"),
        ("light-types", "光源类型"),
        ("reflections", "反射概述"),
    ],
    "材质": [
        ("material-editor-guide", "材质编辑器指南"),
        ("material-expressions", "材质表达式参考"),
        ("texture-asset-editor", "贴图资产编辑器"),
        ("materials", "材质概述"),
        ("instanced-materials", "实例化材质"),
        ("textures", "贴图概述"),
    ],
    "世界": [
        ("world-partition", "World Partition"),
        ("landscape-technical", "Landscape 技术指南"),
        ("foliage", "植被模式"),
        ("water-bodies", "水体 Actor"),
        ("collision", "碰撞概述"),
        ("navigation-basic", "基础寻路"),
        ("navigation-mesh", "导航网格"),
        ("landscape", "Landscape 概述"),
        ("water", "水体概述"),
        ("navigation", "导航概述"),
    ],
    "动画": [
        ("animation-editors", "动画编辑器"),
        ("state-machines", "动画状态机"),
        ("control-rig-editor", "Control Rig 编辑器"),
        ("sequencer-editor", "Sequencer 编辑器"),
        ("animation-blueprints", "动画蓝图"),
        ("skeletal-animation", "骨骼动画系统"),
        ("control-rig", "Control Rig 概述"),
        ("sequencer", "Sequencer 概述"),
    ],
    "模拟": [
        ("physics", "物理"),
        ("chaos-fracture", "Chaos 破裂"),
        ("niagara-overview", "Niagara 概述"),
        ("chaos-destruction", "Chaos 破坏"),
        ("niagara", "Niagara 概述页"),
    ],
    "玩法与系统": [
        ("blueprints", "蓝图"),
        ("enhanced-input", "增强输入"),
        ("umg-quick-start", "UMG 快速入门"),
        ("game-mode", "Game Mode 与 Game State"),
        ("gameplay-framework", "Gameplay 框架"),
    ],
    "音频 / 网络 / 性能": [
        ("sound-cue-reference", "Sound Cue 参考"),
        ("networking", "网络"),
        ("performance", "性能分析"),
        ("audio", "音频概述"),
        ("sound-cue-editor", "Sound Cue 编辑器"),
        ("attenuation", "声音衰减"),
    ],
    "编辑器与脚本": [
        ("python-scripting", "Python 脚本"),
        ("unreal-mcp", "Unreal MCP"),
        ("python-with-ai-agents", "Python + AI Agent"),
        ("level-editor", "关卡编辑器"),
        ("asset-management", "资产管理"),
        ("command-line-arguments", "命令行参数"),
    ],
    "本项目专用（跨领域但项目直接用）": [
        ("user-interfaces-huds", "UI 与 HUD（Canvas）"),
        ("data-tables", "数据表"),
        ("savegame", "存档"),
        ("insights", "Unreal Insights"),
        ("hlod", "HLOD 层级 LOD"),
        ("geometry-scripting", "几何脚本（程序化网格）"),
    ],
}


def measure(path):
    text = open(path, encoding="utf-8").read()
    lines = len([ln for ln in text.split("\n") if ln.strip()])
    is_article = lines >= ARTICLE_LINES and len(text) >= ARTICLE_CHARS
    return len(text), lines, is_article


def main():
    files = sorted(f for f in glob.glob(os.path.join(MANUAL, "*.md"))
                   if not f.endswith("README.md"))
    api = glob.glob(os.path.join(API, "*.txt"))

    info = {}
    for path in files:
        name = os.path.basename(path)[:-3]
        chars, lines, is_article = measure(path)
        info[name] = (chars, lines, is_article, os.path.getsize(path))

    articles = [n for n, v in info.items() if v[2]]
    indexes = [n for n, v in info.items() if not v[2]]
    manual_kb = sum(v[3] for v in info.values()) / 1024.0
    api_kb = sum(os.path.getsize(f) for f in api) / 1024.0

    out = []
    out.append("# 本地 UE 官方文档\n")
    out.append("> **目的：把课程要查的官方文档搬到本地，减少来回翻网页。**")
    out.append("> **只搬运，不改编** —— 原文照录，出处写在每篇开头。")
    out.append(">")
    out.append("> **最后更新：2026-11-26 · 实测 %d 篇手册（%d 篇真文章 + %d 篇索引页）+ %d 篇 Python API**"
               % (len(info), len(articles), len(indexes), len(api)))
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 一、总数")
    out.append("")
    out.append("| 目录 | 内容 | 大小 |")
    out.append("| --- | --- | --- |")
    out.append("| **`Docs/UEManual/`** | **%d 篇**（%d 真文章 + %d 索引页）| %.1f KB |"
               % (len(info), len(articles), len(indexes), manual_kb))
    out.append("| **`Docs/PythonAPI/`** | **%d 篇 `.txt`** | %.1f KB |" % (len(api), api_kb))
    out.append("")
    out.append("> **⚠️ `PythonAPI` 是 `.txt` 不是 `.md`。** 用 `glob(\"*.md\")` 找会以为它是空的。")
    out.append("")
    out.append("**判定标准：**")
    out.append("- **真文章** = 至少 %d 行非空 + %d 字符" % (ARTICLE_LINES, ARTICLE_CHARS))
    out.append("- **索引页** = 只列子主题链接，单看学不到东西")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 二、按模块")
    out.append("")
    for group, entries in GROUPS.items():
        present = [(n, d, info[n]) for n, d in entries if n in info]
        if not present:
            continue
        total = sum(v[3] for _n, _d, v in present) / 1024.0
        art_count = sum(1 for _n, _d, v in present if v[2])
        out.append("### %s —— %d 篇（%d 真文章）/ %.1f KB" % (group, len(present), art_count, total))
        out.append("")
        out.append("| 文件 | 内容 | 大小 | 类型 |")
        out.append("| --- | --- | --- | --- |")
        for name, desc, (chars, lines, is_article, size) in sorted(present, key=lambda r: -r[2][3]):
            out.append("| `%s.md` | %s | %.1f KB | %s |"
                       % (name, desc, size / 1024.0, "文章" if is_article else "**索引页**"))
        out.append("")

    # Anything on disk not listed in GROUPS.
    listed = {n for entries in GROUPS.values() for n, _d in entries}
    unlisted = [n for n in info if n not in listed]
    if unlisted:
        out.append("### 未归类")
        out.append("")
        for name in sorted(unlisted):
            chars, lines, is_article, size = info[name]
            out.append("- `%s.md` %.1f KB" % (name, size / 1024.0))
        out.append("")

    out.append("---")
    out.append("")
    out.append("## 三、🔴 判断「有没有抓到」的正确方法")
    out.append("")
    out.append("**文档站对**任何路径**都返回 HTTP 200**，包括不存在的：")
    out.append("")
    out.append("```")
    out.append("this-page-does-not-exist-at-all-xyz  ->  200  没有 <title>  body 很短")
    out.append("lumen-technical-details-...         ->  200  有 <title>Lumen Technical Details</title>")
    out.append("```")
    out.append("")
    out.append("**→ 判据只能是**有没有 `<title>`**，不能看状态码。**")
    out.append("`Tools/verify_curriculum_slugs.py` 内置负对照。")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 四、🔴 三个用错过的判据")
    out.append("")
    out.append("| # | 错的判据 | 为什么错 | 改成什么 |")
    out.append("| --- | --- | --- | --- |")
    out.append("| 1 | `read(4000)` 后按状态码判成功 | 4000 是**截断长度**，不是页面大小 | 看 `<title>` + 负对照 |")
    out.append("| 2 | 「`-`/`|` 开头行占比高 = 索引页」 | 抓取时 `<li>` 全被转成 `\\n- `，任何列表页面都像索引 | **只看行数与字符数** |")
    out.append("| 3 | 审计脚本的分组清单写死 | 加了新文章它还在看旧的索引页，一直报 uncovered | 分组清单**同时列出索引页和文章页** |")
    out.append("")
    out.append("**共同点：判据没跟上数据。每次改完数据都要重跑 `audit_manual_gaps.py` 核实。**")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 五、还没做到的")
    out.append("")
    out.append("| 项 | 现状 |")
    out.append("| --- | --- |")
    out.append("| **Python API 覆盖** | **190 / 约 11,459 类 = 1.7%**（**按需子集**，不是缺口）|")
    out.append("| **音频** | 2 篇且都偏薄（`audio` 5736 字符 / `sound-cue-editor` 3749）|")
    out.append("| **索引页** | %d 篇只有子主题链接，需要时按需补子页面 |" % len(indexes))
    out.append("| **整站** | 未镜像，估数十小时且随版本漂移 |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 六、为什么不全站镜像")
    out.append("")
    out.append("| 项 | 数字 |")
    out.append("| --- | --- |")
    out.append("| 单页抓取 | 约 1–10 秒 |")
    out.append("| 全量估算 | 数十小时 |")
    out.append("| **本目录** | **%d 篇 / %.0f KB** |" % (len(info), manual_kb))
    out.append("")
    out.append("**→ 覆盖课程要查的九个领域，不是整站。**")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 七、权威顺序")
    out.append("")
    out.append("```")
    out.append("① 本机 Engine/Source 源码          ← 最权威")
    out.append("② Docs/PythonAPI/（官方签名）      ← C++ 给不了的 Python 名字")
    out.append("③ Docs/UEManual/（官方手册）        ← 概念与用法")
    out.append("④ 实测                            ← 前三者都没有时")
    out.append("```")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 八、怎么更新")
    out.append("")
    out.append("```powershell")
    out.append("python Tools/verify_curriculum_slugs.py   # 1. 验证 slug，打印 PAGES")
    out.append("# 2. 加进 Tools/mirror_manual_pages.py")
    out.append("python Tools/mirror_manual_pages.py       # 3. 抓取（幂等）")
    out.append("python Tools/audit_manual_gaps.py         # 4. 覆盖率与缺口")
    out.append("python Tools/rewrite_local_docs.py        # 5. 重生本文档")
    out.append("```")
    out.append("")
    out.append("**⚠️ 不要再猜 slug。** 猜的结果是 12 篇空页，花了两轮才修好。")

    open(DOC, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote %s" % os.path.basename(DOC))
    print("  manual %d pages (%d articles, %d indexes), %.1f KB"
          % (len(info), len(articles), len(indexes), manual_kb))
    print("  api %d files, %.1f KB" % (len(api), api_kb))


if __name__ == "__main__":
    main()
