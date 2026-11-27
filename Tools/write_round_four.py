"""Append the fourth round to the handoff, including the procedural lesson.

    python Tools/write_round_four.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 21. UE5 第四轮：网格合并实测 + 找 API 的正确方法（2026-11-26 19:30）

### 一、网格合并：学会了，然后决定不用

**实测结果：**
```
MERGE: found 96 building actors
MERGE: merged mesh SM_SM_Lanzhou_City, material slots 96
合并后：64,740 三角形 / 85,522 顶点 / 96 个材质槽
```

**🔴 最重要的认知：合并**减 actor，不减 draw call**。**

> **96 actor + 96 材质 = 96 次 draw call**
> **1 actor + 96 材质 = 仍然 96 次 draw call**

**所以合并的真实收益只有两个：大纲整洁、整座城能一起移动。**

**决定：不采用。** 理由：
1. 对 draw call 无帮助
2. 96 个 actor 便于单独调整
3. 96 不算多

**合并产生的 asset 留在磁盘（`SM_SM_Lanzhou_City`），actor 已删除，关卡恢复原状。**

### 二、🔴 本轮最大的方法收获：找 API 读引擎工具的实现

**踩了三个坑才找对合并 API：**
```
1. EditorLevelLibrary.merge_actors        -> 不存在
2. MeshMergingSettings.generate_lightmap_uv -> 属性不存在
3. 正确答案：StaticMeshEditorSubsystem.merge_static_mesh_actors(actors, options)
```

**怎么找到的：读引擎自带 `SceneTools.merge_actors` 的实现 —— 它内部就这么调。**

> **引擎自己的 217 个工具是**最好的 API 示例**，
> 因为它们只能调用真实存在的方法。**

**这条已写进 `Docs/UE5-MESH-MERGE.md` 第六节，应该进开工流程。**
**已加入 `AGENTS.md` 规则 0 的查询顺序（见下）。**

### 三、新增文档

| 文档 | 大小 |
| --- | --- |
| **`UE5-MESH-MERGE.md`** | 4.9 KB |

### 四、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **网格合并** | 0 | **70%**（跑通 + 有判断）|

### 五、下一步（转向实操）

| 顺位 | 任务 | 说明 |
| --- | --- | --- |
| 1 | 清理 107 个遗留资产 | 先查 referencers |
| 2 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 了 |
| 3 | 动画实操 | 等 .mod 蒙皮 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 21." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 21; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
