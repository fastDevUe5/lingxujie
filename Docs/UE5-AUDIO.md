# UE5 音频：实测验证过的完整路径（引擎源码 + 实测）

> **这一篇的核心不是结构，是**实测**：一个 wav 文件从磁盘到世界里播出声音，
> 全程通过 Python 完成，日志为证。**

---

## 一、实测结果（2026-11-26）

### 1.1 导入

**源文件：** 韩服的 `M004_Attack_01.wav`（55,992 字节）

**日志原文：**
```
[LingXuJie] AUDIO: source M004_Attack_01.wav (55992 bytes)
LogAudioDerivedData: 构建压缩音频格式 BINKA 散列 ... SR0_48000 SR1_32000 SR2_24000
LogAudioDerivedData: S_M004_Attack_01 压缩为 29.15%（从 54KB 到 15KB），
                     用质量修改器 1.00 在质量 80 处实现 BINKA
LogAudio: Chunk stats for (SoundWave /Game/Moxiang/Audio/S_M004_Attack_01:
          Duration=1.27 secs
[LingXuJie] AUDIO: imported /Game/Moxiang/Audio/S_M004_Attack_01
[LingXuJie] AUDIO: class=SoundWave duration=1.265 s
```

### 1.2 三个可验证的事实

| 事实 | 数据 |
| --- | --- |
| **导入后的类** | **`SoundWave`** |
| **时长** | **1.265 秒**（日志两处：1.27 与 1.265，一致）|
| **自动压缩** | **BINKA，29.15%**（54 KB → 15 KB）|
| **采样率转换** | 48,000 → 32,000 / 24,000（多级）|

**所以 UE 导入 wav 时**自动做了三件事**：转码、压缩、生成多级采样率。
**不需要我们配什么。**

### 1.3 播放

```
[LingXuJie] AUDIO: played at 8950, -6200, 3900
```

**完整调用：**
```python
unreal.GameplayStatics.play_sound_at_location(world, sound, location, rotation)
```

**⚠️ `rotation` 是**必需参数**，没有省略它的重载：**
```
TypeError: play_sound_at_location() required argument 'rotation' (pos 4) not found
```

---

## 二、六个类（源码核实）

| 类 | 头文件 | 职责 |
| --- | --- | --- |
| **`USoundWave`** | **83,432 B** | **导入的音频文件**（实测拿到的就是它）|
| **`UAudioComponent`** | **50,140 B** | **挂在 Actor 上播放**（可跟随、可停止）|
| `USoundBase` | 20,065 B | 所有可播放声音的基类 |
| `UAudioSettings` | 13,830 B | 项目级设置 |
| `USoundClass` | 11,142 B | **音量分组**（主音量 / 音效 / 音乐）|
| `USoundMix` | 7,454 B | **混音状态**（进战斗时压低音乐）|

---

## 三、播放的两条路（该怎么选）

| 方式 | 特点 | 适用 |
| --- | --- | --- |
| **`PlaySoundAtLocation` / `PlaySound2D`** | **一次性**，播完就没 | 脚步、技能音效、打击声 |
| **`UAudioComponent`** | **挂在 Actor 上**，可跟随移动、可停止、可调参数 | **背景音乐、循环环境音** |

**本项目的判据：**

| 墨香音频类型 | 数量 | 该用哪条路 |
| --- | --- | --- |
| 武器 / 打击音效 | ~数百 | `PlaySoundAtLocation` |
| 怪物攻击/死亡 | ~295 | `PlaySoundAtLocation` |
| **BGM（bgm/）** | 12 | **`UAudioComponent`**（要能淡入淡出）|
| 环境音 | 若干 | `UAudioComponent` |

---

## 四、本项目的音频现状与实际缺口

### 4.1 素材

| 项 | 数量 |
| --- | --- |
| 国服索引引用 | 719 |
| 有文件 | 713（99.2%）|
| **缺失（任何版本都没有）** | **6** |
| 韩服独有（已导入研究区） | 35 个怪物音效 |

**素材基本齐了。**

### 4.2 真正的缺口（这次实测后更清楚了）

