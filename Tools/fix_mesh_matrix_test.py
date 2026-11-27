"""Fix the mesh matrix test to use parsed mesh objects directly.

parse_mod already returns the mesh blocks with their positions and node_matrix, so re-reading the
file was both unnecessary and wrong - the payload key does not exist on the parsed object.

    python Tools/fix_mesh_matrix_test.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/test_mesh_matrix.py"

OLD = '        block = exporter.read_mod_mesh(data, mesh["payload"])'
NEW = "        block = mesh"


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("already fixed")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("fixed both call sites")


if __name__ == "__main__":
    main()
