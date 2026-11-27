"""Append the fourth debugging round.

    python Tools/write_debug_round4.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 61. 调试系列第 4 轮：**内存 — 环数不等于泄漏**（2026-11-26 46:00）

### 一、`memreport` 的机制：延迟到帧末，先强制 GC

**源码 `UnrealEngine.cpp` 8120-8126：**
```cpp
// This will defer the report to the end of the frame so we can force a GC and get a real report
// with no gcable objects
GEngine->DeferredCommands.Add(FString::Printf(TEXT("MemReportDeferred %s"), Cmd ));
```

**→ 敲 `memreport` 不会立刻输出，它在帧末跑，**报告写进文件**。**

**落盘路径（实测）：**
```
Saved/Profiling/MemReports/LingXuJie-WindowsEditor-11.26-20.54.27/
    Pid4544_LingXuJie-WindowsEditor-26-20.54.27.memreport   ← 468.5 KB
```

**默认跑 **34 条命令**（`BaseEngine.ini` 2371 起），可用 `[MemReport<Profile>Commands]` 自定义。**

### 二、🔴 `obj cycles` 找到 29 个环内对象 —— 但**一个都不是项目的**

**实测输出：**
```
66998 total objects, 126353 total edges.
Non-permanent: 12333 objects, 8616 edges, 14 strongly connected components,
               29 objects are included in cycles.
```

**逐个看环的成员，只有 4 种类型：**
```
Level / ParticleEventManager / World / WorldSettings
```
**全是 `/Engine/Transient.World_N`，`/Game/` 出现 **0 次**。**

**环结构（引擎固有）：**
```
ParticleEventManager → WorldSettings      [Actor:Owner]
WorldSettings → ParticleEventManager      [Actor:Children]

Level → World                             [Level:OwningWorld]
World → Level                             [World:PersistentLevel / LevelCollection:*]
```

**→ World 不是靠 GC 回收的，是靠 `UWorld::Destroy()` 显式销毁。
这些环**设计如此**，不是泄漏。**

### 三、本条是本轮最重要的教训

> **`obj cycles` 报「29 个对象在环里」不等于「29 个泄漏」。必须看**环里是谁**。**
>
> **判断方法：搜输出里的 `/Game/`。没有 = 项目零泄漏。**

**这和本系列反复出现的「数字是真的但量错了东西」是同一类。**

### 四、本项目实测内存

```
Time Since Boot: 3733.60 Seconds          （62 分钟）
Process Physical Memory: 4554.05 MB used, 4648.82 MB peak
Process Virtual Memory:  8406.94 MB used
AssetRegistry memory usage = 140.97 MB
Nametable memory usage = 17.76 MB
```

**按类的资源占用：**

| 类 | 数量 | 资源内存 |
| --- | --- | --- |
| Texture2D | 251 | 43.1 MB |
| **TextureCube** | **3** | **16.5 MB** |
| Material | 152 | 15.0 MB |
| StaticMesh | 136 | 10.6 MB |
| **VolumeTexture** | **7** | **10.5 MB** |
| FontFace | 7 | 4.8 MB |

### 五、🔴 反直觉：10 张贴图占 63%

**3 张 cubemap (16.5MB) + 7 张 volume (10.5MB) = 27 MB，
而 251 张 Texture2D 才 43 MB。**

**但逐个列过：这 10 个**全是 `/Engine/`** —— 没有任何一张是 `/Game/`。**
```
/Engine/EngineResources/DefaultTextureCube
/Engine/MapTemplates/Sky/DaylightAmbientCubemap
/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128
/Engine/EngineMaterials/Hair/Hair_DualScattering
...
```

**→ 本项目内存大头是**引擎编辑器开销**，不是项目内容。**
**→ 要评估项目真实占用，必须量**打包版**。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-MEMORY.md`** | memreport 机制 + obj cycles + obj refs + 实测数据 |
| `Tools/practice_memory_commands.py` | 跑 obj cycles / memreport |
| `Tools/list_expensive_textures.py` | 列贵的 cube/volume 贴图 |

**证据：`Saved/Profiling/MemReports/` 里那份 468.5 KB 报告。**

### 七、这轮学到的排查套路

**「内存一直在涨」的六步：**
1. `memreport -full` 记基线
2. 做可疑操作 N 次
3. 再 `memreport -full`
4. 对比两份，看哪一类 **Count 涨了** → 对象泄漏
5. 看哪一类 **Count 不变但 NumKB 涨** → 同一对象在累积
6. `obj cycles` + `obj refs name=<对象>` 定位持有者

**⚠️ 第 4 和第 5 必须分开 —— 它们的病因完全不同。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **渲染调试** —— `r.*` CVar、VisualizeBuffer、`r.ShaderPrint`、GPU 抓帧 |
| 2 | 蓝图与脚本调试 |
| 3 | 网络调试 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 61." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 61; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
