"""Скрипт для сборки тестовых архивов виртуальной файловой системы."""

import zipfile

MAIN_VFS = "virtual_fs.zip"
SECONDARY_VFS = "secondary_vfs.zip"

LONG_TEXT = "\n".join([f"Line {idx}" for idx in range(1, 16)])

MAIN_DATA = {
    "readme.txt": "Welcome to VFS!\nVariant 27 Shell Emulator.\n",
    "long.txt": LONG_TEXT,
    "home/user/test.txt": "Hello from user directory.\n",
    "home/user/notes.txt": "1. Task one\n2. Task two\n",
    "etc/config.cfg": "env=production\nversion=1.0.0\n",
    "empty_dir/": "",
}

SECONDARY_DATA = {
    "backup_info.txt": "This is secondary VFS archive loaded at runtime.\n",
    "var/data.log": "System rebooted\nStatus: OK\n",
}


def build_archives() -> None:
    """Создает основной и вторичный zip-архивы VFS."""
    with zipfile.ZipFile(MAIN_VFS, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path, content in MAIN_DATA.items():
            archive.writestr(file_path, content)

    with zipfile.ZipFile(SECONDARY_VFS, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path, content in SECONDARY_DATA.items():
            archive.writestr(file_path, content)


if __name__ == "__main__":
    build_archives()
    print(f"Архивы {MAIN_VFS} и {SECONDARY_VFS} успешно созданы.")