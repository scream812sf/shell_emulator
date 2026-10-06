"""Модуль виртуальной файловой системы (VFS) в оперативной памяти (Этап 5)."""

import os
import posixpath
import zipfile
from typing import Dict, List, Optional, Set


class VirtualFileSystem:
    """Представляет файловую систему в оперативной памяти на основе zip."""

    def __init__(self, vfs_path: Optional[str] = None) -> None:
        self.vfs_path: Optional[str] = vfs_path
        self.current_dir: str = "/"
        self.directories: Set[str] = {"/"}
        self.files: Set[str] = set()
        self.file_data: Dict[str, bytes] = {}
        if vfs_path and os.path.exists(vfs_path):
            self._load_from_zip(vfs_path)

    def _register_dir_parents(self, dir_path: str) -> None:
        """Регистрирует директорию и всю цепочку её родителей."""
        current = dir_path
        while current and current != "/":
            self.directories.add(current)
            current = posixpath.dirname(current)

    def _load_from_zip(self, zip_path: str) -> None:
        """Считывает структуру файлов, каталогов и данные из zip-архива."""
        with zipfile.ZipFile(zip_path, "r") as archive:
            for item in archive.namelist():
                norm = posixpath.normpath("/" + item.replace("\\", "/"))
                if item.endswith("/"):
                    self._register_dir_parents(norm)
                else:
                    self.files.add(norm)
                    self._register_dir_parents(posixpath.dirname(norm))
                    self.file_data[norm] = archive.read(item)

    def reload(self, new_vfs_path: str) -> None:
        """Перезагружает VFS из нового zip-архива с диска."""
        if not os.path.exists(new_vfs_path):
            raise FileNotFoundError(
                f"vfs-load: архив '{new_vfs_path}' не найден"
            )
        self.vfs_path = new_vfs_path
        self.current_dir = "/"
        self.directories = {"/"}
        self.files = set()
        self.file_data = {}
        self._load_from_zip(new_vfs_path)

    def resolve_path(self, target_path: str) -> str:
        """Преобразует относительный или абсолютный путь в канонический."""
        if not target_path:
            return self.current_dir
        if target_path.startswith("/"):
            return posixpath.normpath(target_path)
        return posixpath.normpath(
            posixpath.join(self.current_dir, target_path)
        )

    def change_dir(self, target_path: Optional[str] = None) -> None:
        """Переходит в указанную директорию."""
        if not target_path:
            self.current_dir = "/"
            return

        destination = self.resolve_path(target_path)
        if destination in self.directories:
            self.current_dir = destination
            return
        if destination in self.files:
            raise NotADirectoryError(f"cd: '{target_path}': не каталог")
        raise FileNotFoundError(f"cd: '{target_path}': нет такого файла")

    def list_dir(self, target_path: Optional[str] = None) -> List[str]:
        """Возвращает список элементов внутри каталога."""
        target_dir = (
            self.resolve_path(target_path)
            if target_path
            else self.current_dir
        )
        if target_dir not in self.directories:
            if target_dir in self.files:
                raise NotADirectoryError(f"ls: '{target_path}': не каталог")
            raise FileNotFoundError(f"ls: '{target_path}': нет такого файла")

        entries: Set[str] = set()
        for directory in self.directories:
            if directory == target_dir or directory == "/":
                continue
            if posixpath.dirname(directory) == target_dir:
                entries.add(posixpath.basename(directory))

        for file_item in self.files:
            if posixpath.dirname(file_item) == target_dir:
                entries.add(posixpath.basename(file_item))

        return sorted(entries)

    def read_file(self, target_path: str) -> str:
        """Считывает текстовое содержимое файла из VFS."""
        file_path = self.resolve_path(target_path)
        if file_path in self.directories:
            raise IsADirectoryError(f"tail: '{target_path}': это каталог")
        if file_path not in self.files:
            raise FileNotFoundError(
                f"tail: '{target_path}': нет такого файла"
            )
        raw_bytes = self.file_data.get(file_path, b"")
        return raw_bytes.decode("utf-8", errors="replace")

    def remove_dir(self, target_path: str) -> None:
        """Удаляет пустой каталог из виртуальной памяти."""
        resolved = self.resolve_path(target_path)
        if resolved == "/":
            raise ValueError("rmdir: невозможно удалить корневой каталог '/'")
        if resolved not in self.directories:
            if resolved in self.files:
                raise NotADirectoryError(
                    f"rmdir: '{target_path}': не является каталогом"
                )
            raise FileNotFoundError(
                f"rmdir: '{target_path}': нет такого каталога"
            )

        has_subdirs = any(
            d != resolved and posixpath.dirname(d) == resolved
            for d in self.directories
        )
        has_files = any(
            posixpath.dirname(f) == resolved for f in self.files
        )
        if has_subdirs or has_files:
            raise OSError(f"rmdir: '{target_path}': каталог не пуст")

        if self.current_dir == resolved or self.current_dir.startswith(
            resolved + "/"
        ):
            self.current_dir = posixpath.dirname(resolved)
        self.directories.remove(resolved)