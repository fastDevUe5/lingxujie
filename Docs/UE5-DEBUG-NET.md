# UE5 调试 · 八：网络调试

> **⚠️ 本篇有一条必须放在最前面的诚实说明：**
>
> **灵虚界是**单人项目**，没有任何网络配置、没有 Online 插件。
> 本篇的机制部分全部来自源码核实，但**真实复制行为无法在本项目上实测**。**
>
> **标了「✅ 实测」的是真跑过的；标了「📖 源码」的是只读了源码、没跑过。
> 两者的可信度不同，不要混着用。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、本项目的实际网络状况（✅ 实测）

| 检查 | 结果 |
| --- | --- |
| `LingXuJie.uproject` 里的网络/Online 插件 | **没有** |
| `Config/*.ini` 里的 `NetDriver` / `Replication` 段 | **没有** |
| 控制台 `net`（无参数）| **无任何输出** |
| `unreal.World` 的 `get_net_mode` / `net_mode` / `get_net_driver` | **全都不存在**（AttributeError）|
| `unreal.World` 上任何含 `net` 的属性 | **一个都没有** |

**→ 编辑器世界是 Standalone，**没有 NetDriver 实例**。
**→ `net` 命令没有接收者，所以静默无输出。**

### 1.1 存在的 CVar（✅ 实测）

```
net.AllowPIESeamlessTravel        = "false"    LastSetBy: Constructor
net.UseAdaptiveNetUpdateFrequency = "0"        LastSetBy: Constructor
net.Iris.UseIrisReplication       = "0"        LastSetBy: Constructor
net.DebugDrawCullDistance         = "0"        LastSetBy: Constructor
```

### 1.2 不存在（或未注册）的 CVar（✅ 实测）

```
net.PackageMap.LocateNetDriver
net.RepDriver
net.MaxRepArraySize
net.DebugDrawRelevant
```
**→ 控制台回显只有 `Cmd: xxx`，没有 `= value`，说明这个 CVar 不存在。**

**⚠️ 这是个通用判据：敲一个 CVar 名字，**有 `= value` 就是存在，只有 `Cmd:` 就是不存在**。**

---

## 二、丢包模拟：完整参数（📖 源码）

**源码：`Runtime/Engine/Private/Net/NetEmulationHelper.cpp` 第 534 行起**

**`FPacketSimulationSettings::ParseSettings` 接受这些 token：**
```
PktEmulationProfile=
PktLoss=          PktLossMinSize=   PktLossMaxSize=
PktOrder=         PktLag=           PktLagVariance=   PktLagMin=
PktDup=
```

**控制台语法：**
```
net PktLag=100
net PktLoss=5 PktLag=80 PktLagVariance=20
```

### 2.1 字段含义（源码 `NetDriver.h` 第 458 行起）

| 字段 | 单位 | 说明 |
| --- | --- | --- |
| `PktLoss` | **%**（0-100）| 丢包率 |
| `PktLossMinSize` / `PktLossMaxSize` | 字节 | 只丢这个尺寸范围的包 |
| `PktOrder` | bool | **随机乱序** |
| `PktDup` | **%** | 重复包率 |
| `PktLag` | 毫秒 | 出向延迟 |
| `PktLagVariance` | 毫秒 | 延迟抖动（需 `PktLag` 开启）|
| `PktLagMin` / `PktLagMax` | 毫秒 | 延迟区间 |
| `PktIncomingLagMin` / `Max` | 毫秒 | **入向**延迟 |
| `PktIncomingLoss` | % | **入向**丢包 |
| `PktJitter` | 毫秒 | 延迟在 `[PktLagMin, PktLagMin+PktJitter]` 波动 |

### 2.2 🔴 互斥关系 —— 不看清就会测出假结果

**源码注释里明确写着的：**

| 约束 | 原文 |
| --- | --- |
| `PktOrder` **优先于** `PktDup` 和 `PktLag` | "Takes precedence over PktDup and PktLag." |
| `PktDup` **不能**和 `PktOrder` / `PktLag` 同用 | "Cannot be used with PktOrder or PktLag." |
| `PktLagVariance` 只在 `PktLag` 开启时有效 | "Can only be used when PktLag is enabled." |
| `PktLagMin/Max` 在 `PktLag` 设置后**被忽略** | "Ignored if PktLag value is set" |
| `PktJitter` **会造成接收端丢包** | "this will cause packet loss on the receiving end" |

