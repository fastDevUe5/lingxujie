"""Append the second debugging round.

    python Tools/write_debug_round2.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 59. 调试系列第 2 轮：**崩溃 — 用本项目真实崩溃还原全过程**（2026-11-26 44:00）

### 一、素材

**`Saved/Crashes/UECC-Windows-564DEF134CE32AB8E530AD97A88E55B0_0000/`**
**四样东西：`CrashContext.runtime-xml`(213KB) / `LingXuJie.log`(4.5MB) / `UEMinidump.dmp`(2.7MB) / `CrashReportClient.ini`**

### 二、🔴 核心发现：`PCallStack` 才是真调用栈

**112 个字段，按长度排序才看得出真相：**

| 字段 | 长度 | 内容 |
| --- | --- | --- |
| `Modules` | 103,298 | 模块路径 + 基址 |
| **`PCallStack`** | **3,533** | **模块名 + 基址 + 偏移** ← 真栈 |
| `CallStack` | 1,480 | **只有模块名** |
| `ErrorMessage` | 82 | 一行异常描述 |
| **`UserActivityHint`** | 63 | **崩溃时人在干什么** |

**`CallStack` 只有模块名，因为基类实现返回空串：**
```cpp
// GenericPlatformCrashContext.cpp:1208
const TCHAR* FGenericCrashContext::GetCallstackProperty() const { return TEXT(""); }
```

### 三、崩溃完整还原

**证据链三件：**

**① 日志最后一行：**
```
[12:52:06] Cmd: OBJ SAVEPACKAGE PACKAGE="/Game/Maps/LingXuJie"
```

**② `ErrorMessage`：**
```
Unhandled Exception: EXCEPTION_ACCESS_VIOLATION reading address 0x00007465736c6f18
IsAssert=false  IsEnsure=false
```

**③ `PCallStack`（内→外）：**
```
python311 + d8b06                        ← 炸在这里
python311 + cb2a / c795 / cb452
UnrealEditor-PythonScriptPlugin + dd873   ← 但这里让它炸的
UnrealEditor-CoreUObject + 236cf1         ← UObject 属性访问
UnrealEditor-UnrealEd + 79f52b
UnrealEditor-LevelEditor + 1a225f
```

**④ `UserActivityHint`：**
```
Layout="LevelEditorViewport" Label="视口 1" Content=SAssetEditorV...
```

**结论：**
```
Python 脚本 → save_current_level() → OBJ SAVEPACKAGE /Game/Maps/LingXuJie
            → UObject 属性访问 → 访问违例
```

### 四、新学到的一招：把故障地址按字节解

**`0x00007465736c6f18` 按字节读：**
```
18 6f 6c 73 65 74  →  "\x18olset"
```
**是可读 ASCII。**

**→ 读指针却读到文本 = 把**非 UObject 的内存**当对象用。**

**这个线索比栈更直接 —— 它告诉你**故障性质**，而栈只告诉你**位置**。**

### 五、可执行结论

> **本项目不要从 Python 调 `save_current_level()`。**
> **它崩溃过一次。而且关卡本来就是 `Tools/build_level.py` 幂等重建的，不需要 Python 保存。**

**这是第一次因为**读崩溃上下文**得出可执行结论。**

### 六、🔴 本机无法解析 minidump（环境事实）

| 工具 | 状态 |
| --- | --- |
| `cdb.exe` / `windbg.exe` | **未安装** |
| Visual Studio 调试器 | **未找到** |
| **`UnrealEditor.pdb`** | **不存在**（发行版引擎不带）|

**`Symbols` 字段确认：`**UE5*Release-5.8-CL-58902052-Win64-Development`**

**→ 即使装 cdb，也只能得到与 `PCallStack` 相同的模块+偏移，没有符号。**
**→ 「读崩溃 XML」是本机**唯一可行**的崩溃分析路径。**

### 七、排查清单（已写进文档）

**拿到崩溃目录按这个顺序读：**
1. `ErrorMessage` —— 异常类型 + 地址
2. `IsAssert`/`IsEnsure` —— 断言还是访问违例
3. **故障地址按字节解 ASCII**
4. `PCallStack` —— 模块链
5. `UserActivityHint` —— 当时在干什么
6. 同目录 `*.log` 最后 30 行
7. `SecondsSinceStart` —— 长会话累积？

### 八、🔴 这一轮我又犯了同类错误

**先读到：**
```cpp
bGenerateRuntimeCallstack = ForceLogCallstacks || IsInternalBuild() || ...
```
**写下结论：「发行版引擎 → 不会生成运行期栈」。**

**往下两行才发现：**
```cpp
#if UE_LOG_CRASH_CALLSTACK
    true;                    // ← 宏为 1 时恒为 true
#else
    ForceLogCallstacks || IsInternalBuild() || ...
#endif
```
**而 `UE_LOG_CRASH_CALLSTACK` 默认是 1。**

**→ 结论**完全错了**。运行期栈一定会生成。**

**错因：只看 `#else` 分支，没注意它在条件编译里。**

**这已是本系列第 2 次同类错误（第 1 篇：把「运行期」当「编译期」）。
共同点：**看到一段像答案的代码就下结论，没确认它所在的分支是否生效。**"**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CRASH.md`** | 崩溃分析全流程（含源码依据 + 真实案例）|
| `Tools/read_crash_context.py` | 读崩溃XML的关键字段 |
| `Tools/dump_crash_fields.py` | 112 字段按长度排序（找真相藏哪）|

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **性能剖析** —— `stat` 命令族、`stat unit`/`game`/`render` 的含义与读法 |
| 2 | Unreal Insights 的采集与打开 |
| 3 | 帧预算与瓶颈判定（Game vs Draw vs GPU）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 59." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 59; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
