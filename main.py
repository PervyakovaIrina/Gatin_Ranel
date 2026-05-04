import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

DATA_FILE = "books.json"

# Загрузка книг из JSON
def load_books():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Сохранение книг в JSON
def save_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f, indent=2)

# Проверка корректности ввода
def validate_input():
    title = entry_title.get().strip()
    author = entry_author.get().strip()
    genre = entry_genre.get().strip()
    pages = entry_pages.get().strip()

    if not title or not author or not genre or not pages:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return False

    if not pages.isdigit():
        messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
        return False

    return True

# Добавление книги
def add_book():
    if not validate_input():
        return

    book = {
        "title": entry_title.get(),
        "author": entry_author.get(),
        "genre": entry_genre.get(),
        "pages": int(entry_pages.get())
    }

    books.append(book)
    save_books(books)
    update_treeview()
    clear_fields()

# Очистка полей ввода
def clear_fields():
    entry_title.delete(0, tk.END)
    entry_author.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_pages.delete(0, tk.END)

# Обновление таблицы (Treeview)
def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    for book in books:
        tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

# Фильтрация по жанру
def filter_by_genre():
    genre = entry_genre_filter.get().strip()
    filtered = [b for b in books if genre.lower() in b["genre"].lower()]
    update_treeview_with_list(filtered)

# Фильтрация по количеству страниц (больше N)
def filter_by_pages():
    value = entry_pages_filter.get().strip()
    if not value.isdigit():
        messagebox.showerror("Ошибка", "Введите число для фильтрации по страницам!")
        return
    filtered = [b for b in books if b["pages"] > int(value)]
    update_treeview_with_list(filtered)

# Вспомогательная функция для обновления таблицы с любым списком
def update_treeview_with_list(book_list):
    for i in tree.get_children():
        tree.delete(i)
    for book in book_list:
        tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

# Загрузка данных при старте
books = load_books()

# Создание окна
root = tk.Tk()
root.title("Book Tracker")
root.geometry("800x500")

# --- Поля ввода ---
tk.Label(root, text="Название").grid(row=0, column=0, padx=5, pady=5)
entry_title = tk.Entry(root, width=30)
entry_title.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Автор").grid(row=1, column=0, padx=5, pady=5)
entry_author = tk.Entry(root, width=30)
entry_author.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Жанр").grid(row=2, column=0, padx=5, pady=5)
entry_genre = tk.Entry(root, width=30)
entry_genre.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Страниц").grid(row=3, column=0, padx=5, pady=5)
entry_pages = tk.Entry(root, width=10)
entry_pages.grid(row=3, column=1, sticky="w", padx=5, pady=5)

btn_add = tk.Button(root, text="Добавить книгу", command=add_book)
btn_add.grid(row=4, column=0, columnspan=2, pady=10)

# --- Фильтрация ---
tk.Label(root, text="Фильтр по жанру").grid(row=5, column=0, padx=5, pady=5)
entry_genre_filter = tk.Entry(root, width=30)
entry_genre_filter.grid(row=5, column=1, padx=5, pady=5)
btn_filter_genre = tk.Button(root, text="Фильтровать", command=filter_by_genre)
btn_filter_genre.grid(row=6, column=0, columnspan=2, pady=5)

tk.Label(root, text="Фильтр по страницам (> N)").grid(row=7, column=0, padx=5, pady=5)
entry_pages_filter = tk.Entry(root, width=10)
entry_pages_filter.grid(row=7, column=1, sticky="w", padx=5, pady=5)
btn_filter_pages = tk.Button(root, text="Фильтровать", command=filter_by_pages)
btn_filter_pages.grid(row=8, column=0, columnspan=2, pady=5)

# --- Таблица (Treeview) ---
columns = ("title", "author", "genre", "pages")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("title", text="Название")
tree.heading("author", text="Автор")
tree.heading("genre", text="Жанр")
tree.heading("pages", text="Страниц")
tree.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Обновление таблицы при запуске
update_treeview()

root.mainloop()
