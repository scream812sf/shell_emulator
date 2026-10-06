"""Модуль графического интерфейса эмулятора на Tkinter."""

import argparse
import getpass
import os
import socket
import tkinter as tk
from tkinter import scrolledtext
from typing import List, Optional

from src.emulator import CommandExecutor

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
FONT_SIZE = 11
STEP_DELAY_MS = 250
EXIT_DELAY_MS = 300


class ShellGUI:
    """Графический терминал с обработкой команд и стартовых скриптов."""

    def __init__(self, vfs_path: Optional[str], script_path: Optional[str]):
        self.executor = CommandExecutor(vfs_path, script_path)
        self.script_path = script_path
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()

        self.root = tk.Tk()
        self.root.title(f"Эмулятор [{self.username}@{self.hostname}]")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#1e1e1e")

        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            font=("Consolas", FONT_SIZE),
        )
        self.text_area.pack(expand=True, fill="both")
        self.text_area.bind("<Return>", self._handle_manual_enter)

        self._show_startup_info(vfs_path, script_path)
        self._insert_prompt()

        if self.script_path:
            self.root.after(STEP_DELAY_MS, self._execute_startup_script)

    def _get_prompt(self) -> str:
        """Формирует строку приглашения с текущим путем VFS."""
        path = self.executor.get_prompt_path()
        return f"{self.username}@{self.hostname}:{path}$ "

    def _show_startup_info(
        self, vfs_path: Optional[str], script_path: Optional[str]
    ) -> None:
        """Выводит отладочный блок параметров конфигурации."""
        vfs_info = vfs_path if vfs_path else "(не задан)"
        script_info = script_path if script_path else "(не задан)"
        self.text_area.insert(
            tk.END,
            "=== Отладочный вывод параметров конфигурации ===\n"
            f"VFS Path: {vfs_info}\n"
            f"Startup Script: {script_info}\n"
            "================================================\n\n",
        )

    def _insert_prompt(self) -> None:
        """Вставляет строку приглашения и ставит курсор в конец."""
        self.text_area.insert(tk.END, self._get_prompt())
        self.text_area.mark_set(tk.INSERT, tk.END)
        self.text_area.see(tk.END)

    def _handle_manual_enter(self, _event: tk.Event) -> str:
        """Обрабатывает ручной ввод команды по Enter."""
        line = self.text_area.get("insert linestart", "insert lineend")
        prompt = self._get_prompt()
        command = line[len(prompt):] if line.startswith(prompt) else line
        self.text_area.insert(tk.END, "\n")
        self._process_single_command(command)
        return "break"

    def _process_single_command(self, command: str) -> None:
        """Выполняет одну команду и выводит результат."""
        output = self.executor.execute_line(command)
        if output == "exit":
            self.root.after(EXIT_DELAY_MS, self.root.destroy)
            return
        if output is not None and output != "":
            self.text_area.insert(tk.END, f"{output}\n")
        self._insert_prompt()

    def _execute_startup_script(self) -> None:
        """Построчно с задержкой выполняет команды стартового скрипта."""
        if not self.script_path or not os.path.exists(self.script_path):
            if self.script_path:
                msg = f"Ошибка: скрипт '{self.script_path}' не найден\n"
                self.text_area.insert(tk.END, msg)
                self._insert_prompt()
            return

        with open(self.script_path, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        def step(index: int) -> None:
            if index >= len(lines):
                return
            command = lines[index]
            self.text_area.insert(tk.END, f"{command}\n")
            output = self.executor.execute_line(command)
            if output == "exit":
                self.root.after(EXIT_DELAY_MS, self.root.destroy)
                return
            if output is not None and output != "":
                self.text_area.insert(tk.END, f"{output}\n")
            if index + 1 < len(lines):
                self._insert_prompt()
                self.root.after(STEP_DELAY_MS, lambda: step(index + 1))
            else:
                self._insert_prompt()

        step(0)

    def run(self) -> None:
        """Запускает цикл обработки событий Tkinter."""
        self.root.mainloop()


def parse_cli_args() -> argparse.Namespace:
    """Парсит параметры командной строки приложения."""
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument("--vfs", type=str, help="Путь к zip-архиву VFS")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()
    app = ShellGUI(vfs_path=args.vfs, script_path=args.script)
    app.run()