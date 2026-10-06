"""Модульные тесты для команд и VFS (Этапы 1-5)."""

import os
import unittest
import zipfile
from src.emulator import CommandExecutor

TEST_ZIP = "test_vfs_primary.zip"
TEST_ALT_ZIP = "test_vfs_alt.zip"


class TestVirtualFileSystem(unittest.TestCase):
    """Тестирование VFS и всех поддерживаемых команд эмулятора."""

    @classmethod
    def setUpClass(cls) -> None:
        """Создает временные архивы для тестов."""
        with zipfile.ZipFile(TEST_ZIP, "w") as arc:
            arc.writestr("root.txt", "line1\nline2\nline3\n")
            arc.writestr("home/user/notes.txt", "task 1\ntask 2")
            arc.writestr("clean_dir/", "")

        with zipfile.ZipFile(TEST_ALT_ZIP, "w") as arc:
            arc.writestr("alt_file.txt", "reloaded successfully")

    @classmethod
    def tearDownClass(cls) -> None:
        """Удаляет временные архивы после завершения тестов."""
        for path in (TEST_ZIP, TEST_ALT_ZIP):
            if os.path.exists(path):
                os.remove(path)

    def setUp(self) -> None:
        """Инициализирует исполнитель перед каждым тестом."""
        self.executor = CommandExecutor(vfs_path=TEST_ZIP)

    def test_root_listing(self) -> None:
        """Проверка листинга каталога."""
        items = self.executor.vfs.list_dir("/")
        self.assertIn("root.txt", items)
        self.assertIn("clean_dir", items)

    def test_cd_navigation(self) -> None:
        """Проверка перемещения по каталогам."""
        self.executor.execute_line("cd home/user")
        self.assertEqual(self.executor.vfs.current_dir, "/home/user")

    def test_uptime_command(self) -> None:
        """Проверка команды uptime."""
        output = self.executor.execute_line("uptime")
        self.assertTrue(output.startswith("up "))

    def test_tail_command(self) -> None:
        """Проверка команды tail."""
        output = self.executor.execute_line("tail -n 2 root.txt")
        self.assertEqual(output, "line2\nline3")

    def test_rmdir_empty_directory(self) -> None:
        """Проверка удаления пустого каталога."""
        self.assertIn("clean_dir", self.executor.vfs.list_dir("/"))
        res = self.executor.execute_line("rmdir clean_dir")
        self.assertEqual(res, "")
        self.assertNotIn("clean_dir", self.executor.vfs.list_dir("/"))

    def test_rmdir_non_empty_directory(self) -> None:
        """Проверка ошибки при попытке удаления непустого каталога."""
        res = self.executor.execute_line("rmdir home")
        self.assertIn("каталог не пуст", res)

    def test_rmdir_root(self) -> None:
        """Проверка запрета удаления корня."""
        res = self.executor.execute_line("rmdir /")
        self.assertIn("невозможно удалить корневой каталог", res)

    def test_vfs_load_success(self) -> None:
        """Проверка команды vfs-load для смены архива на лету."""
        res = self.executor.execute_line(f"vfs-load {TEST_ALT_ZIP}")
        self.assertIn("успешно загружена", res)
        items = self.executor.vfs.list_dir("/")
        self.assertIn("alt_file.txt", items)
        self.assertNotIn("root.txt", items)

    def test_vfs_load_missing_file(self) -> None:
        """Проверка ошибки vfs-load при отсутствии файла."""
        res = self.executor.execute_line("vfs-load non_existing.zip")
        self.assertIn("не найден", res)


if __name__ == "__main__":
    unittest.main()