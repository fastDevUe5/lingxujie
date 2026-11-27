# UE5 学习 · 补读（二）：一次噪声排查，推翻了 Lumen 那篇的结论

> **这一篇是本系列**最重要的一次自我更正**。**
> **我之前写的「户外关掉 Lumen 有 20.45% 像素变化」——**那个 20.45% 主要是云的动画，不是 Lumen**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、起因：`nanite.md` 的硬限制

**`nanite.md`（15 KB，28 节）给出的关键限制：**

### 材质

> **「Nanite supports materials that have their Blend Mode set to Opaque and Masked.
> When an unsupported material type is detected, a default material is assigned to the mesh
> along with a warning showing up in the Output Log」**

**其它：**
- 不支持 Mesh Decals（需要 Translucent）
- 不支持 Wireframe
- Vertex Interpolator / Custom UVs **每像素计算三次**
- Custom expression 节点**可能出瑕疵**（Nanite 没有解析导数支持）

### 渲染（明确「不支持」列表）

```
Minimum Screen Radius 过滤
Distance culling          ← 距离剔除对 Nanite 网格不生效
Forward Rendering
VR 立体渲染
MSAA
Lighting Channels         ← 光照通道不生效
对 Nanite 网格做光追      → 默认走 Fallback Mesh
```

**→ `r.RayTracing.Nanite.Mode 1` 是实验性的 Nanite 原生光追。**

---

## 二、✅ 一个**否定结果**：项目没撞到材质规则

**搜日志 `Nanite.*unsupported material` / `Warning.*Nanite`：**
```
→ 只有 LogNanite 类别注册、我自己的 Python 探针、r.Nanite.MaterialOverrides="1"
→ 没有「不支持材质 → 换默认材质」的告警
```

**→ 那 101 个网格的 WorldGridMaterial **不是** blend mode 规则造成的，
就是普通的「材质槽没赋值」（与 MAT-03 诊断一致）。**

**→ 一条假设被排除了，这本身有价值。**

---

## 三、🔴🔴 然后是意外的重大发现：**噪声底**

### 3.1 起因是一次**失败的脚本**

**我写了个关 Nanite 的脚本，但 `get_editor_world()` 返回 `None`（关卡刚加载完），
`execute_console_command` 抛了 `Failed to convert parameter 'world_context'`。**

**→ CVar 根本**没改**。但两次截图仍然差 **9.08%**。**

**→ 什么都没改却差 9%，说明**存在噪声**。**

### 3.2 量准噪声底：连拍三张，什么都不动

```
shot_noise1 vs shot_noise2:  5.40%
shot_noise2 vs shot_noise3:  5.96%
shot_noise1 vs shot_noise3:  7.66%
```

**→ **噪声底 5.4% – 7.7%**。**

### 3.3 找噪声源：藏掉体积云

```python
r.VolumetricCloud 0
```

**再连拍三张：**
```
shot_nc1 vs shot_nc2:  0.36%
shot_nc2 vs shot_nc3:  0.24%
```

**→ **噪声从 5.4–7.7% 降到 0.24–0.36%，降了约 20 倍。****

**→ **体积云在动，那就是噪声源。****

---

## 四、🔴 重测 Lumen：**0.18%**

**在「藏云」这个干净条件下，重做 Lumen 开/关对比：**

```
pixels differing by more than 8: 1,424 (0.18%)
mean absolute channel delta: 0.477
VERDICT: the two captures are effectively identical at this threshold
```

**→ **Lumen 在这个场景里的实际贡献是 0.18% —— 低于 0.24–0.36% 的噪声底，等于看不见。****

### 4.1 对照表

| 条件 | 差异 | 噪声底 | 判定 |
| --- | --- | --- | --- |
| **有云 + Lumen 开关**（SCENE-02 那次）| **20.45%** | 5.4–7.7% | ❌ **归错了** |
| **无云 + Lumen 开关**（本次）| **0.18%** | 0.24–0.36% | ✅ **Lumen 几乎无贡献** |

**→ 那 20.45% 里，绝大部分是**两次截图之间云飘过去**造成的。
→ Lumen 只占 0.18%。**

---

## 五、🔴 为什么 Lumen 在户外反而没贡献

**这不反直觉 —— 看这个场景的光是从哪来的：**

| 光源 | 类型 |
| --- | --- |
| `DirectionalLight` | **直接光** |
| `SkyLight`（**real time capture**）| **天光，直接采样天空** |
| **Lumen GI** | 间接反弹 |

**→ 场景的天光由 **SkyLight 的实时捕获**提供，不依赖 Lumen。
→ 地面和物体的反弹光量很小（大部分是平板地面 + 几个孤立形体）。**

**→ 所以 Lumen 在这个场景里确实**没什么可做的**。**

**⚠️ 这**不**说明「Lumen 没用」—— 说明**这个场景不需要它**。
在封闭室内、有复杂几何互动时，Lumen 才是主力（那正是 LUMEN 系列验证过的场景）。**

---

## 六、🎯 这一篇最重要的三条教训

**1. 🔴 对照实验必须控制**所有**变量，包括「动的背景」。**
**体积云是动画的**，我在做 Lumen 对比时把它当成了常量。
**→ 任何「开关 A 看差异」的实验，先确认画面里**没有别的在动**。**

**2. 🔴 先量噪声底，再谈差异。**
没有噪声底，「20.45%」这个数字**无法解释**。
有了噪声底，才知道 0.18% 是**低于底噪**、20.45% 是**远高于底噪但归因错了**。

**3. 🎯 一次失败的脚本（`get_editor_world()` 返回 None）反而暴露了噪声。**
如果我当时忽略了那个异常，就会以为「Nanite 关掉差 9%」，**又是一个错误结论**。**

---

## 七、更正

| 之前（SCENE-02）| 现在 |
| --- | --- |
| 「户外关掉 Lumen 有 **20.45%** 像素变化」 | ❌ **那 20.45% 主要是云的动画** |
| 「Lumen 在户外作用明显」 | ❌ **实际贡献 0.18%，低于噪声底** |
| 「像素对比是可靠判据」 | ⚠️ **必须先量噪声底、必须冻结动画元素** |

**→ SCENE-02 的那一条结论作废。**

---

## 八、`nanite.md` 这一篇本身学到什么

**1. 材质只支持 Opaque / Masked，否则换默认材质 + 日志告警。**
✅ 本项目没触发过 → 排除一条假设。

**2. `Distance culling` 和 `Lighting Channels` 对 Nanite 网格**不生效**。**
→ 想按距离卸载 Nanite 网格，得用别的办法（关卡流送 / HLOD）。

**3. Nanite 网格的光追走 Fallback Mesh**，除非开 `r.RayTracing.Nanite.Mode 1`。

**4. `Fallback Relative Error` 调低 → fallback 用更多源三角形。**

---

## 九、还没做到

| 项 | 说明 |
| --- | --- |
| 真正的 `r.Nanite 0/1` 对比 | 脚本因世界未就绪失败，**没做成** |
| 关掉云后的 `r.Nanite` 对比 | 同上 |
| 用「藏云 + 多帧平均」建立可靠流程 | 值得封装成工具 |

**→ 下一步应该把「藏云 + 噪声底」做成标准流程，再重做所有像素对比（包括 Nanite）。**

---

## 十、状态

**⚠️ 编辑器已还原：`r.VolumetricCloud 1`、`r.Lumen.DiffuseIndirect.Allow 1`、主关卡 116 actor、视口复位。**
**补读进度：2 / 57。**
