# UE5 Lumen：全局光照与反射（源码 + 工程实测）

> **先更正一条：我之前说"Lumen 是零"——**错了**。
> 本项目从第一天起就开着 Lumen，这是场景光照看起来还不错的原因。**
>
> **本篇把它的原理、开关和本项目的实际配置讲清。**

---

## 一、Lumen 是什么

**Lumen 是 UE5 的**全动态全局光照**和**反射**系统。**

| | 传统烘焙 | **Lumen** |
| --- | --- | --- |
| 间接光 | 烘焙进 lightmap | **实时光线追踪** |
| 改光照 | 要重新烘焙（几分钟到几小时）| **立刻看到** |
| 动态物体 | 不参与间接光 | **完全参与** |
| 成本 | 运行时便宜 | **运行时贵** |

**对游戏开发的意义：改一个灯的亮度，立刻看到整间屋子的变化。**

---

## 二、两个独立的开关（源码核实）

**`EngineTypes.h` 里的两个枚举，都注明了 `Must match r.<cvar>`：**

### 2.1 `EDynamicGlobalIlluminationMethod`（对应 `r.DynamicGlobalIlluminationMethod`）

| 值 | 名称 | 说明 |
| --- | --- | --- |
| **0** | `None` | 无动态 GI（仍可烘焙 lightmap）|
| **1** | **`Lumen`** | **Lumen GI**（本项目用这个）|
| 2 | `ScreenSpace` | **已废弃** |
| 3 | `Plugin` | 用插件 |

### 2.2 `EReflectionMethod`（对应 `r.ReflectionMethod`）

| 值 | 名称 | 说明 |
| --- | --- | --- |
| 0 | `None` | 无全局反射（仍可用反射球/平面反射）|
| **1** | **`Lumen`** | **Lumen 反射**（本项目用这个）|

**两者是**独立的**：可以开 Lumen GI 但用简单反射，反之亦然。**

---

## 三、🔴 Lumen 的硬前提（源码注释原文）

**`EDynamicGlobalIlluminationMethod::Lumen` 的注释：**
> *"Use Lumen Global Illumination for all lights, emissive materials casting light and
> SkyLight Occlusion. **Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing**
> and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing."*

**所以 Lumen 有两条路径：**

| 路径 | 前提 | 本项目的值 |
| --- | --- | --- |
| **软件光追（SDF）** | **`r.GenerateMeshDistanceFields=True`** | ✅ **已开** |
| 硬件光追 | 需支持 RT 的显卡 + 项目开关 | ❌ `r.Lumen.HardwareRayTracing=False` |

**关键概念：**网格**距离场（Mesh Distance Fields）**
> **这是把每个网格预处理成一个"离表面多远"的体素场。
> 光线在距离场里走，比在三角形里走快几个数量级 —— 这是软件光追能实时的原因。**

**⚠️ 代价：**
- **勾了 `GenerateMeshDistanceFields` 的网格，构建时间会变长**
- **大网格（比如 524,288 面的地形）的距离场很占内存**

---

## 四、本项目的完整渲染配置（实测）

**`Config/DefaultEngine.ini` 的 `[/Script/Engine.RendererSettings]`：**

```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.DefaultFeature.Bloom=True             ; 泛光
r.DefaultFeature.AutoExposure=False     ; 固定曝光
r.DefaultFeature.MotionBlur=False       ; 无运动模糊
r.AntiAliasingMethod=4                  ; = TSR
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
```

### 4.1 每一项为什么这么设（配置文件里的注释说明了）

| 设置 | 项目注释 | 评价 |
| --- | --- | --- |
| `DynamicGlobalIlluminationMethod=1` | "Next-gen look for the prototype: Lumen GI" | ✅ 现代 |
| `Shadow.Virtual.Enable=1` | 同上 | ✅ 现代（VSM 和 Lumen 是配套的）|
| `AutoExposure=False` | **"headless screenshots used to be washed out because auto exposure was still adapting when the capture fired"** | ✅ **很好的理由**（截图可复现）|
| `MotionBlur=False` | 同上 | ✅ 截图需要 |
| `AntiAliasingMethod=4` | "TSR instead of TAA: cleaner edges on the low-poly silhouettes" | ✅ 有依据 |
| `GenerateMeshDistanceFields=True` | 无注释 | ✅ **Lumen 必需** |
| `AllowStaticLighting=False` | 无注释 | ✅ 全动态，不用烘焙 |

