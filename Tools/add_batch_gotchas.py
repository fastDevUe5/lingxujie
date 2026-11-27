"""Record the two parser bugs the batch exposed, and wire the status doc into the index.

    python Tools/add_batch_gotchas.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRIES = """
## 88. `.mod` 的法线是**条件性**的（LIGHT_MAP 和 ALIGN_VIEW 都没有）

- **症状**：批量导出时部分模型报
  `unpack_from requires a buffer of at least N bytes ... (actual buffer size is N-20)`
  —— **跑到文件末尾之外十几到二十字节**
- **根因**：客户端源码里法线读取有两个前置条件
  ```c
  if (meshFlag.GetShadeType() == SHADE_TYPE_LIGHT_MAP)
      m_pLightTexture->ReadFile(pFP);          // 光图代替法线
  else if (meshFlag.GetTransformType() != TRANSFORM_TYPE_ALIGN_VIEW)
      FSRead(normals, 12 * dwVertexNum);        // 两个条件都要过
  ```
  **`mesh_flag` 位域（`mesh_flag.h`）：**
  | 掩码 | 含义 |
  | --- | --- |
  | `0x0F` SHADE_TYPE | 0=VERTEX_LIGHT_IM / 1=VERTEX_LIGHT_RT / **3=LIGHT_MAP** |
  | `0xF0` TRANSFORM_TYPE | 0=SOLID / 0x10=NOT_SOLID / **0x30=ALIGN_VIEW** / 0x50=ILLUSION |
  | `0x100` RIGID_TYPE | 刚体 |
  | `0x200` PICK_ENABLE | 可拾取 |
  | `0x7F000000` RENDER_ZPRIORITY | 渲染优先级 |
  | **`0x80000000` WRITE_ZBUFFER** | **写 Z 缓冲（与解析无关）** |
- **修法**：先判两个条件，再决定读不读法线；没有法线时给 glTF 一个常量 `(0,0,1)`
  —— 平涂正是源文件不写法线的意思
- **出处**：2026-11-26，批量导出

## 89. `.anm` 走块要自校验，否则会撞进尾部资源引用

- **症状**：`.anm` 解析报 `unpack_from requires 20 bytes`，20 正是 `<5I` 头的大小
- **根因**：`.anm` 最后一块后面有**资源引用文本**（`.dds` / `.chx` 文件名）。
  走法只看 `0xF000` 标记和 size，撞进尾部后把随机字节当成了块头
- **修法**：块大小自校验
  ```python
  expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
  if expected != size:
      break        # 走到尾部了
  ```
  **和 `.mod` 的验证同一手法：让数据自己证明自己**
- **出处**：2026-11-26，批量导出
"""

OLD_INDEX = "| **人形角色导入进度 / 两个坑** |"
NEW_INDEX = ("| **批量导出 / 成功率 / 下一步** | **`Docs/BATCH-EXPORT-STATUS.md`** | "
             "**100/100 导出成功**；`.chx` 才是正确配对来源 |\n"
             "| **人形角色导入进度 / 两个坑** |")


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 88." in text:
        print("gotchas already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRIES)
        print("added gotchas 88 and 89")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index and "BATCH-EXPORT-STATUS" not in index:
        index = index.replace(OLD_INDEX, NEW_INDEX, 1)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already changed")


if __name__ == "__main__":
    main()
