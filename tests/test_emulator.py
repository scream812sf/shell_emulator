"""Модульные тесты для исполнителя команд и VFS (Этап 3)."""

import os
import unittest
import zipfile
from src.emulator import CommandExecutor
from src.vfs import VirtualFileSystem

TEST_ZIP_NAME = "test_vfs_sandbox.zip"


class TestVirtualFileSystem(unittest.TestCase):
    """Тестирование VFS и команд cd/ls."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создает временный zip-архив перед запуском тестов."""
        with zipfile.ZipFile(TEST_ZIP_NAME, "w") as archive:
            archive.writestr("root.txt", "root file content")
            archive.writestr("home/user/test.txt", "user file content")
            archive.writestr("home/user/doc.pdf", "pdf content")
            archive.writestr("var/log/", "")

    @classmethod
    def tearDownClass(cls) -> None:
        """Удаляет временный zip-архив после прохождения тестов."""
        if os.path.exists(TEST_ZIP_NAME):
            os.remove(TEST_ZIP_NAME)

    def setUp(self) -> None:
        """Инициализирует VFS перед каждым тестом."""
        self.executor = CommandExecutor(vfs_path=TEST_ZIP_NAME)

    def test_root_listing(self) -> None:
        """Проверка вывода файлов и каталогов в корне."""
        items = self.executor.vfs.list_dir("/")
        self.assertIn("root.txt", items)
        self.assertIn("home", items)
        self.assertIn("var", items)

    def test_cd_absolute_path(self) -> None:
        """Проверка перехода по абсолютному пути."""
        self.executor.execute_line("cd /home/user")
        self.assertEqual(self.executor.vfs.current_dir, "/home/user")
        output = self.executor.execute_line("ls")
        self.assertIn("test.txt", output)
        self.assertIn("doc.pdf", output)

    def test_cd_relative_path(self) -> None:
        """Проверка перехода по относительному пути."""
        self.executor.execute_line("cd home")
        self.assertEqual(self.executor.vfs.current_dir, "/home")
        self.executor.execute_line("cd user")
        self.assertEqual(self.executor.vfs.current_dir, "/home/user")

    def test_cd_dot_dot(self) -> None:
        """Проверка перехода на уровень выше (..)."""
        self.executor.execute_line("cd /home/user")
        self.executor.execute_line("cd ..")
        self.assertEqual(self.executor.vfs.current_dir, "/home")

    def test_cd_nonexistent_directory(self) -> None:
        """Проверка ошибки перехода в несуществующую папку."""
        result = self.executor.execute_line("cd nonexistent")
        self.assertIn("нет такого файла", result)

    def test_cd_to_file(self) -> None:
        """Проверка ошибки попытки перехода в обычный файл."""
        result = self.executor.execute_line("cd root.txt")
        self.assertIn("не каталог", result)

    def test_ls_with_argument(self) -> None:
        """Проверка вызова команды ls с аргументом пути."""
        result = self.executor.execute_line("ls /home/user")
        self.assertIn("test.txt", result)
        self.assertIn("doc.pdf", result)


if __name__ == "__main__":
    unittest.main()