import os
import sys

from Cython.Build import cythonize
from setuptools import Extension

PROJECT: str = "project"


def pdm_build_hook_enabled(context):
    return context.target == "wheel"


def pdm_build_initialize(context):
    context.ensure_build_dir()


# 函式名稱必須嚴格符合 pdm-backend 的 Hook 規範
def pdm_build_update_setup_kwargs(context, kwargs):
    """當 PDM 執行 C/C++、Cython 編譯時，會自動調用這個函式
    context: PDM 的建構上下文物件
    kwargs: 傳遞給 setuptools 的配置字典
    """

    extensions = []
    source_dir = os.path.join("src", PROJECT)
    for root, _, files in os.walk(source_dir):
        for file in files:
            # 排除 __init__.py 和 __main__.py
            if file.endswith(".py") and file not in ["__init__.py", "__main__.py"]:
                full_path = os.path.join(root, file)
                # 計算出它在 Python 匯入時的相對路徑
                rel_path = os.path.relpath(full_path, "src")
                module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")
                # 為這個檔案單獨建立一個 Extension，確保產出獨立的 .so
                extensions.append(Extension(name=module_name, sources=[full_path]))

    # 需要編譯的檔案
    if extensions:
        kwargs.update(
            ext_modules=cythonize(
                extensions, compiler_directives={"language_level": "3"}, annotate=False
            ),
        )


def pdm_build_update_files(context, files):
    if context.target == "sdist":
        return

    build_dir_path = str(context.build_dir)

    # 建立 files 字典移除清單
    keys_to_pop = []

    # 透過 os.walk 實體遍歷 PDM 的 .pdm-build 硬碟目錄
    for root, _, files_in_dir in os.walk(build_dir_path):
        for file in files_in_dir:
            full_path = os.path.join(root, file)

            # 計算出該檔案相對於 build_dir 的相對路徑！
            pdm_standard_key = os.path.relpath(full_path, build_dir_path)

            # 刪除 .c 或 .cpp 暫存檔
            if file.endswith(".c") or file.endswith(".cpp"):
                if pdm_standard_key in files:
                    keys_to_pop.append(pdm_standard_key)
                try:
                    os.remove(full_path)
                except Exception:
                    pass
                continue

            # 如果是 python 原始碼，執行雙向匹配比對
            if file.endswith(".py") and file not in ["__init__.py", "__main__.py"]:
                # 檢查目錄下，有沒有對應的 .so 動態連結庫已經順利生成
                base_name = os.path.splitext(file)[0]
                has_so = any(f.startswith(base_name) and f.endswith(".so") for f in files_in_dir)

                if has_so:
                    # 確認這個轉換後的標準路徑是不是也同時登記在 PDM 的 files 字典裡
                    if pdm_standard_key in files:
                        # 加入移除清單
                        keys_to_pop.append(pdm_standard_key)

                        # 從 build_dir 中刪除它
                        try:
                            os.remove(full_path)
                        except Exception as e:
                            print(
                                f"-> 實體檔案刪除失敗: {pdm_standard_key} 原因: {e}",
                                file=sys.stderr,
                            )

    # 清除對應的 files 鍵值
    for key in keys_to_pop:
        files.pop(key, None)
