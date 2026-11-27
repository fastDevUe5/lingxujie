# UE5 调试 · 三：崩溃、调用栈与崩溃上下文

> **本篇基于本项目**一次真实崩溃**（2026-11-26 19:52:08），
> 逐个字段拆解 `Saved/Crashes/UECC-*/` 里的四样东西。**
>
> **结论：崩溃是 Python 调 `save_current_level()` 触发的，栈里能指到模块与偏移。**
>
> **日期：2026-11-26 · UE 5.8.4（Release-5.8 发行版引擎）**

---

## 一、崩溃目录里有什么

**每次崩溃产生一个 `Saved/Crashes/UECC-<Platform>-<GUID>_0000/` 目录：**

| 文件 | 大小（本次）| 内容 |
| --- | --- | --- |
| **`CrashContext.runtime-xml`** | 213 KB | **崩溃上下文，112 个字段**（最有价值）|
| `LingXuJie.log` | 4.5 MB | 崩溃时的日志副本 |
| `UEMinidump.dmp` | 2.7 MB | 内存快照（**本机无法解析**，见第四节）|
| `CrashReportClient.ini` | 0.2 KB | 报告客户端配置 |

---

## 二、`CrashContext.runtime-xml` 的 112 个字段：哪些真有用

**按内容长度排序，真相就藏在长字段里：**

| 字段 | 长度 | 内容 | 诊断价值 |
| --- | --- | --- | --- |
| `Modules` | 103,298 | 所有加载模块的路径与基址 | 中（找哪个 DLL 参与）|
| **`PCallStack`** | **3,533** | **模块名 + 基址 + 偏移** | **🔴 最高** |
| `CallStack` | 1,480 | **只有模块名**，无偏移 | 低（只够看大致分层）|
| `ErrorMessage` | 82 | 一行异常描述 | 高（异常类型 + 地址）|
| `CommandLine` | 81 | 启动参数 | **高（能看出跑了什么）** |
| **`UserActivityHint`** | 63 | **崩溃时人在干什么** | **🔴 高（极容易忽略）** |
| `Symbols` | 47 | 符号版本串 | 中（能不能解析栈）|
| `SecondsSinceStart` | — | 会话跑了多久 | 中（长会话 = 累积型）|

**⚠️ 本次崩溃的关键三个字段：**
```
ErrorMessage      Unhandled Exception: EXCEPTION_ACCESS_VIOLATION reading address 0x00007465736c6f18
UserActivityHint  Layout="LevelEditorViewport" Label="视口 1" Content=SAssetEditorV...
CommandLine       LingXuJie.uproject -ModelContextProtocolStartServer
```

### 2.1 🔴 `PCallStack` 才是真调用栈

**`CallStack` 字段只有模块名（`python311` / `UnrealEditor_CoreUObject` …），
因为基类实现返回空串：**

```cpp
// GenericPlatformCrashContext.cpp:1208
const TCHAR* FGenericCrashContext::GetCallstackProperty() const { return TEXT(""); }
```
**注释：**「Allow platforms to override callstack property, on some platforms the callstack is not captured」

**而 `PCallStack`（Portable CallStack）带**模块基址 + 偏移**：**
```
python311                              0x00007fff86680000 + d8b06
UnrealEditor-PythonScriptPlugin        0x0000023725b90000 + dd873
UnrealEditor-CoreUObject               0x00007fffa7d20000 + 236cf1
UnrealEditor-UnrealEd                  0x00007fff9db20000 + 79f52b
UnrealEditor-LevelEditor               0x00007fff907d0000 + 1a225f
```

**→ 有偏移就能算绝对地址（`基址 + 偏移`），配合 PDB 能出符号。
没有 PDB 也能按模块分层定位。**

### 2.2 `UserActivityHint` 是最容易被忽略的字段

**本次值：**
```
Layout="LevelEditorViewport" Label="视口 1" Content=SAssetEditorV...
```

**→ 崩溃那一刻，编辑器焦点在**关卡编辑器视口**，而且有个**资产编辑器**正打开着。**

**这条信息能直接排除「是不是后台线程崩的」「是不是 PIE 崩的」。**

---

## 三、本次崩溃的完整还原（有据可查）

### 3.1 现场证据链

