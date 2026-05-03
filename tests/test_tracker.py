import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# Предопределённые цитаты (текст, автор, тема)
DEFAULT_QUOTES = [
    {"text": "Будь тем изменением, которое хочешь видеть в мире.", "author": "Махатма Ганди", "theme": "Мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "Жизнь"},
    {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "theme": "Знание"},
    {"text": "Ты можешь быть тем, кем захочешь.", "author": "Доктор Сьюз", "theme": "Вдохновение"},
    {"text": "Не бойтесь совершенства — вам его не достичь.", "author": "Сальвадор Дали", "theme": "Искусство"},
    {"text": "Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "Успех"},
]

QUOTES_FILE = "quotes.json"
HISTORY_FILE = "history.json"

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Загрузка данных
        self.quotes = self.load_quotes()
        self.history = self.load_history()

        # Переменные для фильтрации
        self.filter_author_var = tk.StringVar()
        self.filter_theme_var = tk.StringVar()
        self.current_quote_text = tk.StringVar()
        self.current_quote_author = tk.StringVar()
        self.current_quote_theme = tk.StringVar()

        # Создание интерфейса
        self.create_widgets()
        self.update_author_filter()
        self.update_theme_filter()
        self.refresh_history_display()

    def load_quotes(self):
        """Загружает цитаты из JSON или создаёт файл с предопределёнными"""
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            self.save_quotes(DEFAULT_QUOTES)
            return DEFAULT_QUOTES.copy()

    def save_quotes(self, quotes=None):
        """Сохраняет цитаты в JSON"""
        if quotes is None:
            quotes = self.quotes
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)

    def load_history(self):
        """Загружает историю из JSON"""
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        """Сохраняет историю в JSON"""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Рамка для отображения текущей цитаты
        quote_frame = ttk.LabelFrame(self.root, text="Текущая цитата", padding=10)
        quote_frame.pack(fill="both", expand=False, padx=10, pady=10)

        ttk.Label(quote_frame, textvariable=self.current_quote_text, wraplength=650, font=("Arial", 12, "italic"), justify="center").pack(pady=5)
        ttk.Label(quote_frame, textvariable=self.current_quote_author, font=("Arial", 10, "bold")).pack()
        ttk.Label(quote_frame, textvariable=self.current_quote_theme, font=("Arial", 9)).pack()

        # Кнопка генерации
        ttk.Button(self.root, text="Сгенерировать цитату", command=self.generate_quote).pack(pady=5)

        # Рамка добавления новой цитаты
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую цитату", padding=10)
        add_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(add_frame, text="Текст:").grid(row=0, column=0, sticky="w")
        self.new_text = tk.Text(add_frame, height=3, width=50)
        self.new_text.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.new_author = ttk.Entry(add_frame, width=30)
        self.new_author.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky="w")
        self.new_theme = ttk.Entry(add_frame, width=30)
        self.new_theme.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Добавить", command=self.add_quote).grid(row=3, column=0, columnspan=2, pady=10)

        # Рамка фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация истории", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по автору:").grid(row=0, column=0, sticky="w")
        self.author_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_author_var, state="readonly")
        self.author_filter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.author_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_display())

        ttk.Label(filter_frame, text="Фильтр по теме:").grid(row=1, column=0, sticky="w")
        self.theme_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_theme_var, state="readonly")
        self.theme_filter_combo.grid(row=1, column=1, padx=5, pady=5)
        self.theme_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_display())

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=2, column=0, columnspan=2, pady=5)

        # История
        history_frame = ttk.LabelFrame(self.root, text="История цитат", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, font=("Courier", 9))
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Нижняя панель
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Экспорт истории", command=self.export_history).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Выйти", command=self.root.quit).pack(side="right", padx=5)

    def generate_quote(self):
        """Генерирует случайную цитату"""
        if not self.quotes:
            messagebox.showwarning("Нет цитат", "Сначала добавьте хотя бы одну цитату!")
            return

        quote = random.choice(self.quotes)
        self.current_quote_text.set(quote["text"])
        self.current_quote_author.set(f"— {quote['author']}")
        self.current_quote_theme.set(f"Тема: {quote['theme']}")

        # Добавляем в историю с временной меткой
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": quote["text"],
            "author": quote["author"],
            "theme": quote["theme"]
        }
        self.history.append(history_entry)
        self.save_history()
        self.refresh_history_display()

    def add_quote(self):
        """Добавляет новую цитату с проверкой на пустые строки"""
        text = self.new_text.get("1.0", tk.END).strip()
        author = self.new_author.get().strip()
        theme = self.new_theme.get().strip()

        if not text or not author or not theme:
            messagebox.showerror("Ошибка", "Все поля (текст, автор, тема) обязательны для заполнения!")
            return

        new_quote = {"text": text, "author": author, "theme": theme}
        self.quotes.append(new_quote)
        self.save_quotes()
        self.update_author_filter()
        self.update_theme_filter()

        # Очистка полей
        self.new_text.delete("1.0", tk.END)
        self.new_author.delete(0, tk.END)
        self.new_theme.delete(0, tk.END)

        messagebox.showinfo("Успех", "Цитата добавлена!")

    def update_author_filter(self):
        """Обновляет список авторов в фильтре"""
        authors = sorted(set(q["author"] for q in self.quotes))
        self.author_filter_combo["values"] = ["(Все)"] + authors
        if not self.filter_author_var.get():
            self.filter_author_var.set("(Все)")

    def update_theme_filter(self):
        """Обновляет список тем в фильтре"""
        themes = sorted(set(q["theme"] for q in self.quotes))
        self.theme_filter_combo["values"] = ["(Все)"] + themes
        if not self.filter_theme_var.get():
            self.filter_theme_var.set("(Все)")

    def reset_filters(self):
        """Сбрасывает фильтры"""
        self.filter_author_var.set("(Все)")
        self.filter_theme_var.set("(Все)")
        self.refresh_history_display()

    def refresh_history_display(self):
        """Обновляет отображение истории с учётом фильтров"""
        self.history_listbox.delete(0, tk.END)

        filtered = self.history
        author_filter = self.filter_author_var.get()
        theme_filter = self.filter_theme_var.get()

        if author_filter != "(Все)":
            filtered = [h for h in filtered if h["author"] == author_filter]
        if theme_filter != "(Все)":
            filtered = [h for h in filtered if h["theme"] == theme_filter]

        for entry in filtered:
            display = f"[{entry['timestamp']}] {entry['author']}: {entry['text'][:70]}... (Тема: {entry['theme']})"
            self.history_listbox.insert(tk.END, display)

    def clear_history(self):
        """Очищает историю"""
        self.history = []
        self.save_history()
        self.refresh_history_display()
        messagebox.showinfo("История", "История очищена")

    def export_history(self):
        """Экспорт истории в файл"""
        if not self.history:
            messagebox.showwarning("Нет истории", "Нечего экспортировать")
            return
        filename = f"quote_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Экспорт", f"История сохранена в {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
