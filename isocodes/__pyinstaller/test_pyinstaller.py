import subprocess

from PyInstaller import __main__ as pyi_main
import textwrap
import pathlib


# Tests
# =====
# Test out the package by importing it, then running functions from it.
def test_pyi_isocodes(tmp_path: pathlib.Path) -> None:
    app_name = "isocodes_pyinstaller"
    workpath = tmp_path / "build"
    distpath = tmp_path / "dist"
    app = tmp_path / (f"{app_name}.py")

    app.write_text(
        textwrap.dedent(
            """
            import isocodes
            assert isocodes.languages.get(name='Spanish')
            """
        )
    )
    args = [
        # Place all generated files in ``tmp_path``.
        "--workpath",
        str(workpath),
        "--distpath",
        str(distpath),
        "--specpath",
        str(tmp_path),
        str(app),
    ]
    pyi_main.run(args)
    subprocess.run([str(distpath / app_name / app_name)], check=True)
