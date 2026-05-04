import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# Имя файла для хранения данных
DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер Расходов (GosPrompt AI)")
        self.root.geometry("800x600")
        
        self.expenses = []
        self.load_data()

        # --- Интерфейс ---
        # Фрейм для ввода данных
        input_frame = tk.LabelFrame(root, text="Новый расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.entry_amount = tk.Entry(input_frame)
        self.entry_amount.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w")
        self.entry_category = ttk.Combobox(input_frame, values=["Еда", "Транспорт", "Развлечения", "Жилье", "Другое"], state="readonly")
        self.entry_category.grid(row=0, column=3, padx=5)
        self.entry_category.current(0)

        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w")
        self.entry_date = tk.Entry(input_frame)
        self.entry_date.grid(row=0, column=5, padx=5)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))

        btn_add = tk.Button(input_frame, text="Добавить", command=self.add_expense, bg="#4CAF50", fg="white")
        btn_add.grid(row=0, column=6, padx=10)

        # Фрейм для фильтрации
        filter_frame = tk.LabelFrame(root, text="Фильтр и Итоги", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Жилье", "Другое"], state="readonly")
        self.filter_category.grid(row=0, column=1, padx=5)
        self.filter_category.set("Все")

        tk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w")
        self.filter_start = tk.Entry(filter_frame, width=12)
        self.filter_start.grid(row=0, column=3, padx=5)
        self.filter_start.insert(0, "")

        tk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w")
        self.filter_end = tk.Entry(filter_frame, width=12)
        self.filter_end.grid(row=0, column=5, padx=5)
        self.filter_end.insert(0, "")

        btn_filter = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        btn_filter.grid(row=0, column=6, padx=10)
        
        self.lbl_total = tk.Label(filter_frame, text="Итого: 0.00 руб.", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_total.grid(row=0, column=7, padx=10)

        # Таблица (Treeview)
        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма")
        
        self.tree.column("date", width=100)
        self.tree.column("category", width=150)
        self.tree.column("amount", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Кнопка сброса
        btn_reset = tk.Button(root, text="Сбросить фильтр", command=self.reset_filter)
        btn_reset.pack(pady=5)

        # Загрузка данных при старте
        self.refresh_table()

    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            return None

    def add_expense(self):
        amount_str = self.entry_amount.get().strip()
        category = self.entry_category.get()
        date_str = self.entry_date.get().strip()

        # Валидация
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
            return

        date_obj = self.validate_date(date_str)
        if not date_obj:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return

        # Добавление в список
        self.expenses.append({
            "date": date_str,
            "category": category,
            "amount": amount
        })
        
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.focus()

    def apply_filter(self):
        self.refresh_table()

    def reset_filter(self):
        self.filter_category.set("Все")
        self.filter_start.delete(0, tk.END)
        self.filter_end.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение фильтров
        cat_filter = self.filter_category.get()
        start_str = self.filter_start.get().strip()
        end_str = self.filter_end.get().strip()

        total = 0.0

        for exp in self.expenses:
            # Фильтр по категории
            if cat_filter != "Все" and exp["category"] != cat_filter:
                continue

            # Фильтр по дате
            exp_date = self.validate_date(exp["date"])
            if not exp_date:
                continue

            if start_str:
                start_date = self.validate_date(start_str)
                if start_date and exp_date < start_date:
                    continue
            
            if end_str:
                end_date = self.validate_date(end_str)
                if end_date and exp_date > end_date:
                    continue

            # Если прошли фильтры
            self.tree.insert("", tk.END, values=(exp["date"], exp["category"], f"{exp['amount']:.2f}"))
            total += exp["amount"]

        self.lbl_total.config(text=f"Итого: {total:.2f} руб.")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except json.JSONDecodeError:
                self.expenses = []
                messagebox.showwarning("Предупреждение", "Файл данных поврежден, создан новый.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
