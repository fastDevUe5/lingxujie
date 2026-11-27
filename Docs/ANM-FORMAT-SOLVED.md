# `.anm` 动画格式：**完全解开，含帧率**（2026-11-26）

> **状态：完全解决。30 fps 是从 ticks 推导出来的，不是猜的。**
>
> **方法教训（gotcha #81）：先读研究区的客户端源码 + 已有文档，不要从二进制猜。**

---

## 一、文件结构（实测 `108_birda.anm`，29,764 字节）

```
[0 .. 206)              文件头（**不是固定 160！**）
[206 .. 26950)          11 个 0xF000 块，连续
[26950 .. 29764)        2,814 字节尾部（资源引用）
```

### 1.1 🔴 文件头长度**不固定** —— 必须扫描

**`anm-container-solved.md` 说头是 160 字节，但这个文件第一个块在 **206**。**

**160..206 之间的字节是**堆地址**（`0x77D1xxxx` 这类值）—— 说明写入时把运行时指针也 dump 了。**

**所以正确做法：扫描 `00 F0 00 00` 找第一个块，不要假设 160。**

```python
for offset in range(len(data) - 8):
    if data[offset:offset+4] == b'\x00\xF0\x00\x00':
        size = u32(data, offset+4)
        if 152 <= size and offset + 8 + size <= len(data):
            start = offset; break
```

### 1.2 块头 = **8 字节**

```
+0  u32  marker = 0x0000F000
+4  u32  size              （载荷字节数）
+8  载荷
```

**和 `.mod` 的块头结构一样。**

### 1.3 载荷 = `FILE_MOTION_OBJECT_HEADER`（**152 字节**）+ 关键帧

```c
struct FILE_MOTION_OBJECT_HEADER {   // 152 字节
    DWORD  dwIndex;                  // +0
    DWORD  dwRotKeyNum;              // +4
    DWORD  dwPosKeyNum;              // +8
    DWORD  dwScaleKeyNum;            // +12
    DWORD  dwAnimatedMeshKeyNum;     // +16
    char   szObjectName[128];        // +20   骨骼名
    CMotionFlag motionFlag;          // +148  (4 字节 flags)
};
// = 5×4 + 128 + 4 = 152 ✓
```

### 1.4 关键帧顺序（源码 `CMotionObject::ReadFile`）

```c
FSRead(&header, 152);
if (dwPosKeyNum)    FSRead(POS_KEY   × dwPosKeyNum);     // 20 字节
if (dwRotKeyNum)    FSRead(ROT_KEY   × dwRotKeyNum);     // 24 字节
if (dwScaleKeyNum)  FSRead(SCALE_KEY × dwScaleKeyNum);   // 40 字节
```

```c
struct POS_KEY   { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Pos; };        // 20
struct ROT_KEY   { DWORD dwTicks; DWORD dwFrame; QUARTERNION Q; };        // 24
struct SCALE_KEY { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Scale;
                   VECTOR3 v3ScaleAxis; float fScaleAxisAng; };          // 40
```

**⚠️ 顺序是 POS → ROT → SCALE，不是 ROT 先。**

---

## 二、字节数学精确对上（实测）

**`108_birda.anm` 全部 11 块，`expected == size` 全部 `OK`：**

| # | 名称 | rot | pos | scale | size | 验算 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `Line01` | 0 | 0 | 0 | 152 | 152 ✓ |
| 1 | `Bone03` | 0 | 0 | 0 | 152 | 152 ✓ |
| 2 | `Bone02` | 136 | 0 | 0 | 3416 | 152 + 136×24 = **3416** ✓ |
| 3 | `Bone01` | 136 | 0 | 0 | 3416 | ✓ |
| 4 | `Bone06` | 0 | 0 | 0 | 152 | ✓ |
| 5 | `Bone05` | 136 | 0 | 0 | 3416 | ✓ |
| 6 | `Bone04` | 136 | 0 | 0 | 3416 | ✓ |
| 7 | `Bone08` | 0 | 0 | 0 | 152 | ✓ |
| 8 | `Bone07` | 136 | 135 | 0 | 6116 | 152 + 3264 + 2700 = **6116** ✓ |
| 9 | `Bone09` | 136 | 135 | 0 | 6116 | ✓ |
| 10 | `objdefault` | 0 | 0 | 0 | 152 | ✓ |

**11 块，每一块字节数精确吻合。**

---

## 三、🔴 帧率：**30 fps**（推导，不是猜）

### 3.1 ticks 与 frame 的实际数值

