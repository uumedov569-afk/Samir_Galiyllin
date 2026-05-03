import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

DATA_FILE = "weather_diary.json"

class WeatherDiary:
    def init(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")
        self.records = []
        self.filtered_records = []

        # --- Поля ввода ---
        input_frame = tk.LabelFrame(root, text="Новая запись", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e", pady=5)
        self.date_entry = tk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, pady=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="e", pady=5)
        self.temp_entry = tk.Entry(input_frame, width=20)
        self.temp_entry.grid(row=1, column=1, pady=5)

        # Описание
        tk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="e", pady=5)
        self.desc_entry = tk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=2, column=1, pady=5)

        # Осадки
        tk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky="e", pady=5)
        self.rain_var = tk.StringVar(value="Нет")
        rain_frame = tk.Frame(input_frame)
        rain_frame.grid(row=3, column=1, sticky="w")
        tk.Radiobutton(rain_frame, text="Да", variable=self.rain_var, value="Да").pack(side="left")
        tk.Radiobutton(rain_frame, text="Нет", variable=self.rain_var, value="Нет").pack(side="left")

        # Кнопка добавления
        tk.Button(input_frame, text="+ Добавить запись", command=self.add_record, bg="lightgreen").grid(row=4, column=0, columnspan=2, pady=10)

        # --- Таблица записей ---
        list_frame = tk.LabelFrame(root, text="Записи о погоде", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)

        # --- Фильтры ---
        filter_frame = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.filter_date = tk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Температура от (°C):").grid(row=0, column=2, padx=5)
        self.filter_temp_from = tk.Entry(filter_frame, width=10)
        self.filter_temp_from.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5)
        self.filter_temp_to = tk.Entry(filter_frame, width=10)
        self.filter_temp_to.grid(row=0, column=5, padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=6, padx=10)
        tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=7, padx=5)

        # --- Кнопки сохранения/загрузки ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_file, bg="lightblue").pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_file, bg="lightyellow").pack(side="left", padx=5)

        # Загружаем данные при старте
        self.load_from_file()

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
          def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        rain = self.rain_var.get()

        # Проверки
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        record = {
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "rain": rain
        }
        self.records.append(record)
        self.reset_filter()
        messagebox.showinfo("Успех", "Запись добавлена")
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.rain_var.set("Нет")

    def update_treeview(self, records_list):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in records_list:
            self.tree.insert("", tk.END, values=(r["date"], r["temperature"], r["description"], r["rain"]))

    def apply_filter(self):
        filter_date = self.filter_date.get().strip()
        temp_from = self.filter_temp_from.get().strip()
        temp_to = self.filter_temp_to.get().strip()

        filtered = self.records[:]
        if filter_date:
            filtered = [r for r in filtered if r["date"] == filter_date]
        if temp_from:
            try:
                t_min = float(temp_from)
                filtered = [r for r in filtered if r["temperature"] >= t_min]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное значение 'температура от'")
                return
        if temp_to:
            try:
                t_max = float(temp_to)
                filtered = [r for r in filtered if r["temperature"] <= t_max]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное значение 'температура до'")
                return
        self.update_treeview(filtered)

    def reset_filter(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp_from.delete(0, tk.END)
        self.filter_temp_to.delete(0, tk.END)
        self.update_treeview(self.records)

    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Сохранено в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if not os.path.exists(DATA_FILE):
            self.records = []
            self.update_treeview([])
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.reset_filter()
            messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
            self.records = []

if name == "main":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
