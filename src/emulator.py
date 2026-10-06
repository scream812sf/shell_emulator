"""Модуль логики интерпретатора команд с поддержкой VFS (Этап 4)."""

import time
from typing import Dict, List, Optional
from src.vfs import VirtualFileSystem

DEFAULT_TAIL_LINES = 10


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
        self.start_time: float = time.time()

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

    def cmd_uptime(self, args: List[str]) -> str:
        """Выводит время работы эмулятора с момента запуска."""
        if args:
            return "Ошибка: команда uptime не принимает аргументов"
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"up {hours:02d}:{minutes:02d}:{seconds:02d}"

    def cmd_tail(self, args: List[str]) -> str:
        """Выводит последние строки текстового файла из VFS."""
        if not args:
            return "tail: пропущен операнд, задающий файл"

        lines_count = DEFAULT_TAIL_LINES
        target_file = ""

        if args[0] == "-n":
            if len(args) < 3:
                return "tail: для параметра '-n' требуется числовое значение"
            if not args[1].isdigit():
                return f"tail: неверное число строк: '{args[1]}'"
            lines_count = int(args[1])
            target_file = args[2]
        else:
            target_file = args[0]

        try:
            text = self.vfs.read_file(target_file)
            lines = text.splitlines()
            selected = lines[-lines_count:] if lines_count > 0 else []
            return "\n".join(selected)
        except (FileNotFoundError, IsADirectoryError) as error:
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
            "uptime": self.cmd_uptime,
            "tail": self.cmd_tail,
        }

        if command_name == "exit":
            return "exit"
        if command_name in commands:
            return commands[command_name](arguments)
        return f"Ошибка: неизвестная команда '{command_name}'"