```
Bone07 位移:
  [0] ticks=160  frame=0  pos=(-27.157, 15.732, 0.006)
  [1] ticks=480  frame=2  pos=(-27.157, 27.018, 0.006)
  [2] ticks=800  frame=4  pos=(-27.157, 39.107, 0.006)
```

**ticks 间距 320，frame 间距 2 → **160 ticks / 帧**。**

### 3.2 跨 60 个文件统计

```
distinct ticks-per-frame values: [1.0, 160.0]
```

**几乎全是 160（一个异常值 1.0）。**

### 3.3 ticks/秒 的候选

| ticks/秒 | 推导 fps | 合理性 |
| --- | --- | --- |
| **4800** | **30.0** | ✅ **干净整数，且是 3ds Max 的 `TICKS_PER_SECOND`** |
| 3200 | 20.0 | 也整数，但不是 Max 常量 |
| 160000 | 1000.0 | 不合理 |
| 1000 | 6.25 | 不合理 |
| 90000 | 562.5 | 不合理 |

**→ 结论：4800 ticks/秒，160 ticks/帧，**30 fps**。**

**依据：墨香的骨架是**标准 3ds Max Biped**（研究区统计：`Bip01 R Finger` 出现 16,052 次），
而 3ds Max 的 ticks 常量就是 4800/秒。**

### 3.4 这对导入意味着什么

**`UE5-ANIMATION-ENGINE.md` 里把帧率列为"降为调参"，现在**可以直接定 30 fps**，
不用调。glTF 的 `input` accessor 要秒，所以：**

```
time_seconds = ticks / 4800.0
```

**或者等价地 `frame / 30.0`。**

---

## 四、完整读取算法（可实现的伪代码）

```python
data = read(path)

# 1. 扫描第一个块（头长度不固定）
start = scan_for_block(data, marker=0x0000F000, min_size=152)

# 2. 逐块
offset = start
bones = []
while data[offset:offset+4] == b'\x00\xF0\x00\x00':
    size    = u32(data, offset + 4)
    payload = offset + 8
    hdr     = payload                    # 152 字节
    index, rot_n, pos_n, scale_n, mesh_n = 5×u32(hdr)
    name    = gbk_string(hdr + 20, 128)
    cursor  = hdr + 152
    pos   = [read(POS_KEY,   20) for _ in range(pos_n)];   cursor += 20 * pos_n
    rot   = [read(ROT_KEY,   24) for _ in range(rot_n)];   cursor += 24 * rot_n
    scale = [read(SCALE_KEY, 40) for _ in range(scale_n)]; cursor += 40 * scale_n
    bones.append((name, pos, rot, scale))
    offset = payload + size

# 3. 转 glTF animation
for each bone:
    for each key:
        t_seconds = key.dwTicks / 4800.0
```

---

## 五、链路现在完整了

```
.mod（网格 + 蒙皮）      ✅ 已解开（MOD-FORMAT-SOLVED.md）
   ↓ 导出器已验证
SkeletalMesh in UE       ✅ 已导入并可见（鸟）
   ↓
.anm（动画 + 30fps）     ✅ 本轮解开
   ↓ 待写导出
AnimSequence in UE       待做
```

**剩下的是**纯工程**：把 `.anm` 的关键帧写进 glTF 的 animation 通道，
然后 `AssetImportTask` 一并导入。**

---

## 六、工具

| 工具 | 作用 |
| --- | --- |
| `Tools/inspect_anm.py` | dump 头部 + 首块原始字节 |
| `Tools/scan_anm_blocks.py` | 扫描所有块（不假设头长度）|
| **`Tools/parse_anm_motion.py`** | **按客户端结构解析，逐块验算字节数** |
| **`Tools/verify_anm_tickrate.py`** | **跨 60 文件统计 ticks/帧 → 帧率** |

---

## 七、重查命令

```powershell
python Tools\parse_anm_motion.py "C:\...\resources\anm\108_birda.anm"
python Tools\verify_anm_tickrate.py
```

**源码出处：**
```
研究区 client_src\tw\4DyuchiGXGeometry\motion_obj.cpp     -- CMotionObject::ReadFile
研究区 client_src\tw\4DyuchiGXGeometry\motion_obj.h       -- 三个 KEY 结构
研究区 client_src\tw\4DyuchiGRX_common\motion_flag.h      -- CMotionFlag
研究区 Docs\reverse-engineering\anm-fully-solved.md       -- 步长语义
研究区 Docs\reverse-engineering\anm-container-solved.md   -- 容器结构
```
