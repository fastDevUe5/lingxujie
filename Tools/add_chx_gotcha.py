"""Add gotcha 90 about the chx binary prefix and case mismatch.

    python Tools/add_chx_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 90. `.chx` 有的带二进制头尾，且名字大小写和磁盘不一致

- **症状**：直接按文本读 `.chx` 拿到乱码开头
  （`m_do+10.chx` 开头是 `}   Q     øê`）
- **根因**：部分 `.chx` 在文本列表前后各有一段**二进制头/尾**
- **修法**：
  ```python
  start = text.find("*MOD_FILE_NUM")   # 不假设从字节 0 开始
  # 收集动画名时，遇到不以 .ANM 结尾的行就停（后面是二进制尾）
  ```
- **第二个坑**：`.chx` 里的名字大小写可能和磁盘不一致
  （`boss_cowi_01` 列出的是 `Boss_cowI_01.anm`）
  → 查找要**不区分大小写**，并对目录做一次扫描兜底
- **成果**：1,081 个模型 / 21,919 条动画引用 / **21,878 条解析成功（99.8%）**
- **出处**：2026-11-26，批量导出配对
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 90." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotcha 90")


if __name__ == "__main__":
    main()
