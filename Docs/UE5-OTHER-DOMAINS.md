# UE5 其余四域：音频 / UI / 网络 / 资产管线

> **本文只写"是什么、该用哪个、本项目要不要"—— 深度不如前几篇，因为还没读到底。**
> **诚实标注哪些是查过的、哪些是只知道存在。**

---

## 零、四域规模（实测，决定投入顺序）

| 域 | 头文件字节 | 核心类 |
| --- | --- | --- |
| **网络** | **349,816** | `UNetDriver` / `FRepLayout` |
| **资产管线** | 195,785 | `UAssetManager` / `FStreamableManager` |
| **音频** | 186,063 | `USoundWave` / `UAudioComponent` |
| **UI (Slate)** | 154,189 | `SWidget` / `SWindow` |
| **UI (UMG)** | 139,824 | `UUserWidget` / `UWidgetTree` |
| **合计** | **1,025,677** | — |

**规模不等于优先级。本项目是单机垂直切片，所以顺序是：**

| 顺序 | 域 | 理由 |
| --- | --- | --- |
| **1** | **资产管线** | **每天都在用**（`AssetTools` / `import_asset`），但只知调不知原理 |
| **2** | **音频** | 481 个音频文件已提取，迟早要播 |
| 3 | UI | 253 个窗口脚本已分析，但没有运行时框架 |
| 4 | 网络 | **P0 单机不需要** |

---

## 一、资产管线（最该先学）

### 1.1 四个类各管什么

| 类 | 头文件 | 职责 |
| --- | --- | --- |
| **`UAssetRegistry`** | 30,212 B | **资产索引**（不加载就能查有什么）|
| **`UAssetManager`** | 80,883 B | **加载策略**（按规则决定何时加载什么）|
| **`FStreamableManager`** | 45,988 B | **异步加载**（后台加载，完成回调）|
| **`UPackage`** | 38,702 B | 资产包（`.uasset` 文件本体）|

### 1.2 三者的分工（最关键的一句话）

> **`AssetRegistry` 回答"有什么"，`AssetManager` 回答"该不该加载"，
> `StreamableManager` 回答"什么时候加载完"。**

### 1.3 本项目的实际用法

**我们现在全靠 `EditorAssetLibrary`（编辑器专用）：**

```python
unreal.EditorAssetLibrary.load_asset(path)      # 同步加载，编辑器限定
unreal.EditorAssetLibrary.delete_asset(path)    # 删除
unreal.EditorAssetLibrary.does_asset_exist(path)  # 查存在
```

**⚠️ 这是**编辑器**API，打包后不能用。**
**运行时要用 `AssetManager` / `StreamableManager`。**

**对本项目的意义：** 我们现在是编辑器内建关卡，所以没问题。
**但一旦做"游戏里动态加载关卡/模型"，就必须换运行时 API。**

### 1.4 还没查的

| 项 | 状态 |
| --- | --- |
| 软引用（`TSoftObjectPtr`）怎么用 | 没查 |
| 资产包分块（chunk）与打包 | 没查 |
| 主资产（Primary Asset）的注册 | 没查 |

---

## 二、音频

### 2.1 六个类

| 类 | 头文件 | 职责 |
| --- | --- | --- |
| **`USoundWave`** | **83,432 B** | **导入的音频文件本体**（`.wav` / `.ogg`）|
| **`UAudioComponent`** | **50,140 B** | **挂在 Actor 上播放** |
| `USoundBase` | 20,065 B | 所有可播放声音的基类 |
| `UAudioSettings` | 13,830 B | 项目级设置 |
| `USoundClass` | 11,142 B | 音量分组（主音量/音效/音乐）|
| `USoundMix` | 7,454 B | 混音状态（比如"进战斗时压低音乐"）|

### 2.2 播放一个声音的两条路

| 方式 | 特点 |
| --- | --- |
| **`UAudioComponent`** | **挂在 Actor 上**，可以跟随移动、能停止、能调参数 |
| `UGameplayStatics::PlaySound2D/AtLocation` | **一次性播放**，播完就没 |

**判据：**
- 脚步、技能音效 → `PlaySoundAtLocation`（一次性）
- 背景音乐、循环环境音 → `UAudioComponent`（能控制）

### 2.3 本项目的音频现状

| 项 | 数量 |
| --- | --- |
| 已提取音频文件（研究区） | 481 |
| 被脚本实际引用 | 396 |
| 有文件 | 386 |
| **缺失（任何版本都没有）** | **10** |
| 韩服独有的怪物音效（已导入） | 35 |

**所以音频素材基本齐了。缺的是**播放逻辑**。**

### 2.4 还没查的

| 项 | 状态 |
| --- | --- |
| 3D 衰减（`AttenuationSettings`）怎么配 | 没查 |
| 音频空间化（`SoundAttenuation`） | 没查 |
| `MetaSounds`（UE5 的程序化音频） | 完全没碰 |
| 音频混音总线 | 没查 |

