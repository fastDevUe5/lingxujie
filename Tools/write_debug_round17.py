"""Append the seventeenth debugging round.

    python Tools/write_debug_round17.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 74. 调试系列第 17 轮：**历史警告 vs 当前状态**（2026-11-26 59:00）

### 一、起点：最后一条未查的告警

**`LogTexture: Warning: Texture2D T_Boss_Mob01 contains no miplevels!`**

### 二、上下文揭示这是**导入失败的下游症状**

```
InterchangeImport: Warning: Imported DDS files must either be a single base mip,
                           or a full mip chain, not a partial mip chain
LogTexture:        Warning: T_Boss_Mob01 contains no miplevels!
LogUObjectGlobals: Warning: 未找到Object"T_Boss_Mob01"
InterchangeEngine: Error:   [.../boss_mob01.dds : InterchangeDDSTranslator] DDS D...
```

**→ DDS 的 mip 链是「部分」的 → Interchange 拒收 → 贴图没 mip → 对象找不到 → 导入失败。**
**→ 「contains no miplevels」**不是独立问题**，是下游症状。**

### 三、🎯 实测当前状态：健康

**Python 读不到 mip（`platform_data` 不可读）。
用引擎命令 `listtextures`（`memreport` 里也用它），它有一列 **`NumMips`**：**

```
512x512 (192 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/Textures/T_Boss_Mob01.T_Boss_Mob01, YES, NO, NO, 40, 10, NO
64x64 (8 KB), PF_DXT1, TEXTUREGROUP_World,
  /Game/Moxiang/tile_108_road01.tile_108_road01, NO, NO, NO, 1, 7, NO
```

| 贴图 | 尺寸 | NumMips | 完整？ |
| --- | --- | --- | --- |
| T_Boss_Mob01 | 512×512 | **10** | ✅ 512→…→1 正好 10 级 |
| tile_108_road01 | 64×64 | **7** | ✅ 64→…→1 正好 7 级 |

**→ 两张都是完整 mip 链。资产健康。**
**→ 那条警告是 11:57 失败那次留下的**历史记录**，后来走 PNG 的路子修正了。**

**顺带：`Usage Count = 40` 正好对应 Boss 的 40 个材质槽。**

### 四、🎯 DDS 的三种失败模式（错误信息都很精确）

| 模式 | 错误信息 | 怎么办 |
| --- | --- | --- |
| 格式不支持 | `DDS DXGIFormat not supported : 71 : BC1_UNORM` | 转 PNG |
| **mip 链是部分的** | `must either be a single base mip, or a full mip chain, not a partial mip chain` | 转 PNG 或补全 |
| 文件坏了 | `DDS D...` | 换源文件 |

**→ 结论：本项目 DDS 通路不可靠，统一 **DDS → PNG → UE**。**

### 五、🔴 方法论：分清历史警告和当前问题

**日志是**累积**的 —— 一次会话所有尝试都留着。
同一条警告可能在修复之前产生，修复之后仍留在文件里。**

| 判据 | 历史警告 | 当前问题 |
| --- | --- | --- |
| 时间戳 | 早于最后一次修复 | 最近操作之后 |
| 后续成功记录 | 后面有 `import completed` | 没有 |
| **当前实测状态** | **健康** | 有问题 |

**→ 唯一可靠办法：**直接测当前状态**，不要相信日志里的旧行。**
**→ 这轮就是：警告说「没有 mip」，实测说「有 10 级」。信实测。**

**→ 和案例 006 是同一课的两面：**
**日志告诉你**发生过什么**，不告诉你**现在是什么**。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-MIP.md`** | 历史警告溯源 + `listtextures` 用法 + DDS 三模式 |

### 七、七个案例的最终分类

| 案例 | 症状 | 性质 |
| --- | --- | --- |
| 001 动画 | 看不见动 | **真缺陷** |
| 002 法线 | 引擎警告 | **真缺陷** |
| 003 IBM | 模型散开 | **真缺陷** |
| 004 材质 | 101 个缺材质 | **误报 + 1 个真** |
| 005 警告 | Invalid animation skeleton | **无害** |
| 006 测试 | 13 个失败 | **引擎噪音** |
| **007 mip** | **贴图无 mip** | **历史残留，资产健康** |

**→ **七个里只有三个真缺陷、一个真误报、三个已解决/无害。****
**→ 这个比例本身是结论：日志里的「问题」大多数**不是当前问题**。**

### 八、日志信号清点完毕

**74 条告警已全部归类：**
- 31 条 = 我自己测试脚本打的
- 13 条 = 引擎自测噪音
- 8 条 = 案例 002（法线）
- 7 条 = 案例（资产路径）
- 3 条 = 未指定材质的图元
- 2 条 = MapCheck Nanite（案例 004）
- 2 条 = 近零法线（案例 002）
- 1 条 = 贴图 mip（**案例 007**）
- 1 条 = 动画骨架（案例 005）
- 其余 = MCP / 布局 / EOS 等环境提示

### 九、下一轮

**日志清点完了。现在只剩一件事：**应用已定位的修复**。**
**或者继续在别处找问题。**

**⚠️ 代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 74." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 74; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
