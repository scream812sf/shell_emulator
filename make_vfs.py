"""Скрипт для сборки тестового архива виртуальной файловой системы."""

import zipfile
from pathlib import Path

VFS_NAME = "virtual_fs.zip"

FILES_DATA = {
    "readme.txt": "Welcome to VFS!\nVariant 27 Shell Emulator.\n",
    "home/user/test.txt": "Hello from user directory.\n",
    "home/user/notes.txt": "1. Task one\n2. Task two\n",
    "etc/config.cfg": "env=production\nversion=1.0.0\n",
}


def build_vfs(target_path: str = VFS_NAME) -> None:
    """Создает zip-архив с тестовой иерархией каталогов."""
    with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path, content in FILES_DATA.items():
            archive.writestr(file_path, content)


if __name__ == "__main__":
    build_vfs()
    print(f"Архив {VFS_NAME} успешно создан.")