# Gameplay Framework 生命周期（引擎 5.8.4｜核对 2026-11-17｜源码已核对 ✅）

## 一句话结论

独立游戏/PIE 里，**PlayerController、Pawn、HUD 都在 `World::BeginPlay` 之前就创建好了**；
`GameMode::StartPlay()` 的主要职责是“通知世界开始”，而不是“创建玩家”。
所以 `StartPlay` 里可以安全地拿 `GetPlayerPawn`，但构造函数里什么世界状态都不能碰。

## 事实与调用链（均取自本机 5.8.4 源码）

**独立游戏启动顺序**（`Engine/Source/Runtime/Engine/Private/UnrealEngine.cpp` 的 `LoadMap`，约 16616-16660 行）：

1. `World::InitializeActorsForPlay(URL, true, ...)`
2. 为每个本地玩家 `LocalPlayer->SpawnPlayActor(...)`：
   → `UWorld::SpawnPlayActor` → `GameMode::Login` → `PostLogin`
   → `GenericPlayerInitialization()` 里 `InitializeHUDForPlayer(PC)`（`GameModeBase.cpp:978`）
   → `HandleStartingNewPlayer` → `RestartPlayer` → `SpawnDefaultPawnAtTransform` → `Possess`
3. `World::BeginPlay()`：
   - 先遍历 `WorldSubsystem->OnWorldBeginPlay`
   - 再 `GetAuthGameMode()->StartPlay()`（`World.cpp`，`UWorld::BeginPlay`）
4. `AGameModeBase::StartPlay()` 只做一件事：`GameState->HandleBeginPlay()`（`GameModeBase.cpp:204`）
5. `AGameStateBase::HandleBeginPlay()`：`WorldSettings->NotifyBeginPlay()`（**所有 Actor 的 BeginPlay 在这里触发**）+ `NotifyMatchStarted()`（`GameStateBase.cpp:205`）

**PIE 同样如此**：`GameInstance.cpp:538` 在 `InitializeActorsForPlay` 之后、BeginPlay 之前调用 `SpawnPlayActor`。

**`AGameMode`（不是 Base）额外一层**：`StartMatch()` → `SetMatchState(MatchState::InProgress)` →
`HandleMatchHasStarted()` 会给“还没有 Pawn 的 PC”再补一次 `RestartPlayer`，然后再 `NotifyBeginPlay`（`GameMode.cpp:186-230`）。

## 我们工程的取舍

- 用 `AGameModeBase`：本作不需要比赛状态机（WaitingToStart/InProgress），少一层状态就少一类 bug。
- 金币在 `CRGameMode::StartPlay()` 生成——此时 Pawn 已存在、Actor 的 `BeginPlay` 即将开始，两端都安全。
- HUD 不手动 Spawn：`HUDClass` + `InitializeHUDForPlayer` 在登录阶段自动创建（`AGameModeBase::InitializeHUDForPlayer`，`GameModeBase.cpp:889`）。
- 重开关卡用 `UGameplayStatics::OpenLevel`：整套流程重跑一遍，日志会出现第二条 `[CoinRush] Round started`（实测）。

## 反例与坑

- **不要在 GameMode 构造函数里访问 `GetWorld()` / `GetPlayerPawn()`**：构造期是 CDO，拿到的是空。
- **不要在 `StartPlay` 里假设“玩家还没生成”**：独立游戏里已经生成了；但**联机客户端**上 Pawn 可能还没复制过来，做联机时要用 `OnPostLogin`/`OnPossess` 判断。
- **不要依赖 `AGameModeBase::StartPlay` 之后的顺序**去初始化与 Pawn 相关的东西：`NotifyBeginPlay` 里 Actor 的 `BeginPlay` 顺序是不确定的（依赖注册顺序），需要稳定时序就用回调/事件。

## 待复核（升级 5.9 时）

- [ ] `UWorld::BeginPlay` 是否仍先跑 WorldSubsystem 再调 `StartPlay`
- [ ] `LoadMap` 里 SpawnPlayActor 与 BeginPlay 的先后是否变化
- [ ] `InitializeHUDForPlayer` 是否仍挂在 `GenericPlayerInitialization` 上
