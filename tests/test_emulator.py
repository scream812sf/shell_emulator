"""Модульные тесты для логики эмулятора командной строки (Этап 2)."""

import unittest
from src.emulator import CommandExecutor
from src.gui import parse_args


class TestCommandExecutorStage2(unittest.TestCase):
    """Набор тестов для функциональности 2-го этапа."""

    def setUp(self) -> None:
        """Создание экземпляра исполнителя с параметрами конфигурации."""
        self.executor = CommandExecutor(
            vfs_path="/path/to/vfs.zip",
            script_path="scripts/startup.txt",
        )

    def test_conf_dump_format(self) -> None:
        """Проверка вывода служебной команды conf-dump."""
        output, should_exit = self.executor.execute("conf-dump")
        self.assertFalse(should_exit)
        self.assertIn("vfs_path: /path/to/vfs.zip", output)
        self.assertIn("script_path: scripts/startup.txt", output)

    def test_conf_dump_with_args_error(self) -> None:
        """Проверка ошибки при передаче аргументов в conf-dump."""
        output, should_exit = self.executor.execute("conf-dump extra")
        self.assertFalse(should_exit)
        self.assertIn("не принимает аргументов", output)

    def test_comment_line_ignored(self) -> None:
        """Проверка игнорирования строк-комментариев."""
        output, should_exit = self.executor.execute("# тестовый комментарий")
        self.assertFalse(should_exit)
        self.assertEqual(output, "")

    def test_cli_parsing_full(self) -> None:
        """Проверка разбора полного набора аргументов CLI."""
        args = parse_args(["--vfs", "my_vfs.zip", "--script", "init.txt"])
        self.assertEqual(args.vfs_path, "my_vfs.zip")
        self.assertEqual(args.script_path, "init.txt")

    def test_cli_parsing_defaults(self) -> None:
        """Проверка значений по умолчанию без передачи ключей."""
        args = parse_args([])
        self.assertEqual(args.vfs_path, "")
        self.assertEqual(args.script_path, "")

    def test_ls_and_cd_stubs(self) -> None:
        """Проверка корректной работы команд-заглушек ls и cd."""
        out_ls, _ = self.executor.execute("ls -la")
        out_cd, _ = self.executor.execute("cd folder")
        self.assertIn("ls: вызвана с аргументами [-la]", out_ls)
        self.assertIn("cd: вызвана с аргументами [folder]", out_cd)


if __name__ == "__main__":
    unittest.main()