**→ 举例：**
```
net PktLag=100 PktDup=10          ← PktDup 无效（和 PktLag 冲突）
net PktOrder=1 PktLag=100         ← PktLag 无效（PktOrder 优先）
net PktLagMin=50 PktLagMax=150    ← 会被 PktLag 覆盖
```

**⚠️ 这是本篇最实用的一条：以为设了两个参数、实际只有一个生效。**

---

## 三、模拟的持久化机制（📖 源码）

**源码 `NetEmulationHelper.cpp` 第 16-27 行：**
```cpp
/** Global that stores the network emulation values outside the NetDriver lifetime */
static TOptional<FPacketSimulationSettings> PersistentPacketSimulationSettings;

void ApplySimulationSettingsOnNetDrivers(UWorld* World, const FPacketSimulationSettings& Settings) {
    // Execute on all active NetDrivers
    FWorldContext& Context = GEngine->GetWorldContextFromWorldChecked(World);
    for (const FNamedNetDriver& ActiveNetDriver : Context.ActiveNetDrivers) {
        if (ActiveNetDriver.NetDriver) {
            ActiveNetDriver.NetDriver->SetPacketSimulationSettings(Settings);
        }
    }
}
```

**→ 设置存在**全局**，跨 NetDriver 生命周期保留。
**→ 应用到**该世界里所有活跃的 NetDriver**。**

**→ 意义：PIE 里设的模拟，在 PIE 重启后**仍然有效**。**
**→ 排查「为什么 PIE 有延迟」时，先检查模拟有没有残留。**这和无头日志级别残留是同一类问题。**

### 3.1 预配置档

**控制台：**
```
NetEmulation.PktEmulationProfile <名字>
```

**源码会拼成 `PktEmulationProfile=<名字>` 然后去 `Engine.ini` 找对应的段。
找不到时的原文：**
```
"EmulationProfile: %s was not found in Engine.ini"
```

**⚠️ 默认 `BaseEngine.ini` 里**没有**预配置档（✅ 实测搜过），所以这个命令在本机
除非自己加段，否则一定报「not found」。**

---

## 四、`net` 命令全部分支（📖 源码）

**源码 `Runtime/Engine/Private/NetDriver.cpp` 第 4282 行，`UNetDriver::Exec_Dev`：**
```cpp
bool UNetDriver::Exec_Dev(UWorld* InWorld, const TCHAR* Cmd, FOutputDevice& Ar) {
#if !UE_BUILD_SHIPPING
```

| 子命令 | 作用 |
| --- | --- |
| `net SOCKETS` | 转储当前 socket |
| **`net PACKAGEMAP`** | **转储包映射 —— 排查「对象在客户端对不上号」** |
| `net NETFLOOD` | 洪泛测试 |
| `net NETDEBUGTEXT <文本>` | 设置调试文本 |
| `net NETDISCONNECT` | 强制断开 |
| `net DUMPSERVERRPC` | **转储服务器 RPC 统计** |
| **`net DUMPDORMANCY`** | **转储休眠状态** |
| `net PKTLOSSBURST=<毫秒>` | 丢包突发 |
| `net FLUSHALLNETDORMANCY` | 强制唤醒所有休眠 actor |
| `net DUMPSUBOBJECTS` | 转储子对象 |
| `net DUMPREPLAYOUTFLAGS` | 转储复制输出标志 |

**🔴 整个 `Exec_Dev` 包在 `#if !UE_BUILD_SHIPPING` 里。**

**→ 打包版里 `net` 命令**完全不存在**。**

---

## 五、编译开关：三个不同的门

