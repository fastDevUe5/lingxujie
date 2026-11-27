"""Add the component-property gotcha and point the index at the physics document.

    python Tools/add_physics_gotcha.py
"""

GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ENTRY = """
## 76. 遍历 PrimitiveComponent 时不能假设都有仿真属性

- **症状**：用 `get_components_by_class(unreal.PrimitiveComponent)` 拿到组件后逐个读
  `simulate_physics`，撞到 `ArrowComponent` 抛异常：
  `ArrowComponent: Failed to find property 'simulate_physics'`
- **根因**：`ArrowComponent` 确实继承 `PrimitiveComponent`，但不带任何仿真设置。
  同类还有 `BillboardComponent`、`DrawFrustumComponent` 等辅助组件
- **修法**：写一个安全取值函数，读不到就返回默认值
  ```python
  def safe(component, name, default=None):
      try:
          return component.get_editor_property(name)
      except Exception:
          return default
  ```
- **出处**：2026-11-26，物理状态审计
"""

OLD_INDEX = "| **物体没碰撞 / 射线打不中** | **`Docs/UE5-COLLISION.md`** | Enabled / 通道 / Response 三组正交 |"
NEW_INDEX = (
    "| **物体没碰撞 / 射线打不中** | **`Docs/UE5-COLLISION.md`** | Enabled / 通道 / Response 三组正交 |\n"
    "| **物体不会掉 / 没有物理仿真** | **`Docs/UE5-PHYSICS.md`** | 查询 vs 仿真两半分；**本项目零仿真** |"
)


def main():
    text = open(GOTCHAS, encoding="utf-8").read()
    if "## 76." in text:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(ENTRY)
        print("added gotcha 76")

    index = open(INDEX, encoding="utf-8").read()
    if OLD_INDEX in index and "UE5-PHYSICS" not in index:
        index = index.replace(OLD_INDEX, NEW_INDEX)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already split or not found")


if __name__ == "__main__":
    main()