**① 日志最后一行：**
```
[12:52:06] Cmd: OBJ SAVEPACKAGE PACKAGE="/Game/Maps/LingXuJie" FILE="..."
```
**→ 崩溃发生在**保存地图**时。**

**② 崩溃前几行：**
```
[12:52:06] LogPython: [LingXuJie] STATIC: import produced 1 assets
[12:52:06] LoadAsset failed: '/Game/Moxiang/Static/SM_Boss001.SM_Boss001' could not be found
[12:52:06] Message dialog: 「无法从版本控制检出！」 /Game/Maps/LingXuJie
[12:52:06] OBJ SavePackage: Generating thumbnails for [/Game/Maps/LingXuJie]
```

**③ 调用栈（`PCallStack`，从内到外）：**
```
python311 + d8b06                        ← Python 解释器
python311 + cb2a / c795 / cb452
UnrealEditor-PythonScriptPlugin + dd873   ← Python → UE 桥
UnrealEditor-PythonScriptPlugin + c0e7e
UnrealEditor-CoreUObject + 236cf1         ← UObject 属性访问
UnrealEditor-CoreUObject + 208b40 / 28c2d4 / 237d3b
UnrealEditor-UnrealEd + 79f52b / 7788bd / 7a7509 / 7a7e25 / 7eaa28 / 7e9abd
UnrealEditor-Core + 55e106
UnrealEditor-Engine + 299b26f
UnrealEditor-UnrealEd + 12a50ad / bfe4b2 / bfab40
UnrealEditor-LevelEditor + 1a225f / 1a8573   ← 关卡编辑器
```

**④ 异常：**
```
EXCEPTION_ACCESS_VIOLATION reading address 0x00007465736c6f18
IsAssert=false  IsEnsure=false
```

### 3.2 结论

**触发路径：**
```
Python 脚本 → save_current_level() → OBJ SAVEPACKAGE /Game/Maps/LingXuJie
            → UObject 属性访问 → 访问违例
```

**那个地址 `0x00007465736c6f18` 按字节读是**
```
18 6f 6c 73 65 74  →  "\x18olset"
```
**是可读 ASCII。**
**读指针却读到文本，典型特征是：把一个**非 UObject 的内存**当对象用，在属性访问时解引用。**

**⚠️ 这是**推断**，不是证明 —— 没有 PDB 无法看到具体是哪个属性。**

### 3.3 可执行结论

> **本项目不要从 Python 调 `save_current_level()`。**
> **它崩溃过一次，而且关卡本来就是 `Tools/build_level.py` 幂等重建的，不需要 Python 保存。**

**这是我第一次因为**读崩溃上下文**得出可执行结论。**

---

## 四、🔴 本机无法解析 minidump —— 这是硬限制

**查过：**

| 工具 | 状态 |
| --- | --- |
| `cdb.exe`（Windows SDK）| **未安装** |
| `windbg.exe` | **未安装** |
| Visual Studio 调试器 | **未找到** |
| **`UnrealEditor.pdb`** | **不存在**（发行版引擎不带符号）|

**`Symbols` 字段也说得很清楚：**
```
**UE5*Release-5.8-CL-58902052-Win64-Development
```

**→ 即使装了 cdb，也只能得到**模块 + 偏移**，和 `PCallStack` 已有的信息一样。**

**→ 想拿到符号级调用栈，只有两条路：**
1. **从源码编译引擎**（几小时，本项目不值得）
2. **用源码构建的引擎**（当前是 Launcher 发行版，没有）

**⚠️ 所以「读崩溃上下文 XML」是本机**唯一可行**的崩溃分析路径。这不算缺陷，是环境事实。**

---

## 五、崩溃排查清单

### 5.1 拿到一个崩溃目录，按这个顺序读

| 步 | 看什么 | 得到什么 |
| --- | --- | --- |
| 1 | `ErrorMessage` | 异常类型 + 故障地址 |
| 2 | `IsAssert` / `IsEnsure` | **是访问违例还是断言**（决定排查方向）|
| 3 | 故障地址的**字节** | 可读 ASCII → 可能是字符串被当指针 |
| 4 | `PCallStack` | **从内到外的模块链** |
| 5 | `UserActivityHint` | 崩溃时人在做什么 |
| 6 | 同目录 `*.log` **最后 30 行** | 崩溃前最后一个动作 |
| 7 | `SecondsSinceStart` | 是否长会话累积 |
| 8 | `CommandLine` | 启动参数（`-unattended` 有没有）|