| 宏 | 定义 | 影响 |
| --- | --- | --- |
| `DO_ENABLE_NET_TEST` | `!(UE_BUILD_SHIPPING)`（`NetDriver.h` 450 行）| **丢包模拟**在 Shipping 里没有 |
| `!UE_BUILD_SHIPPING`（包裹 `Exec_Dev`）| — | **`net` 子命令**在 Shipping 里没有 |
| `DO_BLUEPRINT_GUARD` | 独立宏（见 `UE5-DEBUG-SCRIPT.md`）| 蓝图循环守卫 |

**→ 结论：网络调试手段在**编辑器/开发版里齐全，打包版里几乎没有**。
**→ 「打包后网络问题没法查」不是错觉，是编译期就删掉了。**

---

## 六、排查清单（📖 储备，本项目暂时用不上）

### 6.1 「客户端看到的属性值不对」

| 步 | 做法 |
| --- | --- |
| 1 | `net PACKAGEMAP` 看对象映射对不对 |
| 2 | 检查 `UPROPERTY(Replicated)` 有没有标 |
| 3 | 检查 `GetLifetimeReplicatedProps` 有没有注册 |
| 4 | 检查 `bReplicates` 在 actor 上有没有开 |
| 5 | 检查 owning connection（`Owner` 不对就收不到）|

### 6.2 「RPC 没触发」

| 步 | 做法 |
| --- | --- |
| 1 | `net DUMPSERVERRPC` 看统计 |
| 2 | 检查 `UFUNCTION(Server/Client/NetMulticast)` 修饰符 |
| 3 | 检查 `WithValidation` 有没有返回 true |
| 4 | **检查 actor 的 `Role` / `RemoteRole`** —— 最常见的根因 |

### 6.3 「怎么模拟差网络」

```
net PktLag=150 PktLagVariance=50 PktLoss=3
```

**然后：**
- 检查 PIE 重启后设置是否**残留**（会）
- 用 `net PktLag=0 PktLoss=0` **显式清零**，不要以为重启就清了

---

## 七、🔴 本篇的诚实边界

**我没能验证的（因为本项目没有网络）：**

| 事项 | 为什么没验证 |
| --- | --- |
| `net PktLag=100` 真的产生延迟 | 没有 NetDriver 接收 |
| `net PACKAGEMAP` 的输出格式 | 同上 |
| 模拟设置在 PIE 重启后真的残留 | 同上 |
| RPC / 属性复制的实际行为 | 项目未启用 |

**📖 标了源码依据的结论可信（代码就摆在那），但**没有经过运行验证**。
**按本系列的规矩，这些必须留在「未验证」状态。**

**⚠️ 这将是本系列第一篇**大部分内容未实测**的文档。
**我不打算把它写成看起来都验证过了的样子。**

---

## 八、如果真要起步做联机

**按这个顺序，每一步都能验证：**

| 序 | 动作 | 怎么验证 |
| --- | --- | --- |
| 1 | 在 `.uproject` 加 Session 相关插件 | 编辑器能起 |
| 2 | 加 `GameMode` 的 `bUseSeamlessTravel` 等基础配置 | 日志里 NetDriver 起来了 |
| 3 | PIE 设成 `Play As Listen Server` + 2 客户端 | `net` 命令**开始有输出**了 |
| 4 | 用一个 replicated 的 float 试通 | 两端值同步 |
| 5 | 再上 `net PktLag` 测 | 延迟可见 |
| 6 | 才轮到 Iris / Replication Graph | — |

**第 3 步是本篇所有「未验证」内容的解锁点：一旦有 NetDriver，`net` 就有接收者了。**

---

## 九、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| `DO_ENABLE_NET_TEST = !(UE_BUILD_SHIPPING)` | `NetDriver.h` | 450 |
| `FPacketSimulationSettings` 字段与互斥注释 | 同上 | 458-560 |
| `ParseSettings` 接受的 token | `NetEmulationHelper.cpp` | 534 起 |
| 模拟设置存全局、跨 NetDriver | 同上 | 16-47 |
| `NetEmulation.PktEmulationProfile` 命令 | 同上 | 47-75 |
| `net` 子命令全表 | `NetDriver.cpp` | 4282 起 |
| `Exec_Dev` 包在 `!UE_BUILD_SHIPPING` | 同上 | 4284 |
