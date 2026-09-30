"""Модуль графического интерфейса эмулятора терминала."""

import getpass
import socket
import tkinter as tk
from tkinter import font

from src.emulator import CommandExecutor

WINDOW_WIDTH = 750
WINDOW_HEIGHT = 450
FONT_SIZE = 11


class EmulatorGUI:
    """Класс графического окна терминала."""

    def __init__(self, root: tk.Tk):
        """Конструктор окна эмулятора."""
        self.root = root
        self.executor = CommandExecutor()
        self._init_window()
        self._build_widgets()

    def _init_window(self):
        """Настройка параметров и заголовка окна."""
        username = getpass.getuser()
        hostname = socket.gethostname()
        self.root.title(f"Эмулятор [{username}@{hostname}]")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    def _build_widgets(self):
        """Создание элементов управления интерфейса."""
        term_font = font.Font(family="Courier", size=FONT_SIZE)

        self.text_area = tk.Text(
            self.root,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            font=term_font,
            state=tk.DISABLED,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.prompt_label = tk.Label(
            input_frame,
            text="$ ",
            bg="#1e1e1e",
            fg="#4ec9b0",
            font=term_font,
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame,
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            font=term_font,
            relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._handle_input)
        self.entry.focus_set()

    def _handle_input(self, _event=None):
        """Обработка нажатия клавиши Enter пользователем."""
        command_line = self.entry.get()
        self.entry.delete(0, tk.END)

        self._append_output(f"$ {command_line}\n")
        output, should_exit = self.executor.execute(command_line)

        if output:
            self._append_output(f"{output}\n")

        if should_exit:
            self.root.after(500, self.root.destroy)

    def _append_output(self, text: str):
        """Добавление текста в область терминала."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)


def main():
    """Точка входа приложения."""
    root = tk.Tk()
    _app = EmulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()