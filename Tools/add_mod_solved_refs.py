"""Record the methodological failure that cost four rounds, and point the index at the solution.

The mod format was in the client source the whole time. Four rounds were spent scanning binary for
a structure that `Physique.cpp` spells out in fifteen lines. That is the lesson worth keeping, more
than the format itself.

    python Tools/add_mod_solved_refs.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRY = """
## 81. 逆向格式先读源码 —— 研究区有客户端 C++ 源码，别从二进制猜

- **症状**：花了**四轮**（第 11–14 轮）从二进制反推 `.mod` 的网格与蒙皮布局，
  试过三种块头长度、三种法线格式（f32/f16/u8）、固定 4 影响的权重扫描 —— **全部失败**
- **实际**：研究区 `client_src\\tw\\4DyuchiGXGeometry\\` 有**完整的客户端 C++ 源码**：
  ```
  geom_obj.cpp     -- CMeshObject::ReadFile     读网格的完整顺序
  object.cpp       -- CBaseObject::ReadFile     324 字节基类头
  face_group.cpp   -- CFaceGroup::ReadFile      28 字节面组头
  Physique.cpp     -- CPhysique::ReadFile       ★ 蒙皮（15 行代码）
  typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM 结构体
  ```
  **`FORMAT-REFERENCE.md` 里甚至摘录了这些源码。**
- **根因**：我把「研究区是数据仓库」当成了「研究区只有数据」。
  实际它有**反编译出来的源码**，那是比二进制更权威的一手资料。
- **修法**：逆向任何格式前，先做这一件事
  ```powershell
  # 研究区有没有这个格式的读取代码？
  Select-String -Path 'C:\\Users\\tk\\Desktop\\moxiang-study\\client_src\\tw\\**\\*.cpp' `
      -Pattern 'ReadFile|LoadFile' -List
  # 研究区有没有格式文档？
  Get-ChildItem 'C:\\Users\\tk\\Desktop\\moxiang-study\\Docs' -Recurse -Filter '*format*'
  ```
- **代价**：四轮 VS 一分钟
- **出处**：2026-11-26，`.mod` 格式解开后的复盘
"""

OLD_INDEX = "| **`.mod` 蒙皮权重** | **`Docs/MOD-SKIN-STATUS.md`** | **未解完**；块长度不含头；一个候选已排除 |"
NEW_INDEX = (
    "| **`.mod` 网格/蒙皮格式** | **`Docs/MOD-FORMAT-SOLVED.md`** | **已完全解开**；"
    "四文件逐字节验证（tail=0）|\n"
    "| **逆向格式从哪开始** | **gotcha #81** | **先读研究区的客户端 C++ 源码** |"
)


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 81." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 81")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index:
        index = index.replace(OLD_INDEX, NEW_INDEX)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row not found; check whether it was already changed")


if __name__ == "__main__":
    main()
