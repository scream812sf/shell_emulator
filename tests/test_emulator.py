"""Модульные тесты для логики эмулятора."""

import unittest
from src.emulator import CommandExecutor


class TestCommandExecutor(unittest.TestCase):
    """Набор тестов для класса CommandExecutor."""

    def setUp(self):
        """Создание экземпляра исполнителя команд."""
        self.executor = CommandExecutor()

    def test_ls_stub(self):
        """Проверка работы заглушки ls."""
        output, should_exit = self.executor.execute("ls -l /home")
        self.assertIn("ls: вызвана с аргументами [-l /home]", output)
        self.assertFalse(should_exit)

    def test_cd_stub(self):
        """Проверка работы заглушки cd с допустимым аргументом."""
        output, should_exit = self.executor.execute("cd documents")
        self.assertIn("cd: вызвана с аргументами [documents]", output)
        self.assertFalse(should_exit)

    def test_cd_invalid_args(self):
        """Проверка обработки некорректных аргументов cd."""
        output, should_exit = self.executor.execute("cd dir1 dir2")
        self.assertIn("Ошибка: команда cd принимает не более", output)
        self.assertFalse(should_exit)

    def test_unknown_command(self):
        """Проверка вывода ошибки при неизвестной команде."""
        output, should_exit = self.executor.execute("unknown_cmd arg1")
        self.assertIn("Ошибка: неизвестная команда 'unknown_cmd'", output)
        self.assertFalse(should_exit)

    def test_exit_command(self):
        """Проверка команды exit без аргументов."""
        output, should_exit = self.executor.execute("exit")
        self.assertTrue(should_exit)
        self.assertIn("Завершение работы", output)

    def test_exit_with_args_error(self):
        """Проверка команды exit с ошибочными аргументами."""
        output, should_exit = self.executor.execute("exit 1")
        self.assertFalse(should_exit)
        self.assertIn("Ошибка: команда exit не принимает аргументов", output)


if __name__ == "__main__":
    unittest.main()