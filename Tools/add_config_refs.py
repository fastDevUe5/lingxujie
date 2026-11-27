"""Wire the project configuration table into the index and add the anti-memory gotcha.

    python Tools/add_config_refs.py
"""

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

OLD = "| **Lumen 全局光照 / 为什么光照好看** | **`Docs/UE5-LUMEN.md`** | **本项目已开 Lumen**；前提是距离场 |"
NEW = (
    "| **Lumen 全局光照 / 为什么光照好看** | **`Docs/UE5-LUMEN.md`** | **本项目已开 Lumen**；前提是距离场 |\n"
    "| **这个工程到底开了哪些设置** | **`Docs/UE5-PROJECT-CONFIG.md`** | **92 个配置键一张表，先查这里** |"
)

GOTCHA = """
## 78. 「我没读过」不等于「没开」——判断有没有之前先读配置

- **症状**：两次判断错误，都是凭印象而不是读文件
  - 第 5 轮：「107 个遗留资产待清理」→ 实际是被引用的**贴图**
  - 第 7 轮：「Lumen 是零」→ 实际 `r.DynamicGlobalIlluminationMethod=1`，**从第一天就在跑**
- **根因**：把「我没研究过这个」当成了「项目没有这个」
- **修法**：判断「有没有」之前，按这个顺序查
  ```
  1. Config/*.ini              <- 项目设置（有没有开）
  2. AssetTools.get_asset_class <- 这是什么东西
  3. AssetTools.get_referencers <- 谁在用
  4. Saved/Logs/*.log          <- 运行时报了什么
  ```
  **四个都查完，再下结论。**
- **工具**：`python Tools\\audit_project_config.py` 输出 92 个配置键 + 来源文件
- **出处**：2026-11-26，两次判断错误的合并教训
"""


def main():
    index = open(INDEX, encoding="utf-8").read()
    if OLD in index and "UE5-PROJECT-CONFIG" not in index:
        index = index.replace(OLD, NEW)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already split or not found")

    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 78." in text:
        print("gotcha already present")
        return
    with open(GOTCHAS, "a", encoding="utf-8") as handle:
        handle.write(GOTCHA)
    print("added gotcha 78")


if __name__ == "__main__":
    main()
