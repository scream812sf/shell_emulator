"""Модуль логики командной строки эмулятора ОС.

Содержит парсер команд, хранилище параметров и выполнение команд.
"""

from typing import Dict, List, Optional, Tuple

class CommandExecutor:
    """Класс для разбора и выполнения команд эмулятора."""

    def __init__(
        self,
        vfs_path: Optional[str] = None,
        script_path: Optional[str] = None,
    ) -> None:
        """Инициализация обработчика команд и параметров конфигурации."""
        self.vfs_path = vfs_path or ""
        self.script_path = script_path or ""

    def parse_command(self, command_line: str) -> Tuple[str, List[str]]:
        """Разбивает строку ввода на имя команды и список аргументов."""
        tokens = command_line.strip().split()
        if not tokens:
            return "", []
        return tokens[0], tokens[1:]

    def get_config(self) -> Dict[str, str]:
        """Возвращает словарь текущих параметров конфигурации."""
        return {
            "vfs_path": self.vfs_path,
            "script_path": self.script_path,
        }

    def execute(self, command_line: str) -> Tuple[str, bool]:
        """Выполняет команду эмулятора.

        Возвращает:
            (текст_вывода, флаг_завершения_работы)
        """
        stripped = command_line.strip()
        if not stripped or stripped.startswith("#"):
            return "", False

        cmd, args = self.parse_command(stripped)
        if cmd == "ls":
            return self._handle_ls(args), False
        if cmd == "cd":
            return self._handle_cd(args), False
        if cmd == "exit":
            return self._handle_exit(args)
        if cmd == "conf-dump":
            return self._handle_conf_dump(args), False

        return f"Ошибка: неизвестная команда '{cmd}'", False

    def _handle_ls(self, args: List[str]) -> str:
        """Обработка команды-заглушки ls."""
        args_str = f" [{' '.join(args)}]" if args else ""
        return f"ls: вызвана с аргументами{args_str}"

    def _handle_cd(self, args: List[str]) -> str:
        """Обработка команды-заглушки cd с валидацией аргументов."""
        if len(args) > 1:
            return "Ошибка: команда cd принимает не более одного аргумента"
        args_str = f" [{args[0]}]" if args else ""
        return f"cd: вызвана с аргументами{args_str}"

    def _handle_exit(self, args: List[str]) -> Tuple[str, bool]:
        """Обработка команды завершения работы exit."""
        if args:
            return "Ошибка: команда exit не принимает аргументов", False
        return "Завершение работы эмулятора...", True

    def _handle_conf_dump(self, args: List[str]) -> str:
        """Обработка служебной команды conf-dump (вывод ключ-значение)."""
        if args:
            return "Ошибка: команда conf-dump не принимает аргументов"
        cfg = self.get_config()
        lines = [f"{k}: {v}" for k, v in cfg.items()]
        return "\n".join(lines)