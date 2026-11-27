# `.mod` → UE 骨骼网格：完整链路验证通过（2026-11-26）

> **结论：`.mod` → glTF → `SkeletalMesh` 全链路跑通并截图验证。**
>
> **这是第 11–15 轮五轮逆向的成果。动画路径从此打开。**

---

## 一、实测结果

### 1.1 导出

```
108_bird.mod: 10 objects (9 bones, 1 meshes)
  vertex_num=146 triangles=190 influence_records=134
  wrote bird.gltf (5485 bytes) and bird.bin (9892 bytes)
  nodes=10 skin joints=9 accessors=7
```

### 1.2 导入（Interchange）

```
LogInterchangeImport: Warning: glTF Mesh Import Warning message: 网格体拥有未指定材质的图元
LogInterchangeEngine: Display: Interchange import completed
```

**生成三个资产：**

| 资产 | 大小 | 类型 |
| --- | --- | --- |
| `SK_Bird.uasset` | 107.55 KB | **SkeletalMesh** |
| `SK_Bird_Skeleton.uasset` | 6.83 KB | **Skeleton** |
| `SK_Bird_PhysicsAsset.uasset` | 11.21 KB | **PhysicsAsset** |

**⚠️ 注意第三项：导入器**自动生成了布娃娃物理资产** —— 这是骨骼网格导入成功的标志。**

### 1.3 验证

```
BIRD: mesh class=SkeletalMesh
BIRD: skeleton class=Skeleton
BIRD: bone count=9              ← 与源文件 9 骨骼精确一致
BIRD: mesh skeleton=SK_Bird_Skeleton
BIRD: bounds box extent=(75.1, 55.5, 68.1)  sphere radius=115.6
```

**骨骼数 9 = 源文件 9。包围盒 75×55×68 cm = 鸟的尺寸。**

### 1.4 放进关卡

![鸟在兰州城](../../Saved/bird_front.png)

**`MX_BIRD_TEST` 在 (9200, -6200, 3820)，缩放 4 倍，画面正上方可见。**

---

## 二、两个导入路径的关键区别（踩过）

### 2.1 ❌ `SkeletalMeshTools.import_file` 不支持 glTF

```
FbxFactory does not support ".gltf" files. Allowed: ['fbx', 'obj'].
```

**它内部**钉死了 FBX 工厂**，所以只认 `.fbx` / `.obj`。**

### 2.2 ✅ `AssetImportTask` 不指定 factory → 走 Interchange

```python
task = unreal.AssetImportTask()
task.filename = ".../bird.gltf"
task.destination_path = "/Game/Moxiang/Skeletal"
task.destination_name = "SK_Bird"
# 不给 factory，让引擎自己选 → Interchange（支持 glTF）
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
```

**这就是为什么之前记录的「`import_asset(factory=None)` 走 Interchange」是对的，
但**工具集里的 `import_file` 不是那条路**。**

### 2.3 还有一个坑：`imported_object_paths` 返回**字符串**不是对象

```
AttributeError: 'str' object has no attribute 'get_name'
```

**要 `unreal.EditorAssetLibrary.load_asset(path)` 再取。**

---

## 三、导出器做了什么（`Tools/export_mod_gltf.py`）

### 3.1 坐标转换

**源：Z 朝上，厘米。**
**glTF：Y 朝上，右手系，米。**

```
position: (x, z, -y) × 0.01
normal:   (x, z, -y)
UV:       (u, 1-v)        ← glTF 原点在左上
```

### 3.2 骨骼权重补齐

**源：每顶点 `bBonesNum` 个影响（1–3 个，可变）。**
**glTF：必须**正好 4 个**。**

```
读 bBonesNum 个 (bone_index, weight)
→ 补 0 到 4 个
→ 归一化（保证和 = 1）
→ 写 JOINTS_0 / WEIGHTS_0
```

### 3.3 骨架层级

**来自 `dwParentObjectIndex`（基类头 +192）：**
```
0xFFFFFFFF = 根
其他值     = 父对象的 dwIndex
```

**实测 `108_bird.mod`：**
```
Bone09 idx=1 parent=0xFFFFFFFF (根) children=1
Bone07 idx=2 parent=1 children=3
Bone04/Bone08/... parent=2
```

**真实的三叉树结构，不需要猜。**

### 3.4 逆绑定矩阵

**当前写的是**单位矩阵** —— 即"绑定姿势 = 节点变换本身"。**
**对静态展示够用；做动画时如果姿态不对，需要算真正的逆绑定矩阵。**

---

## 四、整条链路的现在状态

```
.mod 文件（5,305 个）
   ↓ Tools/export_mod_gltf.py            ✅ 已验证
.gltf + .bin
   ↓ AssetImportTask（未钉 factory）      ✅ 已验证
SkeletalMesh + Skeleton + PhysicsAsset
   ↓ SkeletalMeshActor                    ✅ 已验证
关卡里可见
   ↓ SkeletalMeshTools.import_file(import_animations=True)
动画（待做）
```

**前四步全通。只剩动画。**

---

## 五、下一批要做的

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 现在一次导一个；5,305 个要脚本化 |
| **材质** | 导入警告「未指定材质的图元」—— 要挂上材质 |
| **动画** | `.anm` → glTF animation（帧率仍未知，但不阻塞）|
| **逆绑定矩阵** | 如果动画姿态不对，要算真正的 IBM |

---

## 六、重查命令

```powershell
# 导出
python Tools\export_mod_gltf.py "C:\...\resources\mod\108_bird.mod" "C:\...\Assets\Moxiang\ue_import\bird.gltf"

# 导入（编辑器内）
py "Tools/import_bird_gltf.py"

# 验证
py "Tools/verify_bird_import.py"

# 放进关卡
py "Tools/place_bird.py"
```
