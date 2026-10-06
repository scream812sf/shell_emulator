"""Модуль графического интерфейса эмулятора shell.

Реализует GUI терминала на Tkinter с поддержкой параметров запуска.
"""

import argparse
import getpass
import os
import socket
import sys
import tkinter as tk
from tkinter import font
from typing import List, Optional
from src.emulator import CommandExecutor

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
FONT_SIZE = 11
STEP_DELAY_MS = 150
EXIT_DELAY_MS = 500


class ShellGUI:
    """Класс графического интерфейса эмулятора."""

    def __init__(
        self,
        root: tk.Tk,
        vfs_path: Optional[str] = None,
        script_path: Optional[str] = None,
    ) -> None:
        """Инициализирует графическое окно и выполняет стартовую настройку."""
        self.root = root
        self.executor = CommandExecutor(vfs_path, script_path)
        self._configure_window()
        self._create_widgets()
        self._print_startup_debug()
        if script_path:
            self.root.after(
                STEP_DELAY_MS, lambda: self._run_startup_script(script_path)
            )

    def _configure_window(self) -> None:
        """Настраивает параметры и заголовок окна."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор [{username}@{hostname}]")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#1e1e1e")

    def _create_widgets(self) -> None:
        """Создает элементы управления терминала."""
        term_font = font.Font(family="Consolas", size=FONT_SIZE)
        self.text_area = tk.Text(
            self.root,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            font=term_font,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bd=0,
            padx=10,
            pady=10,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self.prompt_label = tk.Label(
            input_frame, text="$ ", bg="#1e1e1e", fg="#4ec9b0", font=term_font
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            font=term_font,
            bd=0,
        )
        self.entry.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.entry.focus_set()
        self.entry.bind("<Return>", self._on_enter_pressed)

    def _append_output(self, text: str) -> None:
        """Добавляет текст в окно вывода терминала."""
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def _print_startup_debug(self) -> None:
        """Выводит отладочную информацию о параметрах при старте."""
        cfg = self.executor.get_config()
        self._append_output(
            "=== Отладочный вывод параметров конфигурации ===\n"
        )
        self._append_output(f"VFS Path: {cfg['vfs_path'] or '(не задан)'}\n")
        self._append_output(
            f"Startup Script: {cfg['script_path'] or '(не задан)'}\n"
        )
        self._append_output(
            "================================================\n\n"
        )

    def _run_startup_script(self, script_path: str) -> None:
        """Выполняет стартовый скрипт с имитацией диалога."""
        if not os.path.exists(script_path):
            self._append_output(
                f"Ошибка: стартовый скрипт '{script_path}' не найден\n"
            )
            return

        try:
            with open(script_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except OSError as err:
            self._append_output(
                f"Ошибка чтения стартового скрипта: {err}\n"
            )
            return

        self._execute_script_lines(lines, 0)

    def _execute_script_lines(self, lines: List[str], index: int) -> None:
        """Построчно выполняет команды скрипта с задержкой."""
        if index >= len(lines):
            return

        line = lines[index].strip()
        if line and not line.startswith("#"):
            self._append_output(f"$ {line}\n")
            output, should_exit = self.executor.execute(line)
            if output:
                self._append_output(f"{output}\n")
            if should_exit:
                self.root.after(EXIT_DELAY_MS, self.root.destroy)
                return

        self.root.after(
            STEP_DELAY_MS, lambda: self._execute_script_lines(lines, index + 1)
        )

    def _on_enter_pressed(self, event: tk.Event) -> None:
        """Обрабатывает ввод команды пользователем."""
        command_line = self.entry.get()
        self.entry.delete(0, tk.END)

        if not command_line.strip():
            self._append_output("$\n")
            return

        self._append_output(f"$ {command_line}\n")
        output, should_exit = self.executor.execute(command_line)
        if output:
            self._append_output(f"{output}\n")
        if should_exit:
            self.root.after(EXIT_DELAY_MS, self.root.destroy)


def parse_args(args: List[str]) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор UNIX shell (Вариант 27)"
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        default="",
        help="Путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        default="",
        help="Путь к стартовому скрипту эмулятора",
    )
    return parser.parse_args(args)


def main() -> None:
    """Точка входа запуска графического интерфейса."""
    parsed = parse_args(sys.argv[1:])
    root = tk.Tk()
    ShellGUI(root, vfs_path=parsed.vfs_path, script_path=parsed.script_path)
    root.mainloop()


if __name__ == "__main__":
    main()