"""Add the two PowerShell encoding facts learned this round as gotchas.

Both were my own tools misleading me rather than the files being wrong, which is the category this
project keeps rediscovering.

    python Tools/add_encoding_gotchas.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 109. `Get-Content` 不写 `-Encoding UTF8` 会把中文显示成乱码

- **症状**：`Get-Content Docs/UE5-DEBUG-INDEX.md -First 6` 输出
  `# UE5 璋冭瘯涓庨棶棰樺畾浣?路 绯诲垪绱㈠紩`
- **我当时以为**文件编码被我的脚本写坏了
- **实际**：文件是**正常 UTF-8**，解码验证：
  ```
  前 120 字节 hex: 2320554535 20e8b083e8af95e4b88e…
  UTF-8 解码: 成功
  第一行: # UE5 调试与问题定位 · 系列索引
  ```
- **原因**：PowerShell 5.1 的 `Get-Content` 默认按系统 ANSI（本机 GBK）读，不按 UTF-8
- **修法**：
  ```powershell
  Get-Content file.md -Encoding UTF8 -First 6
  ```
  或者用 `read` 工具（它按 UTF-8 读）
- **⚠️ 这是我**第二次**把「工具输出异常」当成「数据有问题」**
  （第一次见 #108 的 `Get-Process` 报错被误读为进程消失）
- **教训**：**显示乱码先查读取端的编码，别先怀疑文件。**
- **出处**：2026-11-26，症状手册索引

## 110. PowerShell 的 `-replace` 会连文件名一起替换

- **症状**：`(Get-Content x.py) -replace 'IBMFix', 'IBMFix2'` 之后，
  脚本里的路径变成 `boss001_IBMFIX222.gltf`，导入静默失败
- **原因**：`-replace` 是**全局正则替换**，不区分「代码里的标识符」和「字符串里的文件名」
- **后果**：Interchange 报 `使用所选的管线` 无法导入，`imported_object_paths` 为空
- **修法**：
  - **改脚本用 `edit` / `write` 工具，不用字符串替换**
  - 真要替换时，锚定上下文（如替换整行而不是子串）
- **⚠️ 和 #109 同一类：工具的行为和我以为的不同**
- **出处**：2026-11-26，验证 IBM 修复
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 109." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    print("added gotchas 109 and 110")

    agents = "C:/Users/tk/Desktop/lingxujie/AGENTS.md"
    text = open(agents, encoding="utf-8").read()
    text = text.replace("（**108 条**）", "（**110 条**）")
    text = text.replace("新增的 #28–#108", "新增的 #28–#110")
    open(agents, "w", encoding="utf-8").write(text)
    print("AGENTS.md count synced to 110")


if __name__ == "__main__":
    main()
