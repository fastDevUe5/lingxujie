# UE5 学习 · 补读（三十三）：数据表与存档 —— 项目两条都刻意没走

> **两篇文档讲的是「把数据放在资产里」和「把状态存到盘上」。**
> **实测：本项目一条是**刻意**不走的（源码注释说明了理由），另一条**完全没有**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、data-tables.md（8.7 KB，8 节）

```
Data Driven Gameplay Elements
**Data Tables**            ← 一组相关数据
Data Table Importing Process（**CSV**）
**Data Curves**            ← 只支持浮点
**Curve Tables**           ← 二维数值数据
Curve Table Importing Process
Data Hookup                ← 蓝图暴露变量 + handle 结构体
Data Usage (C++)
```

**核心机制：**
- **DataTable 从 CSV 导入**（不是直接编辑）
- **DataCurve 只支持 float**
- **CurveTable 是二维数值**
- 用的时候需要：**蓝图暴露一个变量** + **一个 handle 结构体**

**→ 关键点：DataTable 是**资产**，数据在`.uasset`里，不在代码里。**

---

## 二、savegame.md（12.2 KB，13 节）

```
Creating a SaveGame Object（基于 **USaveGame**）
Header / Source
**Saving**
  **Asynchronous Saving** ← 「AsyncSaveGameToSlot is the recommended method」
  Synchronous Saving（SaveGameToSlot，只适合小存档）
  Binary Saving（SaveGameToMemory）
**Loading**
  Asynchronous Loading（AsyncLoadGameFromSlot）
  Synchronous Loading（LoadGameFromSlot）
  Binary Loading（LoadDataFromSlot）
```

**🎯 文档最明确的一条建议：**
> **「**`AsyncSaveGameToSlot` is the recommended method for saving the game.**」**

**→ 同步版只适合「小存档 formats」和特殊场景。**

---

## 三、✅ 本项目实测：两条都没走

### 3.1 零 DataTable / CurveTable / SaveGame 资产

```
/Game 下 DataTable / CurveTable / CurveFloat / CurveVector / SaveGame 资产：0 个
```

**→ `unreal.DataTable` 和 `unreal.SaveGame` 类都可用，但项目一个资产都没建。**

### 3.2 🎯 物品表**刻意**放在代码里（源码注释原文）

```cpp
// Source/LingXuJie/LXJItems.h:1-3
// Item catalog + drop tables for the P0 slice.
// Kept in code (not a DataTable asset) so drops are unit-testable and the level generator
// does not have to author data.
```

**→ 两个理由，都成立：**

| 理由 | 说明 |
| --- | --- |
| **1. drops are unit-testable** | 数据在 C++ 里 → 单元测试可以直接读，不用加载资产 |
| **2. the level generator does not have to author data** | `build_level.py` 生成关卡时不用去建 DataTable 资产 |

**→ 而且这条注释说明：**写代码的人**考虑过** DataTable，并**明确拒绝了**。**
**→ 这不是疏忽，是权衡。**

### 3.3 数据在代码里的形式

```cpp
UENUM()
enum class ELXJItemType : uint8 { Material, Weapon, Armor };

USTRUCT()
struct FLXJItemStack {
    UPROPERTY() FName ItemId;
    UPROPERTY() int32 Count = 0;
};

/** Static definition of an item (**not reflected**: only the stack is saved/exposed). */
struct FLXJItemDef {     // ← 注意：不是 USTRUCT
    FName Id;
    FString DisplayName;
    ...
};
```

**🔴 一个值得注意的设计细节：**
- **`FLXJItemStack` 是 `USTRUCT`**（有 `UPROPERTY`）→ 可反射、可序列化
- **`FLXJItemDef` **不是** `USTRUCT`** → 不可反射、不可序列化

**→ 注释解释了：「not reflected: only the stack is saved/exposed」**
**→ 即：**物品的**静态定义**不需要存盘，只有**背包里的堆叠**需要。**
**→ 这是**有意的内存/序列化边界**：75 行头文件里区分了「要存盘的」和「不要存盘的」。**

### 3.4 完全没有存档系统

**→ 没有 `USaveGame` 子类，没有 `SaveGameToSlot` 调用，没有存档槽概念。**

**→ 对 P0 单机垂直切片，这是**已知的未做项**（不是做错了）。**

---

## 四、🎯 DataTable 的取舍（把两篇文档和项目对照）

| 维度 | DataTable 资产 | **代码（本项目选择）** |
| --- | --- | --- |
| **改数据要不要重新编译** | ❌ 不用 | ✅ **要** |
| **能不能给策划改** | ✅ 能（编辑器里改 CSV）| ❌ 不能 |
| **单元测试能不能直接读** | ❌ 要加载资产 | ✅ **能** |
| **关卡生成要不要建资产** | ❌ 要 | ✅ **不用** |
| **热重载** | ✅ 支持 | ❌ 要重编译 |
| **版本控制的 diff** | CSV 文本，可读 | C++ 代码，可读 |

**→ 对**P0 单机 + 数据量小 + 强调可测**的项目，代码更好。**
**→ 对**数据量大 + 策划频繁改**的项目，DataTable 更好。**

**→ 这条边界值得记住：**DataTable 的价值在「非程序员能改」。**
**→ 这个项目目前不需要那个价值。**

---

## 五、这一篇学到什么

**1. 🎯 DataTable 是**资产**，从 **CSV 导入**，编辑不在代码里。**
**→ 核心价值是「策划能改」，不是「性能更好」。**

**2. 🎯 `AsyncSaveGameToSlot` 是文档推荐的保存方式，同步版只适合小存档。**

**3. 🔴 本项目**刻意**不用 DataTable，源码注释给了两个理由：**
**可单元测试 + 关卡生成不用建数据资产。**

**4. 🎯 项目在物品定义里**区分了「可序列化」和「不可序列化」**：
`FLXJItemStack` 是 USTRUCT，`FLXJItemDef` 不是。**
**→ 注释写明「not reflected: only the stack is saved/exposed」。**

**5. 🔴 项目**完全没有存档系统** —— 这是已知未做项，不是错误。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「数据应该放 DataTable 才规范」 | ❌ **代码里也可 行，且可测性更好** |
| 「物品表没做成 DataTable 是欠债」 | ❌ **是**刻意**选择，注释说明了理由** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **建一个 DataTable 资产实操** | **可以做**（导入 CSV），但没有真实数据 |
| `AsyncSaveGameToSlot` 实测 | 项目没存档系统，无对象可存 |
| CurveTable | 没试 |
| Data Hookup（蓝图变量 + handle）| 没试 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-DATA.md   1 篇（共 45 篇 learn 文档）
补读进度：34 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 23 篇）。下一批：**
- `blueprints.md`（21.4 KB）
- `sequencer-editor.md`（14.4 KB）
- `geometry-scripting.md`（10.4 KB）
- `fbx-static-mesh.md`（16.1 KB）
- `asset-management.md` — 已读（补读-17 合并）

**→ 选 `blueprints.md`（21.4 KB）—— 项目明确「蓝图只做胶水」，值得读它为什么。**
