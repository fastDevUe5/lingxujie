"""Append the two gotchas found while mapping the rendering settings.

Written to a file rather than passed inline, because the text contains quotes and backslashes
that PowerShell mangles when a here-doc is handed to python -c.

    python Tools/add_rendering_gotchas.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRIES = """
## 69. MCP 工具的资产参数要完整对象路径，不是资产路径

- **症状**：`StaticMeshTools.is_nanite_enabled(mesh="/Game/Moxiang/SM_Lanzhou_Terrain")` 报
  `Parameter error: ... is not a valid object path for property 'mesh'`
- **根因**：这些工具的参数类型是 `unreal.Object` 引用，需要 `/Game/文件夹/资产名.对象名` 格式
- **修法**：
  ```
  错误: /Game/Moxiang/SM_Lanzhou_Terrain
  正确: /Game/Moxiang/SM_Lanzhou_Terrain.SM_Lanzhou_Terrain
  ```
  两者通常同名，但路径里必须出现**两次**
- **出处**：2026-11-26，查地形 Nanite 状态

## 70. 碰撞的正确工具是 generate_convex_collisions，不是关掉 Nanite

- **症状**：之前为了「Nanite 不提供复杂碰撞」，把地形的 Nanite 关掉了
- **根因**：关 Nanite 是治症状。Nanite 的碰撞来自 Fallback 网格
  （`FMeshNaniteSettings.GenerateFallback` / `FallbackPercentTriangles`），
  而引擎另外提供了碰撞生成工具
- **修法**：
  ```
  StaticMeshTools.generate_convex_collisions(mesh)   -> 生成凸包
  StaticMeshTools.remove_collisions(mesh)            -> 清除
  StaticMeshTools.set_nanite_enabled(mesh, True)     -> 保留 Nanite
  ```
  **注意：凸包不适合地形** —— 地形会变成一块大平板。
  地形仍应用 `CTF_USE_COMPLEX_AS_SIMPLE`（本项目已在用）
- **出处**：2026-11-26，读 static_mesh.py 源码
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 69." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRIES)
    import re
    numbers = re.findall(r"^## (\d+)\.", text + ENTRIES, re.M)
    print("appended; total gotchas now %d, last %s" % (len(numbers), numbers[-3:]))


if __name__ == "__main__":
    main()
