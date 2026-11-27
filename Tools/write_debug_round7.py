"""Append the seventh debugging round.

    python Tools/write_debug_round7.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 64. 调试系列第 7 轮：**网络 — 大部分只能读源码，我不假装验证过**（2026-11-26 49:00）

### 一、先说诚实的边界

**灵虚界是单人项目：`.uproject` 里没有网络插件，`Config` 里没有 NetDriver 段。**

**所以本篇大部分结论是**读源码**得出的，**没有运行验证**。**

**文档里每个结论都标了 `✅ 实测` 或 `📖 源码`。这是本系列第一篇大部分未实测的。**
**我不打算把它写成看起来都验证过了的样子。**

### 二、✅ 实测部分：本项目网络是静默的

| 检查 | 结果 |
| --- | --- |
| `net`（无参数）| **无任何输出** |
| `unreal.World` 的 `get_net_mode` / `get_net_driver` | **都不存在** |
| `unreal.World` 上含 `net` 的属性 | **一个都没有** |

**存在的 CVar：**
```
net.AllowPIESeamlessTravel        = "false"
net.UseAdaptiveNetUpdateFrequency = "0"
net.Iris.UseIrisReplication       = "0"
net.DebugDrawCullDistance         = "0"
```

**不存在的（只有 `Cmd:` 没有 `= value`）：**
```
net.PackageMap.LocateNetDriver / net.RepDriver / net.MaxRepArraySize / net.DebugDrawRelevant
```

### 三、🎯 一个新学到的通用判据

> **敲一个 CVar 名字：**
> **有 `= value` → 存在**
> **只有 `Cmd: xxx` → 不存在**
>
> **不用猜，回显自己会说。**

### 四、📖 丢包模拟的完整参数与**互斥关系**

**`FPacketSimulationSettings::ParseSettings` 接受的 token：**
`PktEmulationProfile= / PktLoss= / PktLossMinSize= / PktLossMaxSize= /
PktOrder= / PktLag= / PktDup= / PktLagVariance= / PktLagMin=`

**🔴 互斥关系（源码注释原文）：**

| 约束 | 后果 |
| --- | --- |
| `PktOrder` **优先于** `PktDup` 和 `PktLag` | 设了 PktOrder，另两个**静默失效** |
| `PktDup` **不能**和 `PktOrder`/`PktLag` 同用 | 同上 |
| `PktLagVariance` 只在 `PktLag` 开启时有效 | 单独设没用 |
| `PktLagMin/Max` 在 `PktLag` 设置后**被忽略** | 被覆盖 |
| `PktJitter` **会造成接收端丢包** | 不是单纯加抖动 |

**→ 这是本篇最实用的一条：以为设了两个参数，实际只有一个生效，测出来的数据是假的。**

### 五、📖 模拟设置会**跨 PIE 重启残留**

**源码 `NetEmulationHelper.cpp` 16-47：**
```cpp
/** Global that stores the network emulation values outside the NetDriver lifetime */
static TOptional<FPacketSimulationSettings> PersistentPacketSimulationSettings;
// 应用到该世界里所有活跃的 NetDriver
```

**→ PIE 里设的 `PktLag=100`，PIE 重启后**仍然有效**。**
**→ 排查「为什么 PIE 有延迟」时先检查这个 —— 和无头日志级别残留是同一类问题。**
**→ 要清零得显式 `net PktLag=0`，不要以为重启就清了。**

### 六、📖 三个编译门

| 宏 | 定义 | 影响 |
| --- | --- | --- |
| `DO_ENABLE_NET_TEST` | `!(UE_BUILD_SHIPPING)` | 丢包模拟在 Shipping 里没有 |
| `Exec_Dev` 包在 `!UE_BUILD_SHIPPING` | — | **`net` 子命令在 Shipping 里没有** |
| `DO_BLUEPRINT_GUARD` | 独立宏 | 蓝图循环守卫 |

**→ 「打包后网络问题查不了」是编译期就删掉的，不是错觉。**

### 七、📖 `net` 子命令全表

`SOCKETS / PACKAGEMAP / NETFLOOD / NETDEBUGTEXT / NETDISCONNECT /
DUMPSERVERRPC / DUMPDORMANCY / PKTLOSSBURST= / FLUSHALLNETDORMANCY /
DUMPSUBOBJECTS / DUMPREPLAYOUTFLAGS`

**排查最常用的三个：`net PACKAGEMAP`（对象映射）、`net DUMPSERVERRPC`（RPC 统计）、
`net DUMPDORMANCY`（休眠状态）。**

### 八、解锁点

**一旦 PIE 设成 `Play As Listen Server` + 2 客户端，`net` 就**有接收者**了，
本篇所有「未验证」的内容就能逐条变实测。**

**这一条写进了文档第八节，作为下次起步的第一步。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-NET.md`** | 诚实标注 ✅/📖 的网络调试文档 |
| `Tools/practice_net_commands.py` | 探本项目网络状况 + CVar 存在性 |

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **资产与加载问题**（最后一个域）—— 引用链、Size Map、Cook 错误、加载失败 |
| 2 | 之后：回头做**实战演练**——用前七篇的方法定位项目里的真实问题 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 64." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 64; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
