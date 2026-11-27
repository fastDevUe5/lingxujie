"""Append the thirty-eighth round.

    python Tools/write_round_thirtyeight.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 55. 第三十八轮：**40 个槽全部赋材质 —— 但画面不变**（2026-11-26 39:00）

### 一、关键事实：40 个材质用同一张贴图

**逐块打印 40 个 MATERIAL 块，全部是：**
```
MAT @28     dwIndex=0  size=1444  图: ['boss_mob01.tga']
MAT @1480   dwIndex=0  size=1444  图: ['boss_mob01.tga']
...
```

**不是「每部件一张图」，而是**同一张图集的不同 UV 区域**。**

### 二、赋值成功

```
ALLSLOT: mesh has 40 slot(s)
ALLSLOT: assigned to 40 of 40 slots (0 failed)
```

### 三、🔴 画面**没有变化**

**截图与「只有 1 个槽」时完全相同。**

**因为 40 个槽用同一张图、同一套 UV，渲染结果必然一样。**

### 四、为什么 —— 读出材质块的字段

```
MAT @28 前 64 字节:
  00000000  <- dwIndex
  e8eff500  <- 颜色 1 = (232, 239, 245)
  e8eff500  <- 颜色 2
  ffffff00  <- 颜色 3 = 白
  cccccc3d  <- float 0.100
  偏移 156  <- 贴图名

40 个材质块，只有 2 种颜色组合：
  (232,239,245) × 37 个
  (255,255,255) ×  3 个
  f4 = 0.100 全部相同
```

**源数据就是「一张图集 + 近乎统一的材质参数」。**

### 五、教训（gotcha #106）

> **「改了一处但画面没变」时，先分清：**
> **是改动没生效，还是改了的东西本来就没有可见差异？**
>
> **判断方法：把被改的量**读出来**看数值差异，不要靠画面判断。**
>
> **画面是**间接**证据，数值是直接证据。**

### 六、材质管线最终判定：六段全通

| 环节 | 状态 |
| --- | --- |
| `.mod` 材质块解析 | ✅ 贴图名 + 颜色 + 参数 |
| 贴图名 → 文件 | ✅ 三种扩展名都试 |
| DDS → PNG | ✅ Pillow |
| PNG → UE Texture2D | ✅ 512×512 |
| Texture → Material | ✅ `M_Boss_Mob01` |
| 面组 → 材质槽 | ✅ 40 槽 |
| 按槽赋值 | ✅ 40/40 |

**「看起来一样」是源数据的性质，不是缺陷。**

### 七、这一轮的意义

| 之前 | 现在 |
| --- | --- |
| 40 个材质信息**丢失** | 40 个槽**存在**，每个可独立赋材质 |
| 想给眼睛单独挂图 —— **做不到** | 可以做到（槽 32/31 是眼睛）|

**即使当前源数据不需要多贴图，**信息保真**本身是管道正确的标志。**

### 八、下一轮（剩 2 轮）

| 轮 | 任务 |
| --- | --- |
| 39 | **收口**：更新总览（加第 37/38 轮结论）+ 交叉引用一致性检查 |
| 40 | **最终验收**：跑回归 + 汇总报告 + 目标状态 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 55." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 55; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