**这个配置**比大多数原型项目成熟** —— 每一项都有理由，且注释里写了遇到过的问题。**

### 4.2 还有一个值得注意的注释

```ini
; Revisit for the MMO scale test (P0.5) - Lumen is expensive with many players on screen.
```

**这说明在配置时就意识到了 Lumen 的 MMO 扩展性问题。**
**这不是"忘了"，是"知道并推迟决定"。**

---

## 五、Lumen 的代价（MMO 规模的真正问题）

| 成本 | 说明 | 对 MMX 的影响 |
| --- | --- | --- |
| **GPU** | 每帧追光 | 多人同屏时爆 |
| **内存** | 距离场常驻 | 大地图 × 64 张 = 爆炸 |
| **首次构建** | 生成距离场 | 打包时间变长 |

### 5.1 MMO 规模下的三条路

| 方案 | 做法 |
| --- | --- |
| **A. 只用 Lumen 做主角附近** | 远处切烘焙/简化（Lumen 支持场景设置）|
| **B. 全烘焙 + 少量动态** | 关 Lumen，用 lightmap（改光照要重烘）|
| **C. 混合** | 室内 Lumen、室外烘焙 |

**本项目现在选的是"全 Lumen"，对 1 个玩家没问题。
P0.5 的 MMO 规模测试时**必须重新决定** —— 配置文件里已经写明了这一点。**

---

## 六、其他关键枚举（本项目的值）

| cvar | 值 | 含义 |
| --- | --- | --- |
| `r.AntiAliasingMethod` | **4** | **TSR**（Temporal Super Resolution）|
| `r.Shadow.Virtual.Enable` | 1 | 虚拟阴影贴图 |

**`r.AntiAliasingMethod` 的取值（UE5）：**
```
0 = None
1 = FXAA
2 = TAA
3 = MSAA
4 = TSR      ← 本项目
```

**TSR 是 UE5 的默认推荐 —— 比 TAA 清晰，尤其对低模边缘。**

---

## 七、掌握程度（Lumen / 渲染）

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| Nanite 两套结构 | 🟢 清楚 | 🟢 清楚 |
| 351 个后处理字段 | 🟢 清楚 | 🟢 清楚 |
| **Lumen 是什么** | 🔴 **零** | 🟢 **清楚** |
| **Lumen 的两个独立开关** | 🔴 | 🟢 **源码确认枚举值** |
| **Lumen 的硬件前提（距离场）** | 🔴 | 🟢 **清楚** |
| **本项目的 Lumen 配置** | 🔴 **以为没开** | 🟢 **实测：已开，且配置成熟** |
| **MMO 规模的 Lumen 问题** | 🔴 | 🟢 **清楚（配置里已注明）** |
| TSR / VSM | 🔴 | 🟢 **清楚** |
| **实际调过 Lumen 参数** | 🔴 | 🔴 **没调过** |
| 硬件光追 | 🔴 | 🔴 **没试过** |

**渲染：从 35% → **55%**。**

**涨的是：
- 更正了一个错误认知（Lumen 不是零，是在跑）
- 明白了它为什么能跑（距离场）
- 明白了它的代价（MMO 规模要重决定）

没涨的是：没实际调过任何 Lumen 参数。**

---

## 八、下一步（如果要动手）

**最小验证：关掉 Lumen，截图对比。**

```
1. 改 r.DynamicGlobalIlluminationMethod=0
2. 重启编辑器（这个 cvar 可能要重启才生效）
3. 截图
4. 对比：阴影里的区域会变黑（没有间接光）
5. 改回 1，再截图
```

**⚠️ 这需要重启编辑器 —— 按规则要先问人。**

**这一步能验证：Lumen 确实在贡献间接光，不是心理作用。**

---

## 九、重查命令

```powershell
# 看项目渲染配置
Select-String -Path Config\DefaultEngine.ini -Pattern 'Lumen|GlobalIllumination|ReflectionMethod|Virtual|DistanceFields'

# 看枚举定义
Select-String -Path 'C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Engine\Classes\Engine\EngineTypes.h' -Pattern 'EDynamicGlobalIlluminationMethod' -Context 0,20
```
