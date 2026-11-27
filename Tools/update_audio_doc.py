"""Append the level-music result to the audio document.

    python Tools/update_audio_doc.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-AUDIO.md"

SECTION = """
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

**导入后体积涨了 7.7 倍。**

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
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十、关卡背景音乐接入" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
