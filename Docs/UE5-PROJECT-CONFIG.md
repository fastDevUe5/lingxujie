# 灵虚界项目配置全表（实测）

> **这个工程的所有关键配置，一个文件一张表。**
> **为什么单独做这份：我已经有**两次**判断错了，都是因为凭印象而不读配置。**
>
> **重查命令：`python Tools\audit_project_config.py`**

---

## 一、四个配置文件

| 文件 | 大小 | 段 |
| --- | --- | --- |
| `DefaultEngine.ini` | 3.1 KB | `GameMapsSettings` / `RendererSettings` / `Engine` / `AndroidFileServer` / `WindowsTargetSettings` |
| `DefaultInput.ini` | 9.3 KB | `InputSettings` |
| `DefaultGame.ini` | 0.4 KB | `GeneralProjectSettings` / `GameSession` / `ProjectPackagingSettings` |
| `DefaultDeviceProfiles.ini` | 1.4 KB | `GlobalDefaults` / `DeviceProfile` |
| **合计** | **~14 KB** | **92 个配置键** |

---

## 二、渲染（12 项，全部实测）

| 项 | 键 | 值 | 含义 |
| --- | --- | --- | --- |
| **全局光照** | `r.DynamicGlobalIlluminationMethod` | **1** | **Lumen** |
| **反射** | `r.ReflectionMethod` | **1** | **Lumen** |
| **抗锯齿** | `r.AntiAliasingMethod` | **4** | **TSR** |
| **虚拟阴影** | `r.Shadow.Virtual.Enable` | `1` | 开 |
| **网格距离场** | `r.GenerateMeshDistanceFields` | `True` | **Lumen 软件光追的前提** |
| **静态光照** | `r.AllowStaticLighting` | `False` | 全动态 |
| **自动曝光** | `r.DefaultFeature.AutoExposure` | `False` | **固定曝光**（截图可复现）|
| 泛光 | `r.DefaultFeature.Bloom` | `True` | 开 |
| 运动模糊 | `r.DefaultFeature.MotionBlur` | `False` | 关（截图需要）|
| **Lumen 硬件光追** | `r.Lumen.HardwareRayTracing` | `False` | **走软件光追** |
| **光追模式** | `RayTracingMode` | **`Full`** | ⚠️ **与上一项不一致** |
| 其它 | — | — | — |

### 2.1 ⚠️ 一个值得注意的不一致

```
RayTracingMode = Full              ← 引擎级光追总开关打开
r.Lumen.HardwareRayTracing = False  ← 但 Lumen 不用硬件光追
```

**这两个不矛盾，但容易误解：**
- `RayTracingMode=Full` 影响**非 Lumen** 的光追特性（如光追阴影/AO，如果启用）
- **Lumen 自己走软件光追**（依赖距离场）

**所以现在的实际状态是：Lumen 全软件，硬件光追没被 Lumen 使用。**

**如果想试硬件光追：**
```ini
r.Lumen.HardwareRayTracing=True
```
**前提：显卡支持 + `RayTracingMode=Full`（已满足）。**

---

## 三、输入（2 项）

| 项 | 键 | 值 |
| --- | --- | --- |
| 玩家输入类 | `DefaultPlayerInputClass` | `/Script/EnhancedInput.EnhancedPlayerInput` |
| 输入组件类 | `DefaultInputComponentClass` | `/Script/EnhancedInput.EnhancedInputComponent` |

**⚠️ 但 `LXJCharacter.cpp` 里**没有任何输入绑定** —— 它在 `Tick` 里轮询 `IsInputKeyDown`。**

**详细分析见 `Docs/UE5-INPUT.md`。**

---

## 四、Gameplay / 地图

| 项 | 键 | 值 |
| --- | --- | --- |
| 默认地图 | `GameDefaultMap` | `/Game/Maps/LingXuJie.LingXuJie` |
| 编辑器起始图 | `EditorStartupMap` | `/Game/Maps/LingXuJie.LingXuJie` |
| 默认 GameMode | `GlobalDefaultGameMode` | `/Script/LingXujie.LXJGameMode` |

---

## 五、贴图预算（`DefaultDeviceProfiles.ini`）

**这是 AGENTS.md 里"贴图上限 2K"的落地点：**

| 组 | 上限 |
| --- | --- |
| World / NormalMap / Character | **2048** |
| Specular / Effects | **1024** |

**为什么有这个：1080p/60 的目标下 4K 只是浪费下载时间和显存。**

---

## 六、这份表防止的两个错误

### 错误 1：第 5 轮 —— 「107 个遗留资产」

**我根据「名字不在清单里」推断它们是遗留物。**
**实际：它们是材质实例引用的**贴图**。**

**正确的查法不是读配置，而是查 `get_asset_class` + `get_referencers`。**

### 错误 2：第 7 轮 —— 「Lumen 是零」

**我根据"没读过 Lumen 源码"推断"项目没开"。**
**实际：`r.DynamicGlobalIlluminationMethod=1`，从第一天就在跑。**

**正确查法：读 `DefaultEngine.ini`。**

### 教训

> **「我不知道」≠「没有」。**
> **判断"有没有"之前，先查配置、查资产、查日志 —— 别查记忆。**

---

## 七、配置文件里的注释值得读

**这个工程的配置文件写得比一般项目好 —— 每项都带理由：**

```ini
; Next-gen look for the prototype: Lumen GI + virtual shadow maps.
; Revisit for the MMO scale test (P0.5) - Lumen is expensive with many players on screen.

; Fixed exposure: headless screenshots used to be washed out because auto exposure was still
; adapting when the capture fired. Locking it also keeps a consistent look between runs.

; TSR instead of TAA: cleaner edges on the low-poly silhouettes (Epic's default for new 5.x projects).
```

**这三条注释说明：**
1. **选了 Lumen 但知道 MMO 规模问题** —— 知道并推迟
2. **固定曝光是为了截图可复现** —— 遇到过问题并解决
3. **TSR 是为了低模边缘** —— 有依据的选择

**这比"全用默认值"成熟得多。**

---

## 八、还没查的配置

| 段 | 内容 |
| --- | --- |
| `WindowsTargetSettings` | Windows 平台特定设置（没看）|
| `ProjectPackagingSettings` | 打包设置（没细看）|
| `DeviceProfile` | 设备分级（只看了贴图上限）|
| `AndroidFileServer` | 安卓相关（本项目不用）|

---

## 九、重查命令

```powershell
python Tools\audit_project_config.py
```

**输出 92 个配置键 + 来源文件 + 关键项的中文解读。**
