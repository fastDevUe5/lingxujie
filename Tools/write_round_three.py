"""Write the third round summary and the full mastery table.

    python Tools/write_round_three.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 20. UE5 第三轮：音频系统 + UI 边界 + 网络（2026-11-26 19:15）

### 一、三个新增

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-AUDIO.md`** 扩写 | 6.2 KB | **5 个 SoundClass + 1 个衰减**（新增第九节）|
| **`UE5-UI.md`** | 5.5 KB | **实测边界**：Python 做不了 UMG 布局 |
| **`UE5-NETWORKING.md`** | 5.7 KB | 复制的三行声明 + **UE 复制 ≠ 墨香协议** |

### 二、三个「实测结论」

**① 音频系统建成**

```
sound classes: SC_Master, SC_Music, SC_SFX, SC_Voice, SC_Monster
attenuation saved: SA_Monster
磁盘确认：6 个 .uasset
```

**② UMG 的 Python 边界（决定性）**

```
WidgetTree / TextBlock / CanvasPanel 类型  -> 都暴露
WidgetBlueprint 的 widget/tree/root 属性  -> 一个都没有
WidgetBlueprintLibrary                     -> 不存在
UMGEditorSubsystem                         -> 未暴露
```

**结论：能造零件，造不出结构。UI 必须手点编辑器或写 C++。**

**③ UE 复制 ≠ 墨香服务端**

**两套完全不同的协议。即使架起墨香服务端，也不会走 UE 的复制。**
**墨香服务端的研究价值在「理解设计」，不在「和 UE 对接」。**

### 三、踩到的坑（74 条了）

| # | 坑 |
| --- | --- |
| **74** | 资产工厂类名**有的带 New 有的不带**（`SoundClassFactory` 无 New，`MaterialFactoryNew` 有）|

### 四、掌握度全表（本轮结束）

| 域 | 掌握 | 关键证据 |
| --- | --- | --- |
| 编辑器脚本 / MCP / 工具集 | **90%** | 自建工具集跑通，217 工具逐条读 |
| 核心架构 | **80%** | 继承链 + 生命周期 + 复制标志 |
| 子系统 | **75%** | 四层 + 三个判断问题 |
| 碰撞 | **70%** | 三组正交 + CTF |
| **材质** | **65%** | **做成 24 节点三平面** |
| 动画（引擎侧）| **55%** | DataModel 42+42 方法 + 写入配方 |
| **音频** | **50%** | **播过声音 + 建成 SoundClass 体系** |
| 动画（运行时）| **50%** | 槽位/蒙太奇/Notify/状态机 |
| 资产管线 | **45%** | 引用链实测 + 异步边界 |
| 渲染 | **35%** | Nanite 两套结构 + 350 后处理字段 |
| **UI** | **30%** | **实测边界（做不了）** |
| **网络** | **25%** | 三行声明 + RPC 方向 |

### 五、还没做的（诚实）

| 项 | 状态 |
| --- | --- |
| Lumen（全局光照）| 🔴 零 |
| MetaSounds | 🔴 零 |
| 动画蓝图实操 | 🔴 等 .mod 蒙皮 |
| UMG 实操 | 🔴 需人做 |
| 网络实操 | 🔴 P0 不需要 |

### 六、下一步

| 顺位 | 任务 | 能现在做吗 |
| --- | --- | --- |
| 1 | 清理 107 个遗留资产（先查 referencers）| ✅ |
| 2 | `merge_actors` 合并 96 个建筑 actor | ✅ |
| 3 | UMG 控件（需人配合）| ⚠️ 需人 |
| 4 | 动画实操 | ❌ 等 .mod |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 20." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 20; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
