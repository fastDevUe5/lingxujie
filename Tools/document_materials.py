"""Record the material pipeline: texture names, the DDS rejection, and where slots live.

Three things had to be found in order, and each was hiding behind the previous one: the material
block names its texture, the engine refuses the texture format on disk, and the assignment goes on
the component rather than the mesh asset.

    python Tools/document_materials.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十七、材质打通：Boss 不再是灰色（第 31 轮）

### 17.1 🎯 MATERIAL 块里有贴图名

**`MATERIAL` 块虽然大部分是二进制，但贴图文件名是**纯文本**：**

```
MATERIAL @28   size=1444
    'boss_mob01.tga'
    'Default'
```

**从 8 个模型抽出的材质引用：**

| 模型 | 贴图 |
| --- | --- |
| `boss001` | `boss_mob01.tga` |
| `198_bobu` | `N012-1.tga`, `N012.tga` |
| `108_bird` | `107_crow.tga` |
| `216` | `M_santa.tga` |
| `20_eagle_01` | `20_eagle01.tga` |
| `boss_cowf_01` | `EFF_07_01.tga`, `ice_fire_01.tga` |

**引用 9 个，**磁盘上全部找到（100%）**。**

**⚠️ 存的扩展名是 `.tga`，实际文件是 `.dds` —— 查找要换扩展名。**

### 17.2 🔴 UE 5.8 **拒绝**这批 DDS

```
LogFactory: FactoryCreateFile: Texture with TextureFactory (...boss_mob01.dds)
Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
Error: Image Import failed.
Error: Texture import failed
```

**这批 DDS 是 DXGI 格式（`BC1_UNORM` = DXGI 71），引擎的 DDS 读取器不接受。**

**修法：用 Pillow 转 PNG**
```python
image = Image.open("boss_mob01.dds")
image.load()
image.save("boss_mob01.png", "PNG")
```

**8 个全部转换成功：**
```
boss_mob01   512x512 RGBA
N012         256x256 RGBA
107_crow     128x256 RGBA
M_santa      512x256 RGBA
```

**转 PNG 后导入成功：**
```
MAT2: import produced 1 asset(s)
MAT2:   /Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01
MAT2: size 512x512
```

### 17.3 🔴 材质槽在**组件**上，不在**网格资产**上

**`SkeletalMesh` 没有 `set_material`：**
```
MAT2: FATAL: AttributeError("'SkeletalMesh' object has no attribute 'set_material'")
```

**正确做法：设在 `SkeletalMeshComponent` 上**
```python
component.set_material(index, material)     # 覆盖槽
```

**`mesh.set_editor_property("materials", [...])` 也不行：**
```
TypeError("SkeletalMesh: Failed to convert type 'list' to property")
```

### 17.4 结果

```
SLOT: material: M_Boss_Mob01
SLOT: mesh declares 1 slot(s)
SLOT: applied the material to 1 slot(s)
```

**Boss 现在有**材质** —— 画面里能看到棕色石材纹理的躯干，有细节，不再是灰的。**

### 17.5 完整链路（现在全通）

```
.mod  →  [解析网格 + 骨骼 + 材质]  →  glTF  →  UE SkeletalMesh + AnimSequence
                                    ↘
        .dds  →  Pillow 转 PNG  →  UE Texture2D  →  M_Boss_Mob01  →  组件材质槽
```

**这是**完整角色管线**：几何 + 骨骼 + 动画 + 材质。**

### 17.6 三个坑

| 编号 | 内容 |
| --- | --- |
| **#99** | 材质块的贴图名存 `.tga`，磁盘上是 `.dds` —— 换扩展名查找 |
| **#100** | 墨香 DDS 是 DXGI 格式，UE 5.8 不认（`DXGIFormat not supported : 71`）—— 转 PNG |
| **#101** | 材质槽覆盖在**组件**上，`SkeletalMesh` 没有 `set_material` |

### 17.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/extract_materials.py`** | 从 `.mod` 抽贴图名并解析到文件（100%）|
| **`Tools/convert_dds.py`** | DDS → PNG（绕开 UE 的 DDS 读取器）|
| **`Tools/apply_boss_material2.py`** | 导入贴图 + 建材质 |
| `Tools/assign_material_slots.py` | 在组件上设材质槽 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十七、材质打通" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
