"""
module/ui_loader.py
    UI 파일을 PY로 자동 변환한후 읽어온다
    PY로 변환작업을 거치지 않으면 IDE의 자동 완성 기능이 활성화 되지 않는다
    EX) uic.loadUiType(your_ui)[0] => 자동 완성이 제대로 작동하지 않음!! - 런타임에 불러오기 때문에 정적 분석 불가
    출처 : https://stackoverflow.com/questions/58770646/autocomplete-from-ui
"""

from distutils.dep_util import newer
import os


def compile_ui_to_py(ui_dir: str, ui_to_py_dir: str) -> None:
    encoding = "utf-8"

    # UI 파일이 존재하지 않으면 아무 작업도 수행하지 않는다.
    if not os.path.isfile(ui_dir):
        print("The required file does not exist.")
        return

    # UI 파일이 업데이트 됬는지 확인하고, 업데이트 되었으면 *.py로 변환한다
    if not newer(ui_dir, ui_to_py_dir):
        # print("UI has not changed!")
        pass
    else:
        print("UI changed detected, compiling...")
        # ui 파일이 업데이트 되었다, py파일을 연다.

        # ui 파일을 py파일로 컴파일한다.
        result = os.popen(f"pyside6-uic {ui_dir} -o {ui_to_py_dir}").read()


def compile_ui_to_py_multi(ui_path: str, compiled_ui_path: str, ui_files: list[str]):
    for ui_file in ui_files:
        ui_dir = os.path.join(ui_path, ui_file)
        ui_to_py_dir = os.path.join(
            compiled_ui_path, f"{os.path.splitext(ui_file)[0]}.py"
        )
        compile_ui_to_py(ui_dir, ui_to_py_dir)
