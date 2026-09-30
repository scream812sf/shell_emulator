"""Модуль логики интерпретатора команд эмулятора."""

class CommandExecutor:
    """Класс для разбора и выполнения команд REPL."""

    def __init__(self):
        """Инициализация доступных команд."""
        self.supported_commands = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
        }

    def parse_input(self, user_input: str) -> tuple[str, list[str]]:
        """Разбиение входной строки на команду и аргументы по пробелам."""
        tokens = user_input.strip().split()
        if not tokens:
            return "", []
        return tokens[0], tokens[1:]

    def execute(self, user_input: str) -> tuple[str, bool]:
        """
        Выполнение команды.

        Возвращает кортеж: (вывод команды, флаг завершения работы).
        """
        cmd, args = self.parse_input(user_input)
        if not cmd:
            return "", False

        handler = self.supported_commands.get(cmd)
        if handler is None:
            return f"Ошибка: неизвестная команда '{cmd}'", False

        return handler(args)

    def _cmd_ls(self, args: list[str]) -> tuple[str, bool]:
        """Команда-заглушка ls."""
        args_repr = " ".join(args)
        return f"ls: вызвана с аргументами [{args_repr}]", False

    def _cmd_cd(self, args: list[str]) -> tuple[str, bool]:
        """Команда-заглушка cd с валидацией числа аргументов."""
        max_cd_args = 1
        if len(args) > max_cd_args:
            return "Ошибка: команда cd принимает не более одного аргумента", False
        args_repr = " ".join(args)
        return f"cd: вызвана с аргументами [{args_repr}]", False

    def _cmd_exit(self, args: list[str]) -> tuple[str, bool]:
        """Команда exit."""
        if args:
            return "Ошибка: команда exit не принимает аргументов", False
        return "Завершение работы эмулятора...", True