**⚠️ 第 3 步是我这次才意识到有用的一招：**
**`EXCEPTION_ACCESS_VIOLATION reading address 0x...` 里的地址，按字节解成 ASCII，
如果可读，说明代码把**数据**当**指针**用了 —— 这个线索比栈还直接。**

### 5.2 「崩溃发生在哪个模块」怎么判断

**`PCallStack` 是**从内到外**排的（最内层在最上）。**
**本次最上面 4 帧是 `python311`，说明崩溃点在 Python 解释器内部，
但**触发**它的是下面第 5-6 帧的 `PythonScriptPlugin`。**

**规则：**
> **栈顶是「在哪炸的」，往下一两层是「谁让它炸的」。**
> **本次：
> 炸在 `python311`，
> 但真正的问题在 `PythonScriptPlugin` → `CoreUObject` 的属性访问。**

### 5.3 断言崩溃 vs 访问违例

| 字段 | 断言 | 访问违例 |
| --- | --- | --- |
| `IsAssert` | **true** | false |
| `IsEnsure` | 可能 true | false |
| `ErrorMessage` | 含断言表达式文本 | `EXCEPTION_ACCESS_VIOLATION` |
| 排查方向 | 看断言表达式 + 谁传了坏值 | 看指针来源 + 生命周期 |

**本次是访问违例 → 排查方向是「指针从哪来、对象还在不在」，不是「谁传了坏参数」。**

---

## 六、还没做的

| 事项 | 为什么 | 风险 |
| --- | --- | --- |
| **复现这次崩溃** | 能在受控条件下确认触发条件 | **会让编辑器崩溃，必须先问人** |
| 给项目加 `USE_CHECKS_IN_SHIPPING` | 打包版能有断言 | 需改 Target.cs |
| 装 Windows SDK 拿 cdb | 能读 `.dmp` 的原始栈 | **但没 PDB，价值有限** |
| 找 `ForceLogCallstacks` 的实际输出位置 | 源码里它写进 `GErrorHist` | 需再查 `GErrorHist` 落盘路径 |

**⚠️ 第一条**我故意没做** —— 崩溃编辑器会打断你，而且按规则要先问。**

---

## 七、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| `CallStack` 由 `GetCallstackProperty()` 写，基类返回空 | `GenericPlatformCrashContext.cpp` | 1139-1141, 1208-1211 |
| `PCallStack` 是独立的「可移植调用栈」 | 同上 | 1145-1147, 325-327 |
| 运行期栈 `bGenerateRuntimeCallstack` 默认 **true** | `WindowsPlatformCrashContext.cpp` | 1678-1684 |
| `UE_LOG_CRASH_CALLSTACK` 默认 1 | 同上 | 50-51 |
| 运行期栈追加到 `GErrorHist`（用于消息框）| 同上 | 1704-1708 |
| 发行版引擎不带 PDB | 文件系统核实 | — |

### 7.1 🔴 我这一轮犯的错（必须记）

**我先读到：**
```cpp
bGenerateRuntimeCallstack = ForceLogCallstacks || IsInternalBuild() || ...
```
**然后写下结论：「本项目是发行版 → `IsInternalBuild()` 为假 → 运行期栈不会生成」。**

**再往下看两行才发现：**
```cpp
#if UE_LOG_CRASH_CALLSTACK
    true;                      // ← 宏为 1 时恒为 true
#else
    ForceLogCallstacks || IsInternalBuild() || ...
#endif
```
**而 `UE_LOG_CRASH_CALLSTACK` 默认是 1。**

**→ 我的结论**完全错了**。运行期栈**一定会生成**。**

**错因：只看了 `#else` 分支的代码，没注意它在条件编译里。**

**这已经是本系列第 2 次同类错误（第 1 篇是把「运行期」当「编译期」）。
共同点：**看到一段像答案的代码就下结论，没有确认它所在的分支是否生效。**"**

---

**下一篇：`Docs/UE5-DEBUG-PERF.md` —— `stat` 命令族与 Unreal Insights。**
