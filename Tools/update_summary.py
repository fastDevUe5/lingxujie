"""Fold rounds thirty-seven and thirty-eight into the overview.

The summary was written at round thirty-six, before the material slots existed and before the
material fields were read. Leaving it stale would make the one document a new session reads first
the one most out of date, which is the opposite of its purpose.

    python Tools/update_summary.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-KNOWLEDGE-SUMMARY.md"

OLD_VERIFIED = (
    "| 材质管道通 | Boss 有棕色石材纹理，不再是灰的 |"
)
NEW_VERIFIED = (
    "| 材质管道通 | Boss 有棕色石材纹理，不再是灰的 |\n"
    "| **材质六段全通** | 材质块 → 贴图名 → 三种扩展名 → PNG → Texture2D → Material → 40 槽 |\n"
    "| **面组材质索引保真** | `primitives 17 → 40`、`materials 0 → 40`、UE 槽数 **1 → 40** |"
)

OLD_UNVERIFIED = (
    "| 材质**多槽**（Boss 有 40 个 MATERIAL 块但只用了 1 槽）| 未按槽分配 |"
)
NEW_UNVERIFIED = (
    "| 材质**多槽视觉差异** | 40 槽已全部赋材质，但源数据只有 1 张贴图 + 近乎统一颜色\n"
    "  —— **结构已修好，视觉差异源数据里就没有** |"
)

OLD_INVENTORY = "| UE 内的角色资产 | 4 组 × 4 资产 = 16 个 | — |"
NEW_INVENTORY = (
    "| UE 内的角色资产 | 4 组 × 4 资产 = 16 个 | — |\n"
    "| **Boss 材质槽** | **40 个，全部赋材质** | — |\n"
    "| **材质块字段** | 贴图名 + 3 组颜色 + 1 个 float，已解析 | — |"
)

ADDENDUM = """

---

## 八、第 37–38 轮的补充（材质结构）

### 8.1 材质槽：1 → 40

**`boss001.mod` 的 40 个 MATERIAL 块，原来只导入 1 个槽（全身一个表面）。**

**原因是面组的材质索引被合并了：**
```
MESH @83800: faceGroups=6
   group 0: mtl=39  index=5
   group 1: mtl=38  index=4
   ...
```

**修法：每个面组一个 primitive（glTF 允许多 primitive 共享顶点属性，只换索引缓冲）。**

**结果：**
```
primitives: 17 → 40
materials:  0  → 40
UE 槽数:    1  → 40
```

**回归：7 个模型包围盒**完全不变**，primitive 数各自增加。**

### 8.2 40 个材质只有 1 张贴图

**逐块打印 40 个 MATERIAL 块，全部引用 `boss_mob01.tga`，`dwIndex` 全是 0。**

**材质块字段布局（前 64 字节）：**
```
00000000  <- dwIndex
e8eff500  <- 颜色 1 = (232, 239, 245)
e8eff500  <- 颜色 2
ffffff00  <- 颜色 3 = 白
cccccc3d  <- float 0.100
偏移 156  <- 贴图名
```

**40 个块只有 2 种颜色：37 个 `(232,239,245)`、3 个纯白。**

### 8.3 所以「所有槽一个外观」是源数据的性质

**不是管道简化。原游戏就是「一张图集 + 近乎统一的材质参数」，视觉差异全在 UV 区域。**

### 8.4 两个新坑

| 编号 | 内容 |
| --- | --- |
| **#105** | 面组材质索引被合并 —— 40 个材质变 1 个槽 |
| **#106** | 「改了但画面没变」：先分清是没生效还是没有可见差异 |

**#106 的方法：把被改的量**读出来**看数值，不要靠画面判断 —— 画面是间接证据。**

---

**总览更新至第 39 轮。共 34 篇文档、106 条坑、144 次提交。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 八、第 37–38 轮的补充" in text:
        print("already present")
        return

    changed = 0
    for old, new in ((OLD_VERIFIED, NEW_VERIFIED),
                     (OLD_UNVERIFIED, NEW_UNVERIFIED),
                     (OLD_INVENTORY, NEW_INVENTORY)):
        if old in text:
            text = text.replace(old, new)
            changed += 1

    text = text.rstrip("\n") + "\n" + ADDENDUM
    open(PATH, "w", encoding="utf-8").write(text)
    print("replaced %d section(s) and appended the addendum" % changed)
    print("file now %d bytes" % len(text))


if __name__ == "__main__":
    main()
