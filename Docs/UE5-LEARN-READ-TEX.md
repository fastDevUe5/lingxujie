# UE5 学习 · 补读（十一）：贴图 —— 三条规则审出项目里一张问题资产

> **文档给了三条硬规则，拿它们审了 813 张贴图，**审出一张同时踩四个问题的**。**
> **⚠️ 那是导入的墨香资产，不是我的文件 —— 只诊断，没动它。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、material-editor-guide.md（7.6 KB，6 节）

```
Material Creation Workflow
Creating a new Material
Using the Material Editor
Live Update Options
Compiler Errors
Material Graph Search
```

**→ 这是一篇**界面操作指南**（怎么建材质、怎么看编译错误、怎么搜节点），
没有可验证的硬事实。**这一篇我已在 MAT-01~03 用实操覆盖过了**（从零建材质、实例、Nanite override）。

---

## 二、texture-asset-editor.md（30 KB，32 节）—— 这篇有硬事实

### 2.1 🎯 三条硬规则

> **「Non-power of 2 textures support mip maps.
> **However, power of 2 textures is still required in order for them to texture stream.**
> **The top mip map level must be a multiple of 4 in order to use texture compression.**
> Non-power of 2 textures have their Mip Gen Settings **automatically set to NoMipMap** at time of import.」**

**拆成三条：**

| # | 规则 |
| --- | --- |
| **1** | **非 2 次幂**不能**纹理流式** |
| **2** | **顶层 mip 必须是 4 的倍数**才能用**压缩** |
| **3** | **非 2 次幂导入时自动 `NoMipMap`** |

**→ 3489 是**奇数**，违反 1 和 2。**

### 2.2 BC6 / BC7 的定量事实

| 格式 | 相对大小 | 说明 |
| --- | --- | --- |
| **BC6H** | **比 RGBA16F 小 8 倍** | HDR 压缩，应优先于未压缩 HDR |
| **BC7（无 alpha）** | **BC1 的 2 倍字节** | 质量更高，适合通道打包的图 |
| **BC7（带 alpha）** | **与 BC3 同样大小** | 同尺寸下质量更高 |

**→ 文档还说：「We do not recommend changing existing BC3 usage habits to BC7 at this time」**
—— 不推荐全面改用 BC7，只对特定贴图有意义。**

---

## 三、🎯 审计 813 张贴图

### 3.1 审计结果（✅）

```
Texture2D assets in /Game: 813
非 2 次幂: 1
  T_GCM_Ceiling_BC     3489 x 4096
2 次幂但顶层 mip 不整除 4: 0
```

**→ 813 张里 **812 张合规**，只有 1 张违规。**

### 3.2 🔴 那一张的问题不止一个

```
路径: /Game/GeonchunmunComplex/Textures/Decals/T_GCM_Ceiling_BC
尺寸: 3489 x 4096

mip_gen_settings       TMGS_NO_MIPMAPS      ← 无 mip（规则 3 的自动结果）
compression_settings   TC_EDITOR_ICON       ← 编辑器图标压缩！
never_stream           True                 ← 流式显式关闭（规则 1 的后果）
lod_group              TEXTUREGROUP_WORLD
max_texture_size       0
virtual_texture_streaming  False
```

**四个问题叠在一起：**

| # | 问题 | 后果 |
| --- | --- | --- |
| 1 | **3489 不是 2 的幂** | 不能流式 |
| 2 | **奇数尺寸** | **不能压缩** |
| 3 | **`TC_EDITOR_ICON`** | 这是**编辑器图标**压缩模式，不是游戏贴图格式 |
| 4 | **`TMGS_NO_MIPMAPS`** | 无 mip 链 |

### 3.3 显存估算

```
3489 × 4096 = 14,290,944 像素
× 4 字节（RGBA8，因为 TC_EDITOR_ICON 通常不压缩）
= 57,163,776 字节 ≈ 54.5 MB
```

**→ 一张天花板贴花占 **约 55 MB** 显存，且**无 mip**（远处也不降采样）**
**→ 而且**不能流式**（必须常驻）。**

**→ 对比：一张合规的 2048×2048 BC1 带 mip 约 **2.7 MB**。
→ **这一张相当于 20 张正常贴图。**

---

## 四、⚠️ 我没有修改它

**理由：**
1. **它在 `/Game/GeonchunmunComplex/` —— 是导入的墨香素材，不是我的文件**（AGENTS.md 规则 11）
2. 改它属于**资产管线决策**（要不要重采样到 2048、换什么压缩格式），应该是人的决定
3. 重采样会改变画面（贴花会变模糊），**不是我该擅自做的视觉变更**

**→ 正确做法：报告 + 给出选项，等人决定。**

### 4.1 如果要修，三个选项

| 选项 | 做法 | 代价 |
| --- | --- | --- |
| **A. 重采样到 2048×2048** | 改源图尺寸，重新导入 | 画面轻微变糊，**省 ~50 MB** |
| **B. 只改压缩** | `TC_DEFAULT` + 启用 mip | 奇数尺寸**压不了**，无解 |
| **C. 保持不动** | — | 55 MB 显存 |

**→ **必须走 A**。B 不可行，因为奇数尺寸**物理上不能**用块压缩。**
**→ 这也印证了文档那条规则为什么重要：尺寸选错，后面所有优化手段都用不上。**

---

## 五、这一篇学到什么

**1. 🎯 「顶层 mip 必须是 4 的倍数」是一条**物理约束**，不是建议。**
3489 是奇数 → 任何块压缩格式都用不了 → 只剩未压缩。

**2. 🔴 `TC_EDITOR_ICON` 出现在游戏贴图上是个信号。**
它意味着这张图被当成编辑器图标处理（不压缩、可能不生成 mip）。
**→ 通常来自导入时压缩设置没改。**

**3. 🔴 三个问题会连锁：**
奇数尺寸 → 不能压缩 → 不能 mip → `never_stream` 被设上 → **55 MB 常驻显存。**

**4. 🎯 审计是**低成本高回报**的检查。**
遍历 813 张资产的尺寸，只花了不到 3 秒，就定位到唯一的例外。

**5. 🎯 **发现问题和修改问题是两件事**。**
这张图属于导入素材，改它要动画面，**应该由人决定**。

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「贴图导入就是点一下，没什么可管的」 | ❌ **尺寸/压缩/mip/流式四件事各自独立，错一个就浪费几十 MB** |
| 「非 2 次幂只是小瑕疵」 | ❌ **它让压缩和流式**两个手段全部失效** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| 修这张贴图 | **等人决定（会改画面）** |
| 统计 813 张的**总显存** | 没做，值得做 |
| 检查 `TC_EDITOR_ICON` 是否还有别的图 | 只查到这一张（它是唯一的非 2 次幂）|
| BC6/BC7 的实际使用情况 | 没查项目用了哪些压缩格式 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-TEX.md   1 篇（共 34 篇 learn 文档）
补读进度：12 / 57（material-editor-guide 无硬事实，与 texture 合并成一篇）
编辑器：主关卡 116 actor / 视口复位
```

---

## 九、这一篇的结论用一句话

**813 张贴图里 812 张合规，唯一违规的那张因为尺寸是 3489（奇数），
导致压缩、mip、流式三个手段全部失效，白占约 55 MB 显存。**
**我发现了它，但没改它 —— 因为改它会改画面，那是人的决定。**
