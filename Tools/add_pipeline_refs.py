"""Add gotcha 82 and point the index at the pipeline document.

    python Tools/add_pipeline_refs.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRY = """
## 82. `SkeletalMeshTools.import_file` 钉死 FBX 工厂，不支持 glTF

- **症状**：`SkeletalMeshTools.import_file(... source_file='x.gltf')` 报
  `FbxFactory does not support ".gltf" files. Allowed: ['fbx', 'obj'].`
- **根因**：那个工具内部钉死了 FBX 工厂，只认 `.fbx` / `.obj`
- **修法**：用 `AssetImportTask` 不指定 factory，让引擎走 Interchange
  ```python
  task = unreal.AssetImportTask()
  task.filename = '.../x.gltf'
  task.destination_path = '/Game/...'
  task.destination_name = 'SK_X'
  # 不给 factory
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
  ```
- **附带坑**：`task.imported_object_paths` 是字符串列表不是对象，
  要 `EditorAssetLibrary.load_asset(path)` 再取
- **成功的标志**：生成三个资产（SkeletalMesh + Skeleton + PhysicsAsset）
- **出处**：2026-11-26，导入墨香的鸟模型
"""

OLD_INDEX = "| **`.mod` 网格/蒙皮格式** |"
NEW_INDEX = ("| **`.mod` → UE 骨骼网格** | **`Docs/MOD-TO-UE-PIPELINE.md`** | "
             "**全链路跑通**；import_file 不认 glTF |\n"
             "| **`.mod` 网格/蒙皮格式** |")


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 82." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 82")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index and "MOD-TO-UE-PIPELINE" not in index:
        index = index.replace(OLD_INDEX, NEW_INDEX, 1)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already changed")


if __name__ == "__main__":
    main()
