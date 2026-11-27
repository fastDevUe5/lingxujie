"""Record the factory naming inconsistency, which costs time every time it is rediscovered.

Asset creation factories do not follow one naming rule. Some carry a New suffix and some do not,
and the error names an attribute rather than the convention, so the only way to know is to look it
up. This writes the mapping down.

    python Tools/add_factory_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 74. 资产工厂类名**有的带 New 有的不带** —— 猜必错

- **症状**：`tools.create_asset(name, path, unreal.SoundClass, unreal.SoundClassFactoryNew())` 报
  `AttributeError: module 'unreal' has no attribute 'SoundClassFactoryNew'`
- **根因**：引擎的工厂类命名不统一，同一个模块里两种风格并存：
  ```
  USoundClassFactory        <- 没有 New
  USoundAttenuationFactory  <- 没有 New
  USoundMixFactory          <- 没有 New
  USoundConcurrencyFactory  <- 没有 New
  USoundCueFactoryNew       <- 有 New
  UMaterialFactoryNew       <- 有 New
  UStaticMeshFactoryNew     <- 有 New
  ```
- **怎么查**：扫引擎源码找真实类名，不要猜：
  ```python
  # 找所有继承 UFactory 的音频相关类
  re.finditer(r'class\\s+(?:\\w+_API\\s+)?(U\\w*Factory\\w*)\\s*:\\s*public\\s+UFactory', text)
  ```
- **修法**：先 `Tools/list_python_toolset_tools.py` 看有没有现成工具，
  再扫源码确认工厂名，**最后才写代码**
- **出处**：2026-11-26，建音频系统时踩到
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 74." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    import re
    numbers = re.findall(r"^## (\d+)\.", text + ENTRY, re.M)
    print("added gotcha 74; total %d" % len(numbers))


if __name__ == "__main__":
    main()
