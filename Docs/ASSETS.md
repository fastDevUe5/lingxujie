# 资产台账

> 新会话先看这张表，别再去 Fab 重新找一遍、也别重复下载。

## 1. 已导入工程（`Content/`，可被 Python 按路径加载）

| 包 | 路径 | 内容 | 体积 | 备注 |
| --- | --- | --- | --- | --- |
| KHS 建春门（城门） | `Content/GeonchunmunComplex/` | 444 件模块（墙/门/屋顶/斗拱/柱） | 320 MB | 布局已采集成 `Assets/Gate/geonchunmun_gate.json`；**当前不在生成流程里** |
| KCISA 甫吉岛洗然亭（园林） | `Content/SeyeonjeongPavilion/` | 560 件（亭/驳岸/叠石/树/水） | 3.8 GB | 布局 `Assets/Village/seyeonjeong_layout.json`；**当前不在生成流程里**；贴图到 8K，未压 |
| Megascans 苔石步道 | `Content/Fab/Megascans/...` | 2K 材质 | 小 | 已用于石板铺装 |

⚠️ 这两个大包**没有提交到 git**（`.gitattributes` 走 LFS，但体积太大）。

## 2. 已在 Fab 库（个人档 ¥0，随时可导入）

| 资产 | 角色 | 网格 | 状态 |
| --- | --- | --- | --- |
| KHS Naganeupseong Walled Town | 民居（茅草院屋成组） | 206 | **未导入** |
| KCISA Korean Traditional Smart Materials Vol.1 | 地面材质（砖/石/草/土） | — | 未导入 |
| KCISA Korean Traditional Heritage Props | 道具（罐/灯笼/条凳/农具） | 145 | 未导入 |
| tharlevfx Water Materials | 水面材质 | — | 未导入 |
| KHS House Of Changwon | 院落住宅 | 228 | 未导入 |
| KHS Gwolnaegaksa（官署） | 院落/门楼 | — | 未导入 |
| KHS Soswaewon（园林） | 竹/松/叠石 | 99 | 未导入 |

导入流程：编辑器 Fab 面板 → 拉到右栏「添加到项目」→ 弹「与 5.8 不兼容」选 **5.7**。

## 3. 署名要求（CC-BY，发布时必须写）

- KHS（Korea Heritage Service）系列：`Korea Heritage Service`
- KCISA 系列：`Korea Culture Information Service Agency`
- Megascans / Quixel：Epic Games（Fab 标准许可）

## 4. 参照资料（不是素材，不能进 `Content/`）

`C:/Users/tk/Desktop/moxiang-study/Docs/MoXiang/`（**仓库外，不入库**）：参照截图与逆向资料；
其中 `maps/` 目前只有 3 张（1 张城镇广场、1 张俯视地形、1 张含地图内嵌的宣传图），**世界地图还缺**。
