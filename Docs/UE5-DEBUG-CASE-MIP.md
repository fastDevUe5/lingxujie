# 实战诊断 007：一条历史警告，和一个健康的资产

> **起点：日志里 `T_Boss_Mob01 contains no miplevels!`。**
>
> **结论：这是 11:57 那次**DDS 导入失败**的残留记录。
> 现在的资产有**完整的 10 级 mip 链**，是健康的。**
>
> **但那次失败的错误信息本身很有价值 —— 它精确指出了 DDS 的第三种失败模式。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、起点：上下文揭示这是一次**导入失败**

**日志原文（✅ 实测）：**
```
InterchangeEngine: Display: Interchange start importing source [.../boss_mob01.dds]
InterchangeImport: Warning: Imported DDS files must either be a single base mip,
                           or a full mip chain, not a partial mip chain
LogTexture:        Warning: Texture2D /Game/Moxiang/Textures/T_Boss_Mob01 contains no miplevels!
LogUObjectGlobals: Warning: 未找到Object"Object /Game/Moxiang/Textures/T_Boss_Mob01"
InterchangeEngine: Display: Interchange import completed [.../boss_mob01.dds]
InterchangeEngine: Error:   [.../boss_mob01.dds : InterchangeDDSTranslator] DDS D...
```

**→ 完整链条：**
```
DDS 的 mip 链是「部分」的 → Interchange 拒收 → 贴图没有 mip
→ 对象找不到 → 翻译器报错 → 导入实际失败
```

**⚠️ 所以「contains no miplevels」**不是**一条独立的贴图问题，
它是**导入失败的下游症状**。**

---

## 二、真正的答案：现在健康吗

**Python 读不到 mip 数（`platform_data` / `asset_import_data` 都不可读）。
改用引擎自己的控制台命令 `listtextures`（`memreport` 里也用它）。**

**表头（✅ 实测）：**
```
MaxAllowedSize: Width x Height (Size in KB, Authored Bias), Current/InMem: Width x Height (Size in KB),
Format, LODGroup, Name, Streaming, UnknownRef, VT, Usage Count, NumMips, Uncompressed
```

**🔴 最后一列前面有 **`NumMips`** —— 这就是要的那个数。**

**实测结果：**
```
512x512 (192 KB, 0), 512x512 (192 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01, YES, NO, NO, 40, 10, NO

64x64 (8 KB, 0), 64x64 (8 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/tile_108_road01.tile_108_road01, NO, NO, NO, 1, 7, NO
```

| 贴图 | 尺寸 | **NumMips** | 完整吗 |
| --- | --- | --- | --- |
| `T_Boss_Mob01` | 512×512 | **10** | ✅ 512→256→128→64→32→16→8→4→2→1 正好 10 级 |
| `tile_108_road01` | 64×64 | **7** | ✅ 64→32→16→8→4→2→1 正好 7 级 |

**→ **两张都是完整 mip 链。当前资产健康。**

**顺带：`T_Boss_Mob01` 的 `Usage Count = 40`** —— 正好对应 Boss 的 40 个材质槽（第 38 轮那次赋值）。

---

## 三、🎯 这次失败留下的最有价值的东西：**精确的错误信息**

**三条 DDS 失败模式，错误信息都很明确：**

| 模式 | 错误信息 | 怎么办 |
| --- | --- | --- |
| **格式不支持** | `DDS DXGIFormat not supported : 71 : BC1_UNORM` | **转 PNG**（gotcha #100）|
| **mip 链是部分的** | `Imported DDS files must either be a single base mip, or a full mip chain, not a partial mip chain` | **同上，或补全 mip** |
| 文件本身坏了 | `DDS D...` 截断的信息 | 换源文件 |

**→ 这三条都能从日志里直接读出**该做什么**。**

**⚠️ 共同结论：这个项目的 DDS 通路不可靠，统一走 **DDS → PNG → UE** 是正确选择。**
**（`Tools/convert_dds.py` 用 Pillow，绕开 UE 的 DDS 读取器。）**

---

## 四、🔴 方法论：怎么分清「历史警告」和「当前问题」

**日志是**累积**的 —— 一次会话里所有尝试都留着。
**同一条警告可能在修复之前产生，修复之后仍然留在文件里。**

| 判据 | 历史警告 | 当前问题 |
| --- | --- | --- |
| **时间戳** | 早于最后一次修复 | 最近一次操作之后 |
| **后续有没有成功记录** | 后面有 `import completed` / 成功日志 | 没有 |
| **当前实测状态** | **健康** | 有问题 |

**→ 唯一可靠的办法：**直接测当前状态**，不要相信日志里的旧行。**

**这一轮就是：警告说「没有 mip」，实测说「有 10 级」。信实测。**

**这和案例 006 是同一课的两面：
**日志告诉你**发生过什么**，不告诉你**现在是什么**。****

---

## 五、顺带发现：Python 读不到的两个属性

| 想读 | 结果 |
| --- | --- |
| `platform_data` | `Failed to find property 'platform_data'` |
| `asset_import_data.get_editor_property("generate_mips")` | 静默无输出 |

**→ 贴图的 mip 信息**只能靠 `listtextures`（控制台）拿到，Python 不行。**

**→ 这条要加进 `UE5-DEBUG-TOOLKIT.md` 的「查不出什么」表。**

---

## 六、待办

| 事项 | 状态 |
| --- | --- |
| 把 DDS 三种失败模式写进 gotcha | 待做 |
| 给 `diagnose.py` 加 `listtextures` 检查（`NumMips` 与尺寸是否匹配）| 待做 |
| 更新工具包的「查不出什么」表 | 待做 |

**⚠️ 代码一字未改。**
