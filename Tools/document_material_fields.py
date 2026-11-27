"""Record what the material blocks actually contain beyond the texture name.

Forty material blocks, one texture name, and two colour values between them - thirty-seven use a
near-white and three are pure white. That settles the question of whether per-part appearance was
being lost: it was not. The original describes one atlas sampled at different UV regions.

    python Tools/document_material_fields.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 二十四、材质块里到底有什么（第 38 轮）

### 24.1 字段布局

```
MAT @28 前 64 字节:
  00000000  <- dwIndex = 0
  e8eff500  <- 颜色 1 = (232, 239, 245)
  e8eff500  <- 颜色 2 = (232, 239, 245)
  ffffff00  <- 颜色 3 = (255, 255, 255)
  00000000
  cccccc3d  <- float 0.100
  ...
  偏移 156  <- 贴图名 'boss_mob01.tga'
```

### 24.2 🔴 40 个材质只有 2 种颜色

```
材质块数: 40
不同 (c1,c2,c3,f4) 组合: 2

  (232,239,245) (232,239,245) (255,255,255) f4=0.100  × 37 个材质
  (255,255,255) (255,255,255) (255,255,255) f4=0.100  ×  3 个材质
```

**37 个是略带蓝的白色，3 个是纯白，**`f4` 全部 0.100。**

### 24.3 所以「所有槽一个外观」是**源数据的真实情况**

**不是管道简化，是原游戏就这么做的：**
- 一张图集 `boss_mob01.tga`
- 40 个材质块引用同一张图
- 颜色几乎一致
- **视觉差异全部来自 UV 区域**

> **我原来怀疑「多材质信息被丢了，所以看起来一样」。
> 实际是「信息没丢，源数据本来就没差异」。**

**这两件事在画面上完全无法区分 —— 只有读出来才能分辨。**

### 24.4 材质管线的最终判定

| 环节 | 状态 |
| --- | --- |
| `.mod` 材质块解析 | ✅ 贴图名 + 颜色 + 参数都读到 |
| 贴图名 → 文件 | ✅ 三种扩展名（tif/dds/tga）都试 |
| DDS → PNG | ✅ Pillow 转，绕开 UE 的 DXGI 拒绝 |
| PNG → UE Texture2D | ✅ 512×512 |
| Texture → Material | ✅ `M_Boss_Mob01` |
| 面组 → 材质槽 | ✅ 40 槽（第 37 轮）|
| 按槽赋值 | ✅ 40/40 成功 |

**六个环节全通。**「看起来一样」是源数据的性质，不是缺陷。**

### 24.5 一个可用的判断规则

> **「改了一处但画面没变」时，先问：
> 是**改动没生效**，还是**改了的东西本来就没有可见差异**？**
>
> **判断方法：把被改的量**读出来**看数值差异。**
> 这次读出来是 37:3 且颜色差 23/16/10 —— 差异存在但极小，属于后者。

**这和 gotcha #80（报告数字前先问三件事）是同一套思路的延伸。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 二十四、材质块里到底有什么" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
