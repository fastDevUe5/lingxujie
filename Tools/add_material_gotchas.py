"""Add gotchas 99 through 101 for the material pipeline.

    python Tools/add_material_gotchas.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 99. 墨香材质块的贴图名存 `.tga`，磁盘上是 `.dds`

- **现象**：MATERIAL 块里的纯文本是 `boss_mob01.tga`，
  但真正的文件是 `resources/dds/boss_mob01.dds`
- **修法**：查找时**换扩展名**，不要信任存的扩展名
  ```python
  stem = os.path.splitext(name)[0]
  for folder, extension in ((DDS, ".dds"), (TGA, ".tga")):
      candidate = os.path.join(folder, stem + extension)
      if os.path.exists(candidate):
          return candidate
  ```
- **实测**：8 个模型共 9 个贴图引用，**100% 解析成功**
- **出处**：2026-11-26，材质管线

## 100. 墨香 DDS 是 DXGI 格式，UE 5.8 不认

- **症状**：
  ```
  LogFactory: FactoryCreateFile: Texture with TextureFactory (...boss_mob01.dds)
  Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
  Error: Image Import failed.
  Error: Texture import failed
  ```
- **根因**：这批 DDS 用 DXGI 格式头（`BC1_UNORM` = DXGI 71），
  引擎的 DDS 读取器只接受旧的 DXT 头，`import_asset_tasks` 走 Interchange 或
  显式 `TextureFactory` 都失败
- **修法**：**用 Pillow 转 PNG 再导入**
  ```python
  image = Image.open(source + ".dds")
  image.load()
  image.save(target + ".png", "PNG")
  ```
  **8 个全部转换成功，原始尺寸保留（512x512 / 256x256 / 128x256）**
- **一般化**：**格式不认时不要换工具，先换格式**
- **出处**：2026-11-26，材质管线

## 101. 材质槽覆盖在**组件**上，`SkeletalMesh` 没有 `set_material`

- **症状**：
  ```
  AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
  TypeError("SkeletalMesh: Failed to convert type 'list' to property")
  ```
- **根因**：`SkeletalMesh` 资产只有导入时带的那份材质列表，
  **放置时的覆盖属于组件** —— 这是 UE 的常规分工，不是 API 缺失
- **正确做法**：
  ```python
  component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
  component.set_material(index, material)     # 按槽号覆盖
  ```
- **槽数从网格读**：`len(mesh.get_editor_property("materials"))`
- **出处**：2026-11-26，材质管线
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 99." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotchas 99, 100 and 101")


if __name__ == "__main__":
    main()
