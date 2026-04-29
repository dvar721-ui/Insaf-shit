import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re


class MovieLibrary:
    """Главный класс приложения для управления личной кинотекой"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Файл для хранения данных
        self.data_file = "movies.json"
        
        # Загружаем данные
        self.movies = self.load_movies()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Обновляем таблицу
        self.refresh_table()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса колонок
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ===== Панель ввода данных =====
        input_frame = ttk.LabelFrame(main_frame, text="Добавление фильма", padding="10")
        input_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Поле: Название
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(input_frame, textvariable=self.title_var, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Поле: Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.genre_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(input_frame, textvariable=self.genre_var, width=28)
        self.genre_combo['values'] = ('Драма', 'Комедия', 'Боевик', 'Триллер', 'Ужасы', 
                                       'Фантастика', 'Фэнтези', 'Мелодрама', 'Детектив', 
                                       'Приключения', 'Анимация', 'Документальный')
        self.genre_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Поле: Год выпуска
        ttk.Label(input_frame, text="Год выпуска:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.year_var = tk.StringVar()
        self.year_entry = ttk.Entry(input_frame, textvariable=self.year_var, width=30)
        self.year_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Поле: Рейтинг
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.rating_var = tk.StringVar()
        self.rating_entry = ttk.Entry(input_frame, textvariable=self.rating_var, width=30)
        self.rating_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="➕ Добавить фильм", command=self.add_movie)
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # ===== Панель фильтрации =====
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, padx=(0, 10))
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, width=20)
        self.filter_genre_combo['values'] = ['Все'] + list(self.genre_combo['values'])
        self.filter_genre_combo.grid(row=0, column=1, padx=(0, 20))
        self.filter_genre_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Фильтр по году (диапазон)
        ttk.Label(filter_frame, text="Год от:").grid(row=0, column=2, padx=(0, 10))
        self.year_from_var = tk.StringVar()
        self.year_from_entry = ttk.Entry(filter_frame, textvariable=self.year_from_var, width=8)
        self.year_from_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=(0, 10))
        self.year_to_var = tk.StringVar()
        self.year_to_entry = ttk.Entry(filter_frame, textvariable=self.year_to_var, width=8)
        self.year_to_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Кнопка применения фильтра
        self.apply_btn = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filters)
        self.apply_btn.grid(row=0, column=6, padx=(10, 0))
        
        # Кнопка сброса фильтра
        self.reset_btn = ttk.Button(filter_frame, text="🗑️ Сбросить фильтр", command=self.reset_filters)
        self.reset_btn.grid(row=0, column=7, padx=(10, 0))
        
        # ===== Таблица с фильмами =====
        table_frame = ttk.LabelFrame(main_frame, text="Список фильмов", padding="10")
        table_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Создание таблицы
        columns = ('ID', 'Название', 'Жанр', 'Год', 'Рейтинг')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Жанр', text='Жанр')
        self.tree.heading('Год', text='Год')
        self.tree.heading('Рейтинг', text='Рейтинг')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Название', width=250)
        self.tree.column('Жанр', width=120)
        self.tree.column('Год', width=80, anchor='center')
        self.tree.column('Рейтинг', width=80, anchor='center')
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.delete_btn = ttk.Button(btn_frame, text="❌ Удалить выбранный", command=self.delete_movie)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Сохранить", command=self.save_movies)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готово")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def validate_movie(self, title, genre, year, rating):
        """
        Валидация введенных данных
        
        Возвращает: (is_valid, error_message)
        """
        if not title or not title.strip():
            return False, "Название фильма не может быть пустым!"
        
        if not genre:
            return False, "Выберите жанр фильма!"
        
        # Проверка года
        if not year:
            return False, "Введите год выпуска!"
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888:  # Первый фильм в истории
                return False, f"Год должен быть не меньше 1888!"
            if year_int > current_year:
                return False, f"Год не может быть больше текущего ({current_year})!"
        except ValueError:
            return False, "Год должен быть целым числом!"
        
        # Проверка рейтинга
        if not rating:
            return False, "Введите рейтинг!"
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                return False, "Рейтинг должен быть в диапазоне от 0 до 10!"
        except ValueError:
            return False, "Рейтинг должен быть числом!"
        
        return True, ""
    
    def add_movie(self):
        """Добавление нового фильма"""
        title = self.title_var.get().strip()
        genre = self.genre_var.get()
        year = self.year_var.get().strip()
        rating = self.rating_var.get().strip()
        
        # Валидация
        is_valid, error_msg = self.validate_movie(title, genre, year, rating)
        
        if not is_valid:
            messagebox.showerror("Ошибка ввода", error_msg)
            return
        
        # Генерация ID
        movie_id = max([m['id'] for m in self.movies], default=0) + 1
        
        # Добавление фильма
        movie = {
            'id': movie_id,
            'title': title,
            'genre': genre,
            'year': int(year),
            'rating': float(rating)
        }
        
        self.movies.append(movie)
        self.save_movies()
        self.refresh_table()
        
        # Очистка полей
        self.title_var.set("")
        self.genre_var.set("")
        self.year_var.set("")
        self.rating_var.set("")
        
        self.status_var.set(f"Фильм '{title}' успешно добавлен!")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return
        
        # Получение ID фильма
        item = self.tree.item(selected[0])
        movie_id = item['values'][0]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот фильм?"):
            # Удаление из списка
            self.movies = [m for m in self.movies if m['id'] != movie_id]
            self.save_movies()
            self.refresh_table()
            self.status_var.set("Фильм успешно удален!")
    
    def load_movies(self):
        """Загрузка фильмов из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_movies(self):
        """Сохранение фильмов в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False
    
    def apply_filters(self, event=None):
        """Применение фильтров к таблице"""
        self.refresh_table(filtered=True)
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_genre_var.set("Все")
        self.year_from_var.set("")
        self.year_to_var.set("")
        self.refresh_table()
        self.status_var.set("Фильтры сброшены")
    
    def refresh_table(self, filtered=False):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение данных
        movies_to_show = self.movies.copy()
        
        # Применение фильтров
        if filtered:
            # Фильтр по жанру
            selected_genre = self.filter_genre_var.get()
            if selected_genre != "Все":
                movies_to_show = [m for m in movies_to_show if m['genre'] == selected_genre]
            
            # Фильтр по году (диапазон)
            year_from = self.year_from_var.get().strip()
            year_to = self.year_to_var.get().strip()
            
            if year_from:
                try:
                    year_from_int = int(year_from)
                    movies_to_show = [m for m in movies_to_show if m['year'] >= year_from_int]
                except ValueError:
                    pass
            
            if year_to:
                try:
                    year_to_int = int(year_to)
                    movies_to_show = [m for m in movies_to_show if m['year'] <= year_to_int]
                except ValueError:
                    pass
        
        # Сортировка по ID
        movies_to_show.sort(key=lambda x: x['id'])
        
        # Заполнение таблицы
        for movie in movies_to_show:
            self.tree.insert('', tk.END, values=(
                movie['id'],
                movie['title'],
                movie['genre'],
                movie['year'],
                f"{movie['rating']:.1f}"
            ))
        
        # Обновление статуса
        self.status_var.set(f"Показано фильмов: {len(movies_to_show)} из {len(self.movies)}")


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()


if __name__ == "__main__":
    main()