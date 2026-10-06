"""Модуль логики интерпретатора команд с поддержкой VFS."""

from typing import Dict, List, Optional
from src.vfs import VirtualFileSystem


class CommandExecutor:
    """Исполнитель встроенных команд оболочки с виртуальной ФС."""

    def __init__(
        self,
        vfs_path: Optional[str] = None,
        script_path: Optional[str] = None,
    ) -> None:
        self.vfs_path: Optional[str] = vfs_path
        self.script_path: Optional[str] = script_path
        self.vfs: VirtualFileSystem = VirtualFileSystem(vfs_path)

    def get_prompt_path(self) -> str:
        """Возвращает текущий путь для строки приглашения."""
        return self.vfs.current_dir

    def cmd_conf_dump(self, args: List[str]) -> str:
        """Служебная команда вывода конфигурации."""
        if args:
            return "Ошибка: команда conf-dump не принимает аргументов"
        vfs_display = self.vfs_path if self.vfs_path else "(не задан)"
        script_display = self.script_path if self.script_path else "(не задан)"
        return f"vfs_path: {vfs_display}\nscript_path: {script_display}"

    def cmd_ls(self, args: List[str]) -> str:
        """Выводит содержимое каталога из VFS."""
        target = args[0] if args else None
        try:
            items = self.vfs.list_dir(target)
            return "\n".join(items) if items else ""
        except (FileNotFoundError, NotADirectoryError) as error:
            return str(error)

    def cmd_cd(self, args: List[str]) -> str:
        """Выполняет смену директории в VFS."""
        if len(args) > 1:
            return "Ошибка: команда cd принимает не более одного аргумента"
        target = args[0] if args else None
        try:
            self.vfs.change_dir(target)
            return ""
        except (FileNotFoundError, NotADirectoryError) as error:
            return str(error)

    def execute_line(self, line: str) -> Optional[str]:
        """Парсит и выполняет команду, возвращая текстовый результат."""
        raw_line = line.strip()
        if not raw_line or raw_line.startswith("#"):
            return None

        tokens = raw_line.split()
        command_name = tokens[0]
        arguments = tokens[1:]

        commands: Dict[str, callable] = {
            "conf-dump": self.cmd_conf_dump,
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
        }

        if command_name == "exit":
            return "exit"
        if command_name in commands:
            return commands[command_name](arguments)
        return f"Ошибка: неизвестная команда '{command_name}'"