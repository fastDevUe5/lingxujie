# 灵虚界（LingXuJie）

修仙题材 3D MMO 原型，UE 5.8.4 + C++ + 编辑器 Python。**当前阶段：P0 单机垂直切片骨架**。

## 现状

- [x] C++ 模块 + GameMode 骨架，可编译
- [x] 关卡由 `Tools/build_level.py` 生成（石台、灵门、石柱、灵气环、灯光）
- [x] 工具链从 CoinRush 继承：构建 / 测试 / 打包 / 打包验证 / 发布 zip
- [ ] 修炼与境界系统（炼气 → 筑基）
- [ ] 法术与战斗
- [ ] 联机（Dedicated Server + 复制）
- [ ] 持久化（账号 + 数据库）

## 操作

| 键 | 功能 |
| --- | --- |
| WASD / 方向键 | 移动（相机相对） |
| 鼠标 / Q E | 转视角 |
| Space | 跳跃；空中按住 = 御剑滑翔 |
| Shift | 冲刺 |
| Ctrl / C | 闪避冲刺 |
| J / 鼠标左键 | 普攻 |
| 1 / 2 | 剑诀 / Qi Burst |
| Esc | 退出 |

进度与下一步见 [`Docs/P0-ROADMAP.md`](Docs/P0-ROADMAP.md)。

## 命令

```powershell
# 编译 + 重新生成关卡
powershell -ExecutionPolicy Bypass -File Tools\BuildAll.ps1

# 只重新生成关卡
powershell -ExecutionPolicy Bypass -File Tools\BuildLevel.ps1

# 跑游戏（编辑器 -game 模式，1 分钟后自动截图）
powershell -ExecutionPolicy Bypass -File Tools\RunGame.ps1 -Seconds 20

# 自动化测试
powershell -ExecutionPolicy Bypass -File Tools\RunTests.ps1

# 打包 Shipping + 验证 + 发布 zip
powershell -ExecutionPolicy Bypass -File Tools\Package.ps1 -Config Shipping
powershell -ExecutionPolicy Bypass -File Tools\VerifyPackage.ps1
powershell -ExecutionPolicy Bypass -File Tools\MakeRelease.ps1 -Version v0.0.1
```

## 目录

```
Source\LingXuJie\        C++ 模块（LXJGameMode 等）
Tools\                   构建 / 关卡生成 / 测试 / 打包脚本
Docs\                    UE5 踩坑与机制笔记（继承自 CoinRush 工程）
Config\                  默认地图、GameMode、渲染开关
```

## 约定

见 `AGENTS.md`。关键几条：编译前关闭编辑器、`.ps1` 只用 ASCII、二进制资产走 LFS、
改到玩法必须跑测试。踩坑追加到 `Docs/UE5-Gotchas.md`。
