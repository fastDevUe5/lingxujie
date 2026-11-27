# UE5 学习 · 网络（第一块）：复制层在跑，传输层没有

> **这一块推翻了我之前的一条结论：**
> **「项目没有网络」—— 说**对了一半**，但说错了**哪一半**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

**`networking.md`（23.6 KB，20 节，**实质文章**）：**

| 章节 | 内容 |
| --- | --- |
| **Plan Early for Multiplayer** | 早规划 |
| **UE Networking Architecture** | 架构 |
| **Client-Server Gameplay Example** | 客户端-服务器示例 |
| **Fundamental Networking Concepts** | 基础概念 |
| **Network Modes** / **Server Types** | 独立 / 客户端 / 服务器；**Listen Server** vs **Dedicated Server** |
| **Replication** / **Actor Replication** | 复制机制 |
| **Debugging, Profiling, and Testing** | 调试工具 |
| **Replication Systems** | **Generic** / **Replication Graph** / **Iris** 三套系统 |
| **Networking Tips** / **Tutorials** | |

**→ 这篇文档质量高，覆盖了「三套复制系统」这种容易忽略的分层。**

---

## 二、项目配置：确实没有网络设置

**✅ 实测：`Config/*.ini` 里搜 `NetDriver` / `OnlineSubsystem` / `DedicatedServer` / `MaxNetTickRate` →
**全部零命中**。**

**→ **没有配置任何 NetDriver。****

---

## 三、🔴 更正一：`net` 命令不是「静默」，是明确报错

**之前我记的是「`net` 命令静默无输出」。**

**实测：**
```
Cmd: net.NetMode
Command not recognized: net.NetMode
```

**→ 有些 CVar **根本不存在**，引擎会明说 `Command not recognized`。
→ 「静默」和「不存在」是两种不同情况，我之前混为一谈了。**

---

## 四、🔴 更正二：**复制层是活的**

**在 game world 里跑 `net.ActorReport`，输出了真实数据（✅）：**

```
LogNet: Display: Class Count (includes inheritance)
LogNet: Display: Actor - 5
LogNet: Display: Object - 5
LogNet: Display: Info - 3
LogNet: Display: GameStateBase - 1
LogNet: Display: WorldSettings - 1
LogNet: Display: PlayerController - 1
LogNet: Display: Controller - 1
LogNet: Display: PlayerState - 1
LogNet: Display: GameplayDebuggerCategoryReplicator - 1

LogNet: Display: Total Replicated Actor Count: 5
LogNet: Display: Complete Bounding Box:
    IsValid=true, Min=(-350, -350, 0), Max=(0, 0, 100)
    Size: X=350 Y=350 Z=100
LogNet: Display: DORM_Awake - 5
```

**→ **5 个复制 actor 在运行**：PlayerController、PlayerState、GameStateBase、
GameplayDebuggerCategoryReplicator、WorldSettings。**

**→ 这是 UE 的固有行为 —— 任何 World 都有 GameMode/GameState/PlayerController 这套复制体系，
**单机也在跑**，只是没有网络传输。**

**→ 所以准确的结论是：**
> **复制层（replication）在跑；传输层（NetDriver）没有。**

**→ 「项目没有网络」这句话错在把两层混成一层。**

---

## 五、`net.SimulateConnections` 为什么没反应 —— 源码给了答案

**引擎注册了这个命令：**
```cpp
// NetConnection.cpp:6404
FAutoConsoleCommandWithWorldAndArgs AddimulatedConnectionsCmd(
    TEXT("net.SimulateConnections"),
    TEXT("Starts a Simulated Net Driver"), ...);
```

**看它的实现（`NetConnection.cpp:6311-6333`）：**
```cpp
// Search for server game net driver. Do it this way so we can cheat in PIE
UNetDriver* BestNetDriver = nullptr;
for (TObjectIterator<UNetDriver> NetDriverIt; NetDriverIt; ++NetDriverIt)
{
    if (NetDriverIt->NetDriverName == NAME_GameNetDriver && NetDriverIt->IsServer())
    {
        BestNetDriver = *NetDriverIt;
        break;
    }
}

if (!BestNetDriver)
{
    return;        // ← 静默提前返回
}
```

**→ 它需要**一个已存在的服务器 GameNetDriver**。没有就**静默 return**，不报错。**

**→ 这解释了我看到的「无输出」：不是命令坏了，是**前置条件不满足**。**

---

## 六、要做真正的网络实操，还差什么

| 条件 | 现状 |
| --- | --- |
| `r.GenerateMeshDistanceFields` 那类开关 | — |
| **一个 NetDriver** | ❌ **没有**，且 `net.SimulateConnections` 依赖它 |
| **`DefaultEngine.ini` 里的 NetDriverDefinitions** | ❌ 没有 |
| 复制层 | ✅ **有**（5 个复制 actor）|
| 观测工具 | ✅ **`net.ActorReport` 可用** |

**→ 启用传输需要往 `Config/DefaultEngine.ini` 加 NetDriverDefinitions。
那是**项目配置修改**，本轮不做（目标要求「不做开发」）。**

---

## 七、这一块学到什么

**1. 🔴 「没有网络」必须拆成两层说：**
**复制层（replication）**和**传输层（NetDriver）**是独立的。
**单机也在复制，只是不走网络。**

**2. 🔴 `Command not recognized` ≠ 静默。**
命令不存在会明说；命令存在但前置条件不满足才静默。

**3. 🎯 `net.ActorReport` 是最有用的网络观测命令** —— 不依赖 NetDriver，直接给出：
- 复制 actor 总数
- 按类分组
- 包围盒
- 沉睡状态（DORM_Awake）

**4. 🔴 源码能解释「为什么没反应」。**
`if (!BestNetDriver) return;` —— 一行就解释了全部。

**5. 同一次探针里跑多个命令，要看清哪个输出了哪个没输出。**
`net.ActorReport` 输出了一大堆，`net.SimulateConnections` 一个字节没有。

---

## 八、更正

| 之前 | 现在 |
| --- | --- |
| 「项目没有网络，`net` 命令静默」 | ❌ **复制层在跑（5 个复制 actor）；`net` 命令不存在时会报错** |
| 「网络这块零实测」 | ✅ **`net.ActorReport` 实测有数据** |

---

## 九、下一块

**转「打包与优化」**（目标里的最后一项）。

**⚠️ 编辑器状态：主关卡 116 actor、视口复位、练习关卡 10 actor。**
