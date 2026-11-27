"""Append the seventeenth round.

    python Tools/write_round_seventeen.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 34. 第十七轮：**完整管道打通 —— 动画进引擎了**（2026-11-26 24:00）

### 一、结果：一次导入产生四个资产

```
ANIM: import produced 4 assets
  Skeleton        SK_BirdAnim_Skeleton
  SkeletalMesh    SK_BirdAnim
  PhysicsAsset    SK_BirdAnim_PhysicsAsset
  AnimSequence    SK_BirdAnim_Anim        <- 动画序列
```

**日志原文：**
```
LogInterchangeEngine: Display: Interchange import completed
```

**动画长度 `sequence_length = 9.0` 秒 —— 与源文件一致（见第三节）。**

### 二、整个管道

```
mod/108_bird.mod    +   anm/108_birda.anm
       ↓ Tools/export_mod_anim_gltf.py
bird_anim.gltf + bird_anim.bin      （网格 + 动画在一个文件）
       ↓ AssetImportTask（不给 factory → Interchange）
SkeletalMesh + Skeleton + PhysicsAsset + AnimSequence
```

### 三、我算错了一个数字，导出是对的

**导入后长度 9.0 秒，我一开始以为应该是 4.5 秒。**

**实际：**
```
136 个关键帧，间隔 320 ticks
160 ticks/帧  →  每关键帧间隔 2 帧
→ 跨度 = 135 × 2 = 270 帧
→ 270 / 30 = 9.0 秒  ✓
```

**关键帧数 ≠ 帧数。** 又是「数字是真的，但被当成了别的东西」——
和第 5/7/10 轮同一类错误（gotcha #80 的三问法）。

### 四、踩到的坑（gotcha #83）

**glTF 的 `byteLength` 必须在**所有 accessor 写完之后**才算：**

```python
gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # 算早了
# 之后 add_view() 往 binary 追加动画数据
# → 声明值比实际小 → 导入器报「缓冲文件大小不匹配」
```

**症状像文件损坏，实际是顺序问题。**

### 五、只有 6/9 骨骼有动画轨

```
matched bones: 6 of 9 -> Bone02, Bone01, Bone05, Bone04, Bone07, Bone09
```

**其余 3 根（`Bone03`/`Bone06`/`Bone08`）在 `.anm` 里 `rot=0 pos=0 scale=0` ——
这个动作里它们不动，**不是丢失**。**

### 六、七轮的弧线

| 轮次 | 成果 | 方法 |
| --- | --- | --- |
| 11 | API 体量 11,459 类 | 实测代替引用 |
| 12 | `.mod` 容器 | 暴力搜索 |
| 13 | 排除 f32/f16 法线 | 否定实验 |
| **14** | **`.mod` 完全解开** | **读客户端源码** ← 转折 |
| 15 | 导出 → 骨骼网格可见 | 工程 |
| **16** | **`.anm` + 帧率 30fps** | **先读源码**（#81 生效）|
| **17** | **AnimSequence 进引擎** | 工程 |

### 七、下一批

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 5,305 模型 + 4,014 动画要脚本化 |
| **材质** | 导入警告「未指定材质的图元」|
| **角色模型** | 现在只验证了鸟（9 骨骼）；要试 96 骨骼人形 |
| **逆绑定矩阵** | 当前单位矩阵；姿态不对时再算 |
| **动画蓝图** | 有 AnimSequence 了，可以建状态机 |

### 八、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/MOXIANG-TO-UE-PIPELINE.md`** | 完整管道 + 两格式对照表 + 四个实现细节 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 34." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 34; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