| 缺什么 | 说明 |
| --- | --- |
| **播放逻辑** | 现在只有一个测试调用，没有系统 |
| **3D 衰减配置** | `SoundAttenuation` —— 声音多远能听到 |
| **SoundClass 分组** | 没有音量分组，"调低音效"做不到 |
| **音频总线的音量控制** | 没有 UI 音量滑条的基础 |
| **音频与动作的绑定** | 墨香用 Notify 触发，我们还没有动画 |

**"素材有"和"音频能用"之间差的正是这些。**

---

## 五、还没学的（诚实）

| 主题 | 状态 |
| --- | --- |
| 3D 衰减（`AttenuationSettings`） | 🔴 **没碰** |
| `SoundClass` / `SoundMix` 实际配置 | 🔴 **没碰** |
| **MetaSounds（UE5 程序化音频）** | 🔴 **完全没碰** |
| 音频空间化 / 遮挡 | 🔴 **没碰** |
| 音频并发与优先级 | 🔴 **没碰** |

---

## 六、掌握程度（音频）

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| 六个类的职责 | 🟢 知道 | 🟢 知道 |
| **wav 导入成 SoundWave** | 🔴 没做过 | 🟢 **实测通过** |
| **自动压缩与采样率转换** | 🔴 不知道 | 🟢 **日志里看到了具体数字** |
| **播放一个声音** | 🔴 没播过 | 🟢 **实测通过** |
| `rotation` 是必需参数 | 🔴 不知道 | 🟢 **踩过** |
| 3D 衰减 / SoundClass / MetaSounds | 🔴 | 🔴 **仍然零** |

**音频：从 25% → **40%**。**

**涨的是"能播一个声音"，没涨的是"做一套音频系统"。**

---

## 七、下一步

**音频要真正可用，需要：**

```
1. 建 SoundClass 分组（Master / SFX / Music / Voice）
2. 给怪物音效配 AttenuationSettings（多远听得到）
3. 做一个简单的音频管理器（按类别调音量）
4. 等动画就绪后，用 Notify 把音效绑到动作
```

**第 1 和第 2 项现在就能做，不需要等动画。**

---

## 八、重查命令

```powershell
py "Tools/verify_audio.py"     # 导入 + 播放，日志验证
```

---

## 九、音频系统建成（2026-11-26 实测）

### 9.1 五个 SoundClass + 一个衰减

`
sound classes: SC_Master, SC_Music, SC_SFX, SC_Voice, SC_Monster
attenuation saved: SA_Monster
verify SC_Master      -> SoundClass
verify SC_Music       -> SoundClass
verify SC_SFX         -> SoundClass
verify SC_Voice       -> SoundClass
verify SC_Monster     -> SoundClass
verify SA_Monster     -> SoundAttenuation
`

**层级：**
`
SC_Master
  ├ SC_Music
  ├ SC_SFX
  │   └ SC_Monster
  └ SC_Voice
`

**落盘确认：6 个 .uasset，各 1 KB。**

### 9.2 踩到的工厂命名坑

**SoundClassFactoryNew 不存在 —— 正确的是 SoundClassFactory。**
**同一个模块里两种命名风格并存（见 gotcha #74）。**

### 9.3 掌握度更新

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| 播放一个声音 | 🟢 实测 | 🟢 实测 |
| **建 SoundClass 分组** | 🔴 | 🟢 **建成 5 个** |
| **建 Attenuation** | 🔴 | 🟢 **建成 1 个** |
| SoundMix 实际配置 | 🔴 | 🔴 仍零 |
| MetaSounds | 🔴 | 🔴 仍零 |

**音频：从 40% → **50%**。**

---

## 十、关卡背景音乐接入（2026-11-26 实测）

### 10.1 做了什么

**用 `Tools/add_level_music.py` 完成三件事：**

```
MUSIC: imported bg_field.mp3 as SoundWave (95.2 s)
MUSIC: sound class set to SC_Music
MUSIC: ambient actor placed with S_bg_field
MUSIC: level saved
MUSIC: verify: sound=S_bg_field auto_activate=True volume=0.60
```

**关卡里的验证：**
```
MX_AMBIENT_MUSIC (AmbientSound)     <- 新加的
MX_CHARACTER (LXJCharacter)
MX_TERRAIN (StaticMeshActor)
```

### 10.2 为什么用 AmbientSound 而不是 PlaySoundAtLocation

