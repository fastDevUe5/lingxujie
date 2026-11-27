"""Add the audio gotcha and point the index at the new document.

    python Tools/add_audio_gotcha.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRY = """
## 73. `play_sound_at_location` 的 rotation 是必需参数

- **症状**：`unreal.GameplayStatics.play_sound_at_location(world, sound, location)` 报
  `TypeError: play_sound_at_location() required argument 'rotation' (pos 4) not found`
- **根因**：反射签名里 `rotation` 没有默认值，没有省略它的重载
- **修法**：显式传 `unreal.Rotator(0, 0, 0)`
- **出处**：2026-11-26，音频实测
"""

OLD_INDEX = "| **音频 / UI / 网络** | **`Docs/UE5-OTHER-DOMAINS.md`** | 三域规模 + 该用哪个类 |"
NEW_INDEX = (
    "| **音频导入与播放** | **`Docs/UE5-AUDIO.md`** | **实测通过**：wav→SoundWave→播放；rotation 必需 |\n"
    "| **UI / 网络（未深入）** | **`Docs/UE5-OTHER-DOMAINS.md`** | 两域规模 + 该用哪个类 |"
)


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 73." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 73")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index:
        index = index.replace(OLD_INDEX, NEW_INDEX)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row not found; check whether it was already split")


if __name__ == "__main__":
    main()
