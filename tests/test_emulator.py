"""Модульные тесты для исполнителя команд, VFS и команд Этапа 4."""

import os
import unittest
import zipfile
from src.emulator import CommandExecutor

TEST_ZIP_NAME = "test_vfs_sandbox.zip"


class TestVirtualFileSystem(unittest.TestCase):
    """Тестирование VFS и команд эмулятора."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создает временный zip-архив перед запуском тестов."""
        long_content = "\n".join([f"entry {i}" for i in range(1, 15)])
        with zipfile.ZipFile(TEST_ZIP_NAME, "w") as archive:
            archive.writestr("root.txt", "line1\nline2\nline3\n")
            archive.writestr("long.txt", long_content)
            archive.writestr("home/user/test.txt", "user file content")
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

    def test_cd_navigation(self) -> None:
        """Проверка перемещения по директориям."""
        self.executor.execute_line("cd home/user")
        self.assertEqual(self.executor.vfs.current_dir, "/home/user")
        self.executor.execute_line("cd ..")
        self.assertEqual(self.executor.vfs.current_dir, "/home")

    def test_uptime_command(self) -> None:
        """Проверка формата вывода команды uptime."""
        output = self.executor.execute_line("uptime")
        self.assertTrue(output.startswith("up "))

    def test_uptime_invalid_arguments(self) -> None:
        """Проверка ошибки команды uptime при передаче параметров."""
        output = self.executor.execute_line("uptime now")
        self.assertIn("не принимает аргументов", output)

    def test_tail_default_lines(self) -> None:
        """Проверка tail без аргументов строк."""
        output = self.executor.execute_line("tail root.txt")
        self.assertEqual(output, "line1\nline2\nline3")

    def test_tail_with_custom_count(self) -> None:
        """Проверка tail с флагом -n."""
        output = self.executor.execute_line("tail -n 2 root.txt")
        self.assertEqual(output, "line2\nline3")

    def test_tail_nonexistent_file(self) -> None:
        """Проверка ошибки tail для несуществующего файла."""
        output = self.executor.execute_line("tail missing.txt")
        self.assertIn("нет такого файла", output)

    def test_tail_on_directory(self) -> None:
        """Проверка ошибки tail при попытке чтения директории."""
        output = self.executor.execute_line("tail home")
        self.assertIn("это каталог", output)

    def test_tail_invalid_n_param(self) -> None:
        """Проверка ошибки передачи нечислового аргумента в -n."""
        output = self.executor.execute_line("tail -n abc root.txt")
        self.assertIn("неверное число строк", output)


if __name__ == "__main__":
    unittest.main()