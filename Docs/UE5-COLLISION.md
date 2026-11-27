# UE5 碰撞体系（引擎源码核实）

> **碰撞"不生效"几乎总是一个原因：问的通道和答的通道不是同一个。**
> **本文把三组正交概念拆开，看到就能定位。**

---

## 一、三组正交概念（必须先分清）

**一次碰撞判定涉及三个独立的东西：**

| 概念 | 问题 | 取值 |
| --- | --- | --- |
| **① Enabled** | 这个物体参与碰撞吗？ | `NoCollision` / `QueryOnly` / `PhysicsOnly` / `QueryAndPhysics` |
| **② Object Type** | 这个物体**是什么**？ | `ECC_WorldStatic` / `ECC_Pawn` / … |
| **③ Response** | 对某个通道**怎么反应**？ | `ECR_Ignore` / `ECR_Overlap` / `ECR_Block` |

**判定流程：**
```
查询（比如一条射线）带着「我要问哪个通道」
   ↓
物体回答：我对这个通道是 Ignore / Overlap / Block
   ↓
同时物体自己的 Enabled 必须允许这一类查询
```

**三组都对了才能命中。任一组不对就是"没反应"。**

---

## 二、`ECollisionEnabled`（4 个值，实测）

| 值 | 含义 |
| --- | --- |
| `NoCollision` | **不参与任何碰撞**（连查询都不答） |
| `QueryOnly` | 只答**查询**（射线、重叠），不参与物理模拟 |
| `PhysicsOnly` | 只参与物理，不答查询 |
| `QueryAndPhysics` | **两者都参与** |

**源码里有个辅助函数判断"是否有物理碰撞"：**
```cpp
inline bool CollisionEnabledHasPhysics(ECollisionEnabled::Type C)
{
    return (C == ECollisionEnabled::PhysicsOnly) ||
           (C == ECollisionEnabled::QueryAndPhysics);
}
```

**⚠️ 常见误区：**
**物体看着有碰撞（能挡住人），但射线穿过去了 —— 那是 `PhysicsOnly`。
或者射线打得到，但人不被挡住 —— 那是 `QueryOnly`。**

---

## 三、`ECollisionChannel`（66 个值）

**前 8 个是引擎预留的：**

| 通道 | 典型用途 |
| --- | --- |
| `ECC_WorldStatic` | 静态世界（地形、建筑）|
| `ECC_WorldDynamic` | 动态世界（可移动物体）|
| `ECC_Pawn` | 角色 / 载具 |
| `ECC_Visibility` | **可见性查询**（鼠标点选、视线检测）|
| `ECC_Camera` | 相机碰撞 |
| `ECC_PhysicsBody` | 物理刚体 |
| `ECC_Vehicle` | 载具 |
| `ECC_Destructible` | 可破坏物 |

**然后是：**
```
ECC_EngineTraceChannel1..6       ← 引擎预留的自定义通道（6 个）
ECC_GameTraceChannel1..50        ← 项目自定义通道（50 个）
ECC_OverlapAll_Deprecated
ECC_MAX
```

**所以项目最多能自定义 50 个追踪通道 + 6 个引擎通道。**

**本项目目前用了几个自定义通道？** 见 `DefaultEngine.ini` 的 `[/Script/Engine.CollisionProfile]` 段（未查）。

---

## 四、`ECollisionResponse`（3 个值）

| 值 | 含义 |
| --- | --- |
| `ECR_Ignore` | **穿过**，不阻挡也不触发重叠 |
| `ECR_Overlap` | **穿过，但触发重叠事件** |
| `ECR_Block` | **挡住**，触发阻挡事件 |

**`Ignore` 和 `Overlap` 都是"穿过"，区别在**要不要收事件**。
很多"重叠事件没触发"就是配成了 `Ignore`。**

---

## 五、`ECollisionTraceFlag`（4 个值）—— 网格用哪个碰撞

| 值 | 含义 |
| --- | --- |
| `CTF_UseDefault` | 引擎按网格复杂度自动选 |
| `CTF_UseSimpleAndComplex` | **简单碰撞和复杂碰撞都留** |
| `CTF_UseSimpleAsComplex` | 用简单形状回答复杂查询 |
| **`CTF_UseComplexAsSimple`** | **用三角形网格当简单碰撞** |

### 5.1 这是本项目踩过的坑

**当初地形"角色掉下去"，修法是关 Nanite。更根本的原因在这里：**

```
CTF_UseDefault（默认）
   ↓
地形有复杂碰撞（三角形），但"简单碰撞"是空的
   ↓
角色胶囊体用的是**简单碰撞**
   ↓
掉下去
```

**`CTF_UseComplexAsSimple` 让简单查询用三角形回答 —— 这就是我们后来在
`place()` 里设 `CTF_USE_COMPLEX_AS_SIMPLE` 的原因。**

**对照表：**

| 网格类型 | 该用哪个 CTF | 理由 |
| --- | --- | --- |
| **地形 / 建筑（烘焙网格）** | **`CTF_UseComplexAsSimple`** | 三角形就是碰撞体，最准确 |
| 角色 | `CTF_UseDefault` | 用胶囊体，简单碰撞 |
| 可破坏物 | `CTF_UseSimpleAndComplex` | 两种都需要 |
| 不需要碰撞的装饰 | 直接 `NoCollision` | 省性能 |

---

## 六、`UBodySetup`：碰撞设置的家

**`BodySetup.h` 21,354 字节，关键成员：**

| 成员 | 作用 |
| --- | --- |
| `AggGeom` | **简单碰撞形状集合**（盒 / 球 / 胶囊 / 凸包）|
| `bDoubleSidedGeometry` | 双面几何 |
| `bConsiderForBounds` | 是否计入包围盒 |

**所以"简单碰撞"就是 `AggGeom` 里的那些形状。
空 `AggGeom` + `CTF_UseDefault` = 没有简单碰撞 = 角色掉下去。**

**`generate_convex_collisions` 这个工具就是在**往 `AggGeom` 里填凸包**。**

---

## 七、本项目现状（实测）

```
SM_Lanzhou_Terrain:
  Nanite        = false
  三角形        = 524,288
  碰撞          = CTF_USE_COMPLEX_AS_SIMPLE（在 place() 里设的）
```

**角色能站在地形上 —— `Player ready at V(X=4000.00, Y=-8830.49, Z=3684.00)`。**

**建筑网格**（96 个材质组）**目前的碰撞设置没确认** —— 下次该查：

```python
# 看某个建筑组有没有简单碰撞
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Moxiang/17_jp_roof00.17_jp_roof00")
body = mesh.get_editor_property("body_setup")
print(body.get_editor_property("collision_trace_flag"))
print(len(body.get_editor_property("agg_geom").convex_elems))
```

---

## 八、还没学的

| 主题 | 状态 |
| --- | --- |
| 自定义碰撞通道怎么注册 | 没查（`DefaultEngine.ini`）|
| `PhysicalMaterial`（摩擦/弹性）| 没碰 |
| CCD（连续碰撞检测） | 没碰 |
| 物理约束（Constraint） | 没碰 |
| 布娃娃（PhysicsAsset） | 没碰（但它和骨骼动画相关，做动画时会遇到）|

---

## 九、重查命令

```powershell
python Tools\map_collision.py            # 通道列表
python Tools\find_collision_enums.py     # 三组枚举的取值
```
