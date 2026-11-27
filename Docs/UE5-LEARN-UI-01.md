# UE5 学习 · UI / UMG（第一块）：资产能建，其余全被挡住

> **这一块是**负面结论**，但证据链完整：五个环节逐个试过，只有第一个通了。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

**`umg-quick-start.md`（14.4 KB）是一篇**分步教程**（第一人称模板里做一个血量/能量/弹药 HUD）：**

| 步骤 | 内容 |
| --- | --- |
| 1 | 项目设置与蓝图调整 |
| 2 | 显示血量、能量、弹药（**Visual** 和 **Script** 两小节）|
| 3 | 延伸阅读 |

**→ 全部围绕**控件蓝图编辑器（UI）**。文档没有承诺 Python 能做到什么。**

---

## 二、镜像里没有 UMG 类，但运行时**有**

**本地 `Docs/PythonAPI` 里搜 Widget/UMG/UserWidget → **零篇**。
但运行时（✅ 实测）：**

```
unreal 属性提到 widget/umg/slate/canvas: 192 个

WidgetBlueprintFactory    True      ← 工厂存在
WidgetTree                True
CanvasPanel / TextBlock / Button / ProgressBar / Image   True
UserWidget                True
WidgetBlueprintLibrary    False     ← 这个没有

项目里的 widget 资产: WidgetBlueprint × 2（+ 我新建 1 = 3）
```

---

## 三、🔴 五个环节，只通了第一个

| # | 环节 | 结果 | 证据 |
| --- | --- | --- | --- |
| **1** | **建 WidgetBlueprint 资产** | ✅ **成功** | `WidgetBlueprintFactory` + `AssetTools.create_asset` |
| 2 | **拿到控件树** | ❌ | `widget_tree` / `tree` 属性不存在；`WidgetTree` 属性存在但**不可访问** |
| 3 | **往树里加控件** | ❌ | `CanvasPanel` / `TextBlock` **没有任何构造方法** |
| 4 | **构建实例** | ❌ | `new_object` + `construct()` → `desired_size` 仍是 **0.0 × 0.0** |
| 5 | **加进视口** | ❌ | `add_to_viewport(0)` → `is_in_viewport()` 仍是 **False** |

### 3.1 环节 4、5 在 PIE 里也失败

**我怀疑是「缺世界/玩家上下文」，于是在 PIE 里重试：**

```
game world: 'L_LightLab'
player controllers: 1            ← 玩家确实存在
player: 'PlayerController_0'
new_object                 -> 'DefaultBurnIn_C_2'
create_widget_for_player   -> 'DefaultBurnIn_C_0'
construct called
desired size: 0.0 x 0.0          ← 仍然零
added to viewport
in viewport after: False         ← 仍然没进去
```

**→ **有玩家也照样失败** —— 不是上下文问题，是这条 Python 通路本身不通。**

### 3.2 用**引擎自带**的控件蓝图也一样

**`/Engine/Sequencer/DefaultBurnIn.DefaultBurnIn` 是有真实内容的引擎资产，
但它的实例同样 `desired_size = 0.0 x 0.0`。**

**→ 不是「我建的资产是空的」的问题。**

---

## 四、🔴 结论

**在 UE 5.8.4 这个构建里：**

| 能做 | 不能做 |
| --- | --- |
| ✅ 用 `WidgetBlueprintFactory` 建控件蓝图**资产** | ❌ 编辑它的控件树 |
| ✅ 读它的 `generated_class()` | ❌ 往树里加面板/文本/按钮 |
| ✅ `new_object(generated_class)` 创建实例 | ❌ 让实例真正构建出界面 |
| | ❌ 把实例加进视口 |

**→ **UMG 的布局必须在**控件蓝图编辑器**里做。Python 只能建空壳。****

**→ 这和项目现状一致：项目的 HUD 是 **Canvas 绘制的 `LXJHUD`**，不是 UMG ——
很可能就是因为 UMG 这条路只能 UI 手工做。**

---

## 五、这一块学到什么

**1. 🔴 镜像里没有 ≠ 运行时没有。**
UMG 类在精选镜像里一篇都没有，但运行时 192 个属性可用。
**→ 判断 API 是否存在，要问运行时，不能只看镜像。**

**2. 🔴 `new_object` 只创建对象，不构建界面。**
`desired_size` 是判断「有没有真的构建」的可靠指标。

**3. 🔴 加了 PIE 也不通 —— 排除「缺上下文」这个解释。**
这一步很重要：如果只试编辑器就下结论，我会误判原因是「缺玩家」。

**4. 🎯 用引擎自带资产做对照，排除「我的资产是空的」。**
`DefaultBurnIn` 有内容，结果一样 → 不是资产的问题。

**5. 项目用 Canvas HUD 可能正是因为这个限制。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「UMG 可以做，只是没试」 | ❌ **Python 只能建空壳资产**，布局必须 UI |
| 「API 镜像没有就是没有」 | ❌ **必须问运行时** |

---

## 七、还没做到 / 可以再试的

| 项 | 说明 |
| --- | --- |
| `WidgetBlueprintLibrary` 为什么是 False | 可能需要特定插件/模块加载 |
| MVVM（`MVVMPanelWidgetViewExtension` 存在）| 可能是另一条路，没试 |
| `EditorUtilityWidget` | 编辑器工具控件，和游戏内 UMG 不同，没试 |
| C++ 侧能否建树 | 不在本目标范围 |

---

## 八、下一块

**转网络**（目标里的下一项）。

**⚠️ 本项目**没有网络**（之前调试系列已确认 `net` 命令静默、无 NetDriver），
所以网络这一块很可能也是「源码为主、实测受限」—— 但我会先确认，不预设。**

**⚠️ 编辑器状态：主关卡 116 actor、视口复位、练习关卡 10 actor。**
**新建的 `WBP_LabLabel` 是空的，留在 `/Game/Learning/` 作为「资产能建」的证据。**
