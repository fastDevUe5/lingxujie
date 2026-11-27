"""Append the fifth debugging round.

    python Tools/write_debug_round5.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 62. 调试系列第 5 轮：**渲染 — 改渲染能抓到，改覆盖层抓不到**（2026-11-26 47:00）

### 一、缓冲可视化：24 种，配置驱动

**源码 `BufferVisualizationData.cpp` 38 行：**
```cpp
const FConfigSection* MaterialSection =
    GConfig->GetSection(TEXT("Engine.BufferVisualizationMaterials"), false, GEngineIni);
```
**→ 可选哪些可视化由 ini 决定，不是硬编码。**

**24 种：BaseColor / SceneColor / SceneDepth / WorldNormal / WorldTangent /
Metallic / Roughness / Specular / AmbientOcclusion / MaterialAO / Anisotropy /
Opacity / SubsurfaceColor / ShadingModel / Velocity / CustomDepth / CustomStencil /
CustomDepthWorldUnits / SceneDepthWorldUnits / SeparateTranslucencyRGB /
SeparateTranslucencyA / PreTonemapHDRColor / PostTonemapHDRColor / FinalImage**

**⚠️ 5 种带 `ApplyAutoExposure=true`（SceneColor / FinalImage / PreTonemapHDRColor /
PostTonemapHDRColor / SeparateTranslucencyRGB）—— 亮度被归一化过，不能判绝对亮度。**

### 二、🔴 缓冲可视化的切换**只有菜单，没有控制台命令**

**源码 `EditorViewportClient.cpp` 3280：**
```cpp
void FEditorViewportClient::ChangeBufferVisualizationMode(FName InName) {
    SetViewMode(VMI_VisualizeBuffer);
    CurrentBufferVisualizationMode = InName;
}
```
**→ 状态在视口客户端上，`FName` 类型，不暴露给 Python，也没有命令。
搜遍 `Editor/` 没有 `viewmode` 注册。**

### 三、`vis`（VisualizeTexture）**是**控制台命令

**实测 `vis help` 的输出（权威语法）：**
```
VisualizeTexture/Vis <RDGResourceNameWildcard>:
VisualizeTexture/Vis <RDGResourceName>[@<Version>] [<Mode>] [PIP/UV0/UV1/UV2] [BMP] [FRAC/SAT] [FULL]:
VisualizeTexture/Vis 0                                   ← 关闭
VisualizeTexture/Vis pool [BYNAME/BYSIZE]:               ← 列池
VisualizeTexture/Vis view=[ID/NAME]
```

**`vis pool` 实测输出（本项目）：**
```
16 = (2D 592x344 PF_FloatRGBA RT)        VolumetricRenderTarget.ReconstructDepth  1792 KB
22 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyLight.ConvolvedSkyRenderTarget0       576 KB
23 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyRenderTarget                          576 KB
73 = (2D 296x172 PF_FloatRGBA RT UAV)    VolumetricRenderTarget.SecondaryTracing   448 KB
```

**能看出：体积渲染在跑 / 天光在跑 / **分辨率 592×344** 说明有屏幕百分比缩放。**
**`r.RenderTargetPoolMin = "400"` LastSetBy: Scalability。**

### 四、🔴 关键区分：`vis pool` ≠ `obj list`

| 命令 | 量什么 | 生命周期 |
| --- | --- | --- |
| `obj list` / `memreport` | **UObject 资产** | 持久，磁盘来的 |
| **`vis pool`** | **运行时渲染目标（RDG 池）** | **每帧可能复用** |

**上一轮 `TextureCube 3 个 16.5 MB` 是**资产**；
`vis pool` 里的 `SkyRenderTarget 576 KB` 是**运行时立方图**。
**两者不能相加，也不是同一个东西。****

### 五、🎯 决定性实验：渲染改动**能**被抓到

**A/B 测试（`vis SkyRenderTarget` vs `vis 0`）：**
```
pixels differing by more than 8: 135611 (16.70%)
mean absolute channel delta:   3.386
bounding box of any change:    (0, 0, 1180, 688)
```

**对比上一轮 `stat` 面板的 **0% 像素差**（两张图完全一致）。**

| 调试方式 | 改的是什么 | 能抓吗 |
| --- | --- | --- |
| `stat unit` 面板 | Canvas 覆盖层 | ❌ **0%** |
| **`vis <资源>`** | **场景渲染** | ✅ **16.7%** |

**→ 规则：改**渲染状态**的能截图验证；画**覆盖层**的不能。**
**这条规则直接决定以后怎么验证渲染改动。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-RENDER.md`** | 24 种缓冲 + vis 语法 + A/B 实测 + 可抓性规则 |
| `Tools/practice_render_commands.py` | 跑 `vis help` / `vis pool` / 查 r.* CVar |
| **`Tools/diff_captures.py`** | **像素级 A/B 对比（以后验证渲染改动都用它）** |
| `Tools/vis_on.py` / `vis_off.py` | 开关 vis |

**证据：`Saved/shot_vis.png` vs `Saved/shot_vis_off.png`。**

### 七、新增的通用工具

**`Tools/diff_captures.py` 是本轮最有复用价值的产出：**
```
python Tools/diff_captures.py a.png b.png
→ 差异像素数 / 占比 / 平均通道差 / 变化包围盒 / 判定
```
**以后任何「改了渲染但看不出差别」的问题，都能用它给出**数值**答案，而不是靠眼睛。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **蓝图与脚本调试** —— Python 异常栈、蓝图断点、PIE 调试 |
| 2 | 网络调试 |
| 3 | 资产与加载问题 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 62." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 62; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
