import argparse
from pathlib import Path
from shutil import copy
import xml.etree.ElementTree as ET

XML_DEPS = {
    "gtest": {"ament_cmake_gtest"},
    "pytest": {"ament_cmake_ros", "launch", "launch_ros", "launch_testing", "launch_testing_ament_cmake", "rclpy"},
}

CMAKE_DEPS = {
    "gtest": {"ament_cmake_gtest"},
    "pytest": {"ament_cmake_ros", "launch_testing_ament_cmake"},
}

ISOLATED_HELPER = """function(add_ros_isolated_launch_test path)
  set(RUNNER "${ament_cmake_ros_DIR}/run_test_isolated.py")
  add_launch_test("${path}" RUNNER "${RUNNER}" ${ARGN})
endfunction()
"""


def add_package_xml_dependencies(path: Path, deps: set[str]) -> set[str]:
    """Create dependencies in package.xml if not existing

    Args:
        path (Path): _description_
        deps (set[str]): _description_

    Returns:
        set[str]: _description_
    """
    # Set up XML parser to preserve comments
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(path, parser=parser)
    root = tree.getroot()

    # Find dependencies that are missing
    existing = {e.text.strip() for e in root.findall("test_depend") if e.text}
    missing = deps - existing

    # Find the index to insert new dependencies before the first <export> tag, or at the end if no <export> exists
    export_element = root.find("export")
    index = list(root).index(export_element) if export_element is not None else len(root)

    for dependency in sorted(missing):
        element = ET.Element("test_depend")
        element.text = dependency
        root.insert(index, element)
        index += 1

    # Save changes
    if missing:
        ET.indent(tree, space="  ")
        tree.write(path, encoding="unicode", xml_declaration=True)

    return missing


def setup_cmake(path: Path, kind: str) -> None:
    """Configure CMakeLists.txt to include a generated_tests.cmake which will contain the test registration

    Args:
        path (Path): Path to CMakeLists.txt
        kind (str): Type of test, either "gtest" or "pytest"
    """
    content = path.read_text()

    block = ""
    for dep in sorted(CMAKE_DEPS[kind]):
        if f"find_package({dep} REQUIRED)" not in content:
            block += f"  find_package({dep} REQUIRED)\n"

    if kind == "pytest" and "function(add_ros_isolated_launch_test" not in content:
        block += ISOLATED_HELPER + "\n"

    include = "include(test/generated_tests.cmake)"

    # We check if the include already exists in the CMakeLists.txt.
    # If it does, we add the block before it in the same if(BUILD_TESTING) section.
    # If not, we add the block and the include before ament_package()
    if include in content:
        if not block:
            return
        content = content.replace(include, block + include, 1)
    else:
        block += f"  {include}\n"
        content = content.replace("ament_package()", f"if(BUILD_TESTING)\n{block}endif()\n\nament_package()", 1)

    path.write_text(content)


def register_cmake(path: Path, kind: str, name: str, test_path: Path) -> bool:
    """Register test in CMakeLists.txt

    Args:
        path (Path): Path to CMakeLists.txt
        kind (str): Type of test, either "gtest" or "pytest"
        name (str): Name of the test
        test_path (Path): Relative path to the test file

    Returns:
        bool: True if the test was newly registered or False if already existing
    """
    generated = path.parent / "test" / "generated_tests.cmake"
    generated.parent.mkdir(exist_ok=True)

    # Add the registration command based on gtest or pytest
    registration = f"ament_add_gtest(${{PROJECT_NAME}}_{name} {test_path})" if kind == "gtest" else f"add_ros_isolated_launch_test({test_path})"

    if generated.exists() and registration in generated.read_text():
        return False

    with generated.open("a") as f:
        f.write(registration + "\n")
    return True


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate ROS2 test file")
    parser.add_argument("type", choices=["gtest", "pytest"])
    parser.add_argument("name", help="Name of the test. Use test_<name> for pytest and <name>_test for gtest")
    parser.add_argument("--package-dir", type=Path, default=Path.cwd(), help="Path to the ROS2 package directory. Defaults to current working directory.")
    args = parser.parse_args()

    if args.name.contains(" ") or args.name.contains("/") or args.name.contains("\\"):
        raise ValueError("Test name cannot contain spaces or slashes")

    # Setup paths for all package.xml, CMakeLists.txt, and test file
    package: Path = args.package_dir
    xml = package / "package.xml"
    cmake = package / "CMakeLists.txt"
    (package / "test").mkdir(exist_ok=True)
    extension = ".cpp" if args.type == "gtest" else ".py"
    test_path = package / f"test/{args.name}{extension}"

    if not test_path.exists():
        template = Path(__file__).parent / f"template{extension}"
        copy(template, test_path)

    add_package_xml_dependencies(xml, XML_DEPS[args.type])
    setup_cmake(cmake, args.type)
    register_cmake(cmake, args.type, args.name, test_path.relative_to(package))

    print(f"Created/registered {test_path}")


if __name__ == "__main__":
    main()
