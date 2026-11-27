# UE5 学习 · 补读（二十七）：Enhanced Input 实操 —— 打通了

> **上一轮的结论是「只懂概念，一次没实操」。**
> **这一轮把洞补上了：`InputAction` + `InputMappingContext` + 按键映射，全在 Python 里建成并保存。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、先探 API（本轮关键的一步）

```
InputAction                    True
InputMappingContext            True
InputActionValue               True
PlayerMappableKeySettings      True
InputActionFactory             False    ← 没有工厂
InputMappingContextFactory     False    ← 没有工厂
```

**→ 两个类都在，但**都没有工厂**。**
**→ 按以往经验，「没有工厂 = `create_asset` 建不出来」。**

### 1.1 但我先枚举了属性，而不是直接下结论

**`InputAction` 的可读写属性：**
```
value_type                <InputActionValueType.BOOLEAN: 0>
consume_input             True
accumulation_behavior     <InputActionAccumulationBehavior.TAKE_HIGHEST_ABSOLUTE_VALUE: 0>
action_description        Text("")
```

**`InputMappingContext` 的可读写属性：**
```
mappings                  <Array>       ← 可读可写！
default_key_mappings
mapping_profile_overrides
```

**→ `mappings` 是**可写的数组** —— 说明能往里塞映射。**

---

## 二、🎯 关键发现：`create_asset(..., None)` 能建

**尝试了两条路：**

```
None-factory     -> 'IA_LabJump'      ✅ 成功
context          -> 'IMC_Lab'         ✅ 成功
```

**→ 把工厂参数传 **`None`**，`AssetTools.create_asset` 照样能建出这些 UObject 子类！**

```python
action = asset_tools.create_asset("IA_LabJump", "/Game/Learning", unreal.InputAction, None)
context = asset_tools.create_asset("IMC_Lab",    "/Game/Learning", unreal.InputMappingContext, None)
```

**→ 这推翻了我之前的假设「没有工厂就建不了」。**
**→ 正确的判据不是「有没有工厂」，而是「`create_asset` 接不接受 None」。**

---

## 三、🎯 完整链条（✅ 分两步打通）

### 3.1 第一步：建两个资产并设值

```
None-factory     -> 'IA_LabJump'
value type <InputActionValueType.BOOLEAN: 0>, consume True
context -> 'IMC_Lab'
mappings array initially: 0
mapping construction failed: "EnhancedActionKeyMapping: Failed to convert type 'NoneType' to property 'Key'"
```

**→ 资产建成了，值也设上了。**
**→ 只有「键」失败 —— 因为我用了不存在的 `unreal.InputCoreTypes.get_key()`。**

### 3.2 第二步：正确的 FKey 构造方式

**探到的：**
```
unreal.Key 存在
Key members: ... key_name ...
Key('SpaceBar')  → 失败（call() takes at most 0 arguments）
```

**→ `unreal.Key()` **不接受参数**，但**有 `key_name` 属性**。**

```python
key = unreal.Key()
key.set_editor_property("key_name", unreal.Name("SpaceBar"))
```

**✅ 实测：**
```
key_name set to Name("SpaceBar")
mapping key = Name("SpaceBar")
```

### 3.3 第三步：塞进数组并保存

```python
mapping = unreal.EnhancedActionKeyMapping()
mapping.set_editor_property("action", action)
mapping.set_editor_property("key", key)

mappings = context.get_editor_property("mappings")
mappings.append(mapping)
context.set_editor_property("mappings", mappings)
```

**✅ 实测：**
```
mappings now: 1
  action IA_LabJump   key Name("SpaceBar")
saved
```

---

## 四、🎯 完整可复用配方

```python
# 1. 建 InputAction（无工厂，传 None）
action = asset_tools.create_asset(
    "IA_LabJump", "/Game/Learning", unreal.InputAction, None)
action.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
action.set_editor_property("consume_input", True)

# 2. 建 InputMappingContext
context = asset_tools.create_asset(
    "IMC_Lab", "/Game/Learning", unreal.InputMappingContext, None)

# 3. 造一个键（Key 不接受构造参数，只能设 key_name）
key = unreal.Key()
key.set_editor_property("key_name", unreal.Name("SpaceBar"))

# 4. 造一条映射
mapping = unreal.EnhancedActionKeyMapping()
mapping.set_editor_property("action", action)
mapping.set_editor_property("key", key)

# 5. 追加并保存
mappings = context.get_editor_property("mappings")
mappings.append(mapping)
context.set_editor_property("mappings", mappings)

unreal.EditorAssetLibrary.save_asset("/Game/Learning/IA_LabJump")
unreal.EditorAssetLibrary.save_asset("/Game/Learning/IMC_Lab")
```

**→ 这份配方**是本轮最有价值的产出** —— 以后建输入资产可以直接抄。**

---

## 五、这一篇学到什么

**1. 🎯 **没有工厂 ≠ 建不了资产**。**
`create_asset(..., None)` 对 UObject 子类有效。
**→ 判据应该是「试一下」，不是「看有没有工厂」。**

**2. 🎯 `unreal.Key()` **不接受构造参数**，但 `key_name` 可写。**
键名用 `unreal.Name("SpaceBar")`。

**3. 🎯 `EnhancedActionKeyMapping` 的两个字段是 `action` 和 `key`。**
`key` 的类型是 `FKey`（`unreal.Key`），不是字符串。

**4. 🔴 我一开始用了 `unreal.InputCoreTypes.get_key()`，那个类根本不该那样用。**
**→ 又验证了「先枚举，再写代码」的重要性。**

**5. ✅ Enhanced Input 的**资产层**我摸过了。
→ 上一轮「只懂概念」的洞，补上了这一半。**

---

## 六、更正

| 之前（补读-25）| 现在 |
| --- | --- |
| 「Enhanced Input 一次没实操」 | ✅ **资产层已实操：Action + Context + 按键映射全建成** |
| 「没工厂就建不了资产」 | ❌ **传 None 就能建** |

---

## 七、还没做到（这一半仍然是空的）

| 项 | 说明 |
| --- | --- |
| **运行时绑定** | `AddMappingContext` + 绑委托，需要 C++ 或蓝图 |
| **在 PIE 里按键真的触发** | 需要把 Context 挂到 PlayerController 上 |
| **Input Modifier / Trigger 的实例** | 只建了 Action 和 Mapping，没加 Modifier/Trigger |
| **PMI 玩家重绑定配置** | 没建 |

**→ 但「能建出资产」是从 0 到 1 的一步，之前是 0。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-INPUT2.md   1 篇（共 42 篇 learn 文档）
补读进度：28 / 57
新资产：/Game/Learning/IA_LabJump、/Game/Learning/IMC_Lab（保留作证据）
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 29 篇）。下一批：**
- `blueprints.md`（21.4 KB）
- `python-scripting.md`（32.6 KB）—— 我天天在用，应该有大量可核实的
- `unreal-mcp.md`（31.4 KB）
- `data-tables.md` / `savegame.md`

**→ 选 `python-scripting.md`（32.6 KB）—— 这是我最该"学精"的一篇，
因为我整个系列都在用它，但从来没读过它的官方文档。**
