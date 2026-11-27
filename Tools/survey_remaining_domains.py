"""Survey the four remaining domains by size, so effort follows mass rather than curiosity.

Audio, UI, networking and the asset pipeline are the blocks still to study. Which one to read
first should depend on how much there is and how much this project needs, not on which sounds
interesting. This measures the headers that define each domain and picks out the core class of
each, then writes the numbers down so the ordering is a decision rather than a mood.

    python Tools/survey_remaining_domains.py
"""

import os

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

DOMAINS = {
    "音频": [
        ("SoundBase.h", "所有可播放声音的基类"),
        ("SoundWave.h", "导入的音频文件"),
        ("AudioComponent.h", "挂在 Actor 上播放声音"),
        ("AudioSettings.h", "项目级音频设置"),
        ("SoundClass.h", "音量分组"),
        ("SoundMix.h", "混音状态"),
    ],
    "UI (UMG)": [
        ("UserWidget.h", "蓝图可做的 UI"),
        ("WidgetBlueprintLibrary.h", "UI 函数库"),
        ("PanelWidget.h", "容器控件"),
        ("WidgetComponent.h", "3D 世界里的 UI"),
        ("WidgetTree.h", "控件层级"),
    ],
    "UI (Slate)": [
        ("SWidget.h", "所有控件的基类"),
        ("SWindow.h", "窗口"),
        ("SlateStyle.h", "样式表"),
    ],
    "网络": [
        ("NetDriver.h", "网络驱动"),
        ("RepLayout.h", "复制的内存布局"),
        ("NetSerialization.h", "序列化原语"),
        ("PlayerController.h", "已读"),
        ("GameModeBase.h", "已读"),
    ],
    "资产管线": [
        ("AssetRegistry.h", "资产索引"),
        ("AssetManager.h", "资产加载策略"),
        ("StreamableManager.h", "异步加载"),
        ("Package.h", "资产包"),
    ],
}


def size_of(name):
    for root, dirs, files in os.walk(ENGINE):
        if name in files:
            return os.path.getsize(os.path.join(root, name)), os.path.join(root, name)
    return None, None


def main():
    total = 0
    for domain, entries in DOMAINS.items():
        found = []
        for name, purpose in entries:
            size, path = size_of(name)
            if size is not None:
                found.append((size, name, purpose))
                total += size
        found.sort(reverse=True)
        domain_total = sum(size for size, _, _ in found)
        print("=== %s   %d headers, %d bytes total" % (domain, len(found), domain_total))
        for size, name, purpose in found:
            print("   %-32s %8d B   %s" % (name, size, purpose))
        print("")

    print("all four domains: %d bytes of headers" % total)
    print("")
    print("This project's actual need, for ordering the work:")
    print("  音频   - 481 files extracted, 10 referenced-but-absent; simple component use")
    print("  UI     - 253 window scripts analysed, no runtime framework yet")
    print("  网络   - single-player vertical slice; replication not needed yet")
    print("  资产   - already using AssetTools and import_asset daily")
    print("")
    print("So the next block should be the asset pipeline, not networking: it is in use now.")


if __name__ == "__main__":
    main()
