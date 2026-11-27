"""Append the eighteenth debugging round.

    python Tools/write_debug_round18.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 75. 调试系列第 18 轮：**症状手册 + 两个工具坑**（2026-11-26 60:00）

### 一、把七次实战压缩成决策索引

**`Docs/UE5-DEBUG-PLAYBOOK.md` —— 不是知识文档，是**症状 → 该查什么**的索引。**

| 类别 | 覆盖的症状 |
| --- | --- |
| 模型看起来不对 | 散开 / 躺地 / 100 倍大小 / 黑块 / 灰格 / 包围盒对但比例怪 |
| 动画不动 | 没赋值 / 模式错 / 改位置没反应 / `get_bone_pose` 挂死 |
| 日志 Error/Warning | 6 种常见文本 → 该查什么 |
| 性能 | 30fps 显示绿 / 平均好看但有卡顿 / CVar 没效果 |
| 内存 | 环数 ≠ 泄漏 / 对象为何不销毁 / 内存涨的六步法 |
| 渲染 | 缓冲可视化只有 UI / `vis` 拼错名字静默 |
| 脚本 | 没输出 / 异常定位 / 对话框卡死 |
| 崩溃 | `PCallStack` 不是 `CallStack` |

**第五节是**五种推理错误**及各自的防法：**
1. 数字真但含义错（101 个缺材质）
2. 分母错（Textures 只有 1 个）
3. 把方法失败当事情做不到（`set_position` 不求值）
4. 自证式验证（IBM 往返误差 2e-16）
5. **把报错当结果**（`Get-Process` 报错 → 以为进程没了）

### 二、🔴 这一轮又犯了第 5 种错误两次

| # | 我做了什么 | 我看到什么 | 实际 |
| --- | --- | --- | --- |
| 1 | `Get-Content Docs/UE5-DEBUG-INDEX.md -First 6` | 中文全是乱码 | **文件是正常 UTF-8**，只是 PowerShell 默认按 GBK 读 |
| 2 | `-replace 'IBMFix','IBMFix2'` 改脚本 | 导入静默失败 | **文件名被替换成 `boss001_IBMFIX222.gltf`** |

**→ 第 1 次我差点去修一个没坏的文件。**
**→ 第 2 次是 `-replace` 全局替换，不区分标识符和文件名。**

**两条都记进 gotcha（#109 / #110）。**

### 三、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-PLAYBOOK.md`** | 症状 → 该查什么（八类 + 五种推理错误 + 工具边界）|
| `Docs/UE5-Gotchas.md` #109 | `Get-Content` 不写 `-Encoding UTF8` 显示乱码 |
| `Docs/UE5-Gotchas.md` #110 | PowerShell `-replace` 会连文件名一起替换 |

**Gotchas 总数：108 → **110 条**。**

### 四、调试系列现在的完整结构

| 层 | 文档 |
| --- | --- |
| **入门** | **`UE5-DEBUG-INDEX.md`（索引，顶部指向手册）** |
| **决策** | **`UE5-DEBUG-PLAYBOOK.md`（症状 → 查什么）** |
| 机制 | `LOGGING` / `ASSERTS` / `CRASH` / `PERF` / `MEMORY` / `RENDER` / `SCRIPT` / `NET` / `ASSET` |
| 实战 | 案例 001-007 |
| 工具 | `UE5-DEBUG-TOOLKIT.md` + `Tools/diagnose.py` |

**→ 从「遇到问题从哪看」到「机制是什么」到「真跑一遍」到「自动查」，形成闭环。**

### 五、下一轮

**调试系列该收口了。剩下的选择：**
1. **应用已定位的修复**（3 处导出器 + 1 处材质）—— 这会改代码
2. 继续找新问题

**⚠️ 代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 75." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 75; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
