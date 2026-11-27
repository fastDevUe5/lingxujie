"""Replace gotcha 79 with the corrected version, and fix the audio document.

The original entry reported the uasset size as the shipping cost and concluded compression did
nothing. Both were wrong. The log reports the cooked size explicitly, and it changed from 3,103 KB
to 2,247 KB when quality went from 80 to 40. The uasset holds the editor-side source wave, which is
why changing a runtime compression setting cannot move it.

    python Tools/fix_audio_gotcha.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
AUDIO = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-AUDIO.md"

OLD_HEADER = "## 79. mp3 导入成 SoundWave 后体积涨 7 倍"
NEW_ENTRY = """## 79. uasset 体积不是运行时体积 —— 判断音频开销要看日志的压缩行

- **我先写错的版本**：说「mp3 导入后涨 7 倍」，用 `S_bg_field.uasset` 11.14 MB 当运行时开销。
  **这是错的。**
- **实测数据**（`LogAudioDerivedData` 的压缩行，才是运行时数据）：
  ```
  质量 80: S_bg_field 压缩为 17.39%（从 17,851KB 到 3,103KB）
  质量 40: S_bg_field 压缩为 12.59%（从 17,851KB 到 2,247KB）
  ```
  | 项 | 值 |
  | --- | --- |
  | 源波形（PCM） | 17,851 KB |
  | **质量 80 运行时** | **3,103 KB** |
  | **质量 40 运行时** | **2,247 KB**（小 28%）|
  | `uasset` 磁盘 | 11,140 KB ← **编辑器侧源波形** |
- **根因**：`uasset` 里存的是**编辑器用的源波形**，运行时压缩数据在
  `DerivedDataCache` / 打包后的 pak 里。**改运行时压缩质量不会改 uasset 大小。**
- **怎么量运行时大小**：读日志的 `LogAudioDerivedData` 行，或打包后看 pak
- **修法**：`sound.set_editor_property("compression_quality", 40)` **确实生效**
  （质量 80 → 40 让运行时从 3,103 KB 降到 2,247 KB）
- **出处**：2026-11-26，第一次判断错误后的二次更正
"""


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    start = text.find(OLD_HEADER)
    if start < 0:
        print("gotcha 79 header not found (already fixed?)")
    else:
        # The entry runs to the next "## " heading or end of file.
        next_heading = text.find("\n## ", start + len(OLD_HEADER))
        end = next_heading if next_heading > 0 else len(text)
        text = text[:start] + NEW_ENTRY + text[end:]
        open(GOTCHAS, "w", encoding="utf-8").write(text)
        print("gotcha 79 replaced with the measured version")

    # Correct the audio document's section 10.4.
    audio = open(AUDIO, encoding="utf-8").read()
    old_block = "**导入后体积涨了 7.7 倍。**"
    if old_block in audio:
        replacement = """**这一条我写错过，更正如下：**

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
**12 首 BGM 按质量 40 算约 27 MB 运行时，不是 132 MB。**"""
        audio = audio.replace(old_block, replacement)
        open(AUDIO, "w", encoding="utf-8").write(audio)
        print("audio document corrected")
    else:
        print("audio block not found or already corrected")


if __name__ == "__main__":
    main()