---

## 三、UI：UMG 和 Slate 是两层

### 3.1 层次关系

```
Slate（C++，底层）
  SWidget / SWindow / SlateStyle
     ↑ 被包裹
UMG（蓝图可做，上层）
  UUserWidget / UWidgetTree / UPanelWidget
     ↑ 运行时
游戏 HUD
  本项目用的是 ALXJHUD（Canvas 绘制，最轻的一层）
```

| | Slate | UMG | Canvas HUD |
| --- | --- | --- | --- |
| 语言 | C++ | 蓝图 + C++ | **C++ 直接画** |
| 能做交互控件 | ✅ | ✅ | ❌ 只能画 |
| 做起来快吗 | 慢 | 中 | **快** |
| 适合 | 编辑器 UI | **游戏 UI** | 血量/准星这类简单显示 |

### 3.2 本项目该选哪层

**现在用的是 `ALXJHUD`（Canvas），能画血条、灵力、技能栏 —— 够用但不适合做复杂界面。**

**AGENTS.md 里的美术要求是"毛笔感字体、暗底 + 细金边、竖排或仿篆刻标题" ——
这需要**样式表 + 自定义控件**，Canvas 画不出来。**

**所以做 UI 框架时该用 **UMG**，不是继续扩 Canvas。**

### 3.3 还没查的

| 项 | 状态 |
| --- | --- |
| `UUserWidget` 的生命周期 | 没查 |
| 控件样式（`SlateStyle`）怎么定义 | 没查 |
| 3D 世界 UI（`UWidgetComponent`，28,495 B）| 没查 —— **这个对本项目有用**（NPC 头顶名字、血条）|
| 输入绑定与焦点 | 没查 |

---

## 四、网络（P0 不需要，但要懂基础）

### 4.1 三个核心概念

| 概念 | 类 | 说明 |
| --- | --- | --- |
| **网络驱动** | `UNetDriver`（112,293 B） | 连接、收发、超时 |
| **复制布局** | `FRepLayout`（66,419 B） | **哪些属性要复制、怎么序列化** |
| **序列化原语** | `NetSerialization`（22,314 B） | 底层压缩与编解码 |

### 4.2 已经验证过的两条

**来自 `Docs/UE5-CORE-ARCHITECTURE.md`：**

| 结论 | 依据 |
| --- | --- |
| **GameMode 只在服务端** | `GameModeBase.h` **没有** `GetLifetimeReplicatedProps` |
| **GameState 会复制到客户端** | `GameStateBase.h` **有** |
| **HUD 只在客户端** | `HUD.h` **没有** `GetLifetimeReplicatedProps` |

### 4.3 本项目什么时候需要

**P0 是单机垂直切片 —— **不需要**。</br>
**但注意：墨香的完整服务端源码已经在手（研究区），本地架设时会用到网络层。**
**那时需要的不是 UE 的复制，而是**和墨香协议对接**，那是另一件事。**

### 4.4 还没查的

| 项 | 状态 |
| --- | --- |
| `UPROPERTY(Replicated)` / `ReplicatedUsing` 怎么写 | 没查 |
| RPC（`Server` / `Client` / `NetMulticast`）| 没查 |
| 相关性（relevancy）与优先级 | 没查 |
| 网络预测与回滚 | 没查 |

---

## 五、这四个域我掌握到什么程度（诚实）

| 域 | 掌握程度 | 能做什么 | 不能做什么 |
| --- | --- | --- | --- |
| **资产管线** | 🟡 **30%** | 会用编辑器 API | **不懂运行时加载** |
| **音频** | 🟡 **25%** | 知道有哪几个类 | **没播过一个声音** |
| **UI** | 🟡 **20%** | 知道三层关系 | **没做过一个 UMG 控件** |
| **网络** | 🔴 **10%** | 知道 GameMode/GameState 的复制差异 | **不会写任何复制** |

**对比已学的四块：**

| 块 | 掌握程度 |
| --- | --- |
| 核心架构 | 🟢 **80%** —— 继承链、生命周期、Gameplay 五类都查过 |
| 子系统 | 🟢 **75%** —— 四层结构 + 取用方式清楚 |
| 渲染 | 🟡 **35%** —— Nanite/后处理结构清楚，Lumen 没碰 |
| 碰撞 | 🟢 **70%** —— 三组正交概念 + CTF 选择清楚 |
| **编辑器脚本 / 工具集** | 🟢 **90%** —— 能自建、能验证、能查 217 个工具 |
| **动画格式（墨香侧）** | 🟢 **85%** —— 三条轨道全解，导入方案定了 |

---

## 六、重查命令

```powershell
python Tools\survey_remaining_domains.py   # 四域的规模与核心类
```