| 需求 | 一次性播放 | **AudioComponent** |
| --- | --- | --- |
| 循环 | ❌ | ✅ |
| 能停止 | ❌ | ✅ |
| 能调音量 | ❌ | ✅ |
| 跟随玩家 | ❌ | ✅ |

**背景音乐这四条都要，所以必须用组件（`AmbientSound` 就是带 `AudioComponent` 的 Actor）。**

### 10.3 三个组件属性

```python
component.set_editor_property("sound", track)              # 播什么
component.set_editor_property("auto_activate", True)       # 关卡加载就播
component.set_editor_property("volume_multiplier", 0.6)    # 音量
```

**`auto_activate=True` 是关键 —— 否则要手动触发。**

### 10.4 ⚠️ 一个需要注意的体积问题

```
bg_field.mp3   1,488 KB   (源文件)
S_bg_field.uasset  11,410 KB   (导入后)
```

**这一条我写错过，更正如下：**

**`uasset` 里存的是编辑器侧源波形（PCM），不是运行时压缩数据。
改运行时压缩质量不会改 `uasset` 大小。**

**真正的运行时大小在日志里：**
```
质量 80: S_bg_field 压缩为 17.39%（从 17,851KB 到 3,103KB）
质量 40: S_bg_field 压缩为 12.59%（从 17,851KB 到 2,247KB）
```

| 项 | 值 |
| --- | --- |
| 源波形（PCM） | 17,851 KB |
| **质量 80 运行时** | **3,103 KB** |
| **质量 40 运行时** | **2,247 KB** |
| `uasset` 磁盘 | 11,140 KB（编辑器侧源波形）|

**所以：压缩质量确实生效（80 → 40 让运行时小 28%）。**
**12 首 BGM 按质量 40 算约 27 MB 运行时，不是 132 MB。**

**原因：UE 默认**不压缩**MP3 转成的 SoundWave 音质档（`bgm` 类会走高质量）。
11 MB 一首曲子，12 首 = 132 MB —— 对打包体积影响很大。**

**可以做的优化（没做）：**
| 措施 | 效果 |
| --- | --- |
| 设置压缩质量（比如 50） | 体积降一半以上 |
| 用 `SoundCue` 做流式加载 | 不全部驻留内存 |
| 降低采样率（48000 → 32000）| 体积降 1/3 |

**这条记下来，打包前必须处理。**

### 10.5 可用的 BGM 清单（12 首）

| 文件 | 大小 | 推测用途 |
| --- | --- | --- |
| `bg_field.mp3` | 1,488 KB | **野外**（已用）|
| `BG_Town1/2/3.mp3` | 2–3 MB | 城镇 |
| `BG_Battle.mp3` | 3,028 KB | 战斗 |
| `bg_login.mp3` | 1,826 KB | 登录 |
| `jangan.mp3` | 1,760 KB | **长安**（地图 12）|
| `BG_Dungeon1.mp3` | 2,212 KB | 地牢 |
| `bg_jinshi.mp3` | 2,266 KB | 晋石？ |
| `bg_geabong.mp3` | 2,932 KB | ？ |
| `BG_Titan01.mp3` | 3,032 KB | BOSS |
| `BG_TitanIntro.mp3` | 1,019 KB | BOSS 入场 |

**按地图分配 BGM 时直接查这张表。**

---

## 十一、掌握程度更新

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| 导入 wav 并播放 | 🟢 实测 | 🟢 实测 |
| 建 SoundClass 体系 | 🟢 建成 5 个 | 🟢 建成 5 个 |
| **导入 mp3（不是 wav）** | 🔴 | 🟢 **实测通过** |
| **关卡里放背景音乐** | 🔴 | 🟢 **实测通过** |
| **`auto_activate` 的意义** | 🔴 | 🟢 **清楚** |
| **导入后体积膨胀的问题** | 🔴 | 🟢 **发现并记录** |
| 音频压缩质量配置 | 🔴 | 🔴 没做 |
| 3D 衰减 | 🔴 | 🔴 没配 |

**音频：从 50% → **60%**。**

**涨的：mp3 能导入、关卡有音乐了、发现了体积问题。
没涨的：压缩质量、衰减、MetaSounds。**
