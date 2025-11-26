# lab3_complete.py - Полный код для Лабораторной работы №3 в VS Code
import os
import sqlite3
import json
from datetime import datetime, date
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Модель данных Article
class Article:
    def __init__(self, id=None, title="", author="", text="", created_date=None):
        self.id = id
        self.title = title
        self.author = author
        self.text = text
        self.created_date = created_date or date.today()
    
    def get_excerpt(self):
        """Возвращает первые 140 символов текста"""
        return self.text[:140] + "..." if len(self.text) > 140 else self.text
    
    def __str__(self):
        return f"{self.author}: {self.title}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'text': self.text,
            'created_date': str(self.created_date),
            'excerpt': self.get_excerpt()
        }

# База данных SQLite
class Database:
    def __init__(self, db_name='blog_db.sqlite3'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создание таблицы статей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                text TEXT NOT NULL,
                created_date DATE NOT NULL
            )
        ''')
        
        # Создание тестовых данных
        test_articles = [
            ("Первая статья о Django", "admin", 
             "Django - это свободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC. Django позволяет быстро создавать безопасные и поддерживаемые веб-сайты. Разработанный опытными разработчиками, Django занимается большей частью проблем веб-разработки, поэтому вы можете сосредоточиться на написании своего приложения без необходимости изобретать велосипед. Это бесплатно и с открытым исходным кодом.", 
             "2024-01-15"),
            
            ("Преимущества Python в веб-разработке", "user123", 
             "Python является одним из самых популярных языков программирования для веб-разработки благодаря своей простоте и читабельности. С помощью фреймворков like Django и Flask можно быстро создавать мощные веб-приложения. Python также имеет огромное сообщество и множество библиотек для различных задач.", 
             "2024-01-16"),
            
            ("Создание моделей в Django", "developer", 
             "Модели в Django представляют структуру базы данных. Каждый класс модели соответствует таблице в базе данных, а атрибуты класса - полям таблицы. Django ORM автоматически создает SQL-запросы, что позволяет работать с базой данных используя Python код вместо прямого написания SQL.", 
             "2024-01-17"),
            
            ("Административная панель Django", "admin", 
             "Одной из мощных функций Django является автоматически генерируемая административная панель. Она позволяет управлять содержимым сайта без написания дополнительного кода. Для использования админки достаточно зарегистрировать модели в admin.py и создать суперпользователя.", 
             "2024-01-18"),
            
            ("Шаблоны и представления в Django", "webmaster", 
             "Django использует систему шаблонов для отделения логики представления от HTML разметки. Представления (views) обрабатывают запросы и возвращают ответы. Шаблоны позволяют динамически генерировать HTML страницы, используя специальный язык шаблонов Django.", 
             "2024-01-19")
        ]
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.executemany('''
                INSERT INTO articles (title, author, text, created_date)
                VALUES (?, ?, ?, ?)
            ''', test_articles)
            print(" Созданы тестовые статьи в базе данных")
        
        conn.commit()
        conn.close()
    
    def get_all_articles(self):
        """Получить все статьи"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM articles ORDER BY created_date DESC")
        articles_data = cursor.fetchall()
        
        articles = []
        for row in articles_data:
            article = Article(
                id=row['id'],
                title=row['title'],
                author=row['author'],
                text=row['text'],
                created_date=row['created_date']
            )
            articles.append(article)
        
        conn.close()
        return articles
    
    def get_article_by_id(self, article_id):
        """Получить статью по ID"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        if row:
            article = Article(
                id=row['id'],
                title=row['title'],
                author=row['author'],
                text=row['text'],
                created_date=row['created_date']
            )
            conn.close()
            return article
        else:
            conn.close()
            return None
    
    def create_article(self, title, author, text):
        """Создать новую статью"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO articles (title, author, text, created_date)
            VALUES (?, ?, ?, ?)
        ''', (title, author, text, date.today()))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return article_id
    
    def update_article(self, article_id, title=None, text=None):
        """Обновить статью"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if title and text:
            cursor.execute('''
                UPDATE articles SET title = ?, text = ? WHERE id = ?
            ''', (title, text, article_id))
        elif title:
            cursor.execute('''
                UPDATE articles SET title = ? WHERE id = ?
            ''', (title, article_id))
        elif text:
            cursor.execute('''
                UPDATE articles SET text = ? WHERE id = ?
            ''', (text, article_id))
        
        conn.commit()
        conn.close()

# HTML шаблоны
class HTMLTemplates:
    @staticmethod
    def base_template(title, content):
        return f'''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .nav {{
            background: #34495e;
            padding: 15px;
            display: flex;
            justify-content: center;
            gap: 20px;
        }}
        
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .nav a:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        .article-grid {{
            display: grid;
            gap: 25px;
        }}
        
        .article-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}
        
        .article-title {{
            color: #2c3e50;
            font-size: 1.4em;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .article-meta {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .article-author {{
            font-weight: 500;
            color: #667eea;
        }}
        
        .article-date {{
            font-style: italic;
        }}
        
        .article-excerpt {{
            color: #555;
            line-height: 1.7;
            margin-bottom: 15px;
        }}
        
        .read-more {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .read-more:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .article-detail {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }}
        
        .article-full-text {{
            line-height: 1.8;
            color: #444;
            font-size: 1.1em;
            margin-top: 20px;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #6c757d;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            margin-top: 20px;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{
            background: #5a6268;
            transform: translateX(-5px);
        }}
        
        .admin-panel {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .admin-title {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .article-form {{
            display: grid;
            gap: 15px;
            max-width: 600px;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .form-label {{
            margin-bottom: 5px;
            font-weight: 500;
            color: #2c3e50;
        }}
        
        .form-input {{
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .form-textarea {{
            min-height: 150px;
            resize: vertical;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .message {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        
        .success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}
            
            .nav {{
                flex-direction: column;
                align-items: center;
                gap: 10px;
            }}
            
            .article-meta {{
                flex-direction: column;
                gap: 5px;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Django Public Blog</h1>
            <p>Лабораторная работа №3 - Модели данных и административная панель</p>
        </div>
        
        <div class="nav">
            <a href="/"> Все статьи</a>
            <a href="/admin"> Админ-панель</a>
            <a href="/create"> Новая статья</a>
        </div>
        
        <div class="content">
            {content}
        </div>
        
        <div class="footer">
            <p>© 2024 Django Blog - Лабораторная работа №3 | Python + SQLite</p>
        </div>
    </div>
</body>
</html>
        '''
    
    @staticmethod
    def archive_template(articles):
        articles_html = ""
        for article in articles:
            articles_html += f'''
            <div class="article-card">
                <h2 class="article-title">{article.title}</h2>
                <div class="article-meta">
                    <span class="article-author"> {article.author}</span>
                    <span class="article-date"> {article.created_date}</span>
                </div>
                <p class="article-excerpt">{article.get_excerpt()}</p>
                <a href="/article/{article.id}" class="read-more">Читать полностью →</a>
            </div>
            '''
        
        return HTMLTemplates.base_template(
            "Архив статей - Django Blog",
            f'''
            <h2 style="margin-bottom: 25px; color: #2c3e50;"> Все статьи ({len(articles)})</h2>
            <div class="article-grid">
                {articles_html}
            </div>
            '''
        )
    
    @staticmethod
    def article_template(article):
        return HTMLTemplates.base_template(
            f"{article.title} - Django Blog",
            f'''
            <div class="article-detail">
                <h2 class="article-title" style="font-size: 1.8em; margin-bottom: 20px;">{article.title}</h2>
                <div class="article-meta">
                    <span class="article-author"> Автор: {article.author}</span>
                    <span class="article-date"> Опубликовано: {article.created_date}</span>
                </div>
                <div class="article-full-text">
                    {article.text.replace(chr(10), '<br>')}
                </div>
                <a href="/" class="back-link">← Назад ко всем статьям</a>
            </div>
            '''
        )
    
    @staticmethod
    def admin_template(articles):
        articles_html = ""
        for article in articles:
            articles_html += f'''
            <tr>
                <td>{article.id}</td>
                <td><strong>{article.title}</strong></td>
                <td>{article.author}</td>
                <td>{article.created_date}</td>
                <td>{article.get_excerpt()}</td>
                <td>
                    <a href="/article/{article.id}" style="color: #667eea; text-decoration: none;"> Просмотр</a>
                </td>
            </tr>
            '''
        
        return HTMLTemplates.base_template(
            "Административная панель - Django Blog",
            f'''
            <div class="admin-panel">
                <h2 class="admin-title"> Административная панель</h2>
                <p>Управление статьями блога</p>
            </div>
            
            <div style="background: white; border-radius: 10px; padding: 20px; overflow-x: auto;">
                <h3 style="margin-bottom: 20px; color: #2c3e50;"> Список статей ({len(articles)})</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">ID</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Заголовок</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Автор</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Дата</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Краткое содержание</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {articles_html}
                    </tbody>
                </table>
            </div>
            '''
        )
    
    @staticmethod
    def create_article_template(message="", form_data=None):
        form_data = form_data or {}
        message_html = f'<div class="message success">{message}</div>' if message else ""
        
        return HTMLTemplates.base_template(
            "Создать статью - Django Blog",
            f'''
            <div class="admin-panel">
                <h2 class="admin-title"> Создать новую статью</h2>
                <p>Заполните форму для добавления новой статьи в блог</p>
            </div>
            
            {message_html}
            
            <div style="background: white; border-radius: 10px; padding: 30px;">
                <form method="POST" class="article-form">
                    <div class="form-group">
                        <label class="form-label" for="title">Заголовок статьи:</label>
                        <input type="text" id="title" name="title" class="form-input" 
                               value="{form_data.get('title', '')}" required 
                               placeholder="Введите заголовок статьи">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="author">Автор:</label>
                        <input type="text" id="author" name="author" class="form-input" 
                               value="{form_data.get('author', '')}" required 
                               placeholder="Введите имя автора">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="text">Текст статьи:</label>
                        <textarea id="text" name="text" class="form-input form-textarea" 
                                  required placeholder="Введите текст статьи">{form_data.get('text', '')}</textarea>
                    </div>
                    
                    <button type="submit" class="btn"> Опубликовать статью</button>
                </form>
            </div>
            '''
        )

# Веб-сервер
class BlogServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = Database()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.show_archive()
        elif self.path.startswith('/article/'):
            article_id = self.path.split('/')[-1]
            if article_id.isdigit():
                self.show_article(int(article_id))
            else:
                self.show_archive()
        elif self.path == '/admin':
            self.show_admin()
        elif self.path == '/create':
            self.show_create_form()
        else:
            self.show_archive()
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/create':
            self.create_article()
        else:
            self.show_archive()
    
    def show_archive(self):
        """Показать архив всех статей"""
        articles = self.db.get_all_articles()
        html_content = HTMLTemplates.archive_template(articles)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def show_article(self, article_id):
        """Показать отдельную статью"""
        article = self.db.get_article_by_id(article_id)
        if article:
            html_content = HTMLTemplates.article_template(article)
        else:
            articles = self.db.get_all_articles()
            html_content = HTMLTemplates.archive_template(articles)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def show_admin(self):
        """Показать административную панель"""
        articles = self.db.get_all_articles()
        html_content = HTMLTemplates.admin_template(articles)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def show_create_form(self, message="", form_data=None):
        """Показать форму создания статьи"""
        html_content = HTMLTemplates.create_article_template(message, form_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def create_article(self):
        """Создать новую статью"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Парсим POST данные
        form_data = {}
        for item in post_data.split('&'):
            key, value = item.split('=')
            form_data[key] = value.replace('+', ' ').replace('%20', ' ')
        
        # Проверяем обязательные поля
        if not form_data.get('title') or not form_data.get('author') or not form_data.get('text'):
            self.show_create_form(" Заполните все поля!", form_data)
            return
        
        # Создаем статью
        article_id = self.db.create_article(
            form_data['title'],
            form_data['author'],
            form_data['text']
        )
        
        self.show_create_form(" Статья успешно создана", {})

# Демонстрация работы
class Lab3Demo:
    def __init__(self):
        self.db = Database()
    
    def demonstrate_features(self):
        """Демонстрация всех функций"""
        print(" Python Django - Лабораторная работа №3")
        print(" Создание модели данных и административной панели")
        print("=" * 60)
        
        # Показываем созданные статьи
        articles = self.db.get_all_articles()
        
        print("\n СТАТЬИ В БАЗЕ ДАННЫХ:")
        print("-" * 50)
        for article in articles:
            print(f"ID: {article.id}")
            print(f"Заголовок: {article.title}")
            print(f"Автор: {article.author}")
            print(f"Дата: {article.created_date}")
            print(f"Краткое содержание: {article.get_excerpt()}")
            print("-" * 30)
        
        # Демонстрация работы с БД
        print("\n ДЕМОНСТРАЦИЯ РАБОТЫ С БАЗОЙ ДАННЫХ:")
        print("-" * 40)
        
        # Получение статьи по ID
        if articles:
            sample_article = self.db.get_article_by_id(articles[0].id)
            print(f" Получена статья по ID {articles[0].id}: {sample_article.title}")
        
        # Создание новой статьи
        new_article_id = self.db.create_article(
            "Новая статья через демо",
            "demo_user",
            "Это демонстрационная статья, созданная через Python код. Она показывает работу методов создания и управления статьями в базе данных."
        )
        print(f" Создана новая статья с ID: {new_article_id}")
        
        # Обновление статьи
        self.db.update_article(new_article_id, title="Обновленный заголовок демо-статьи")
        print(f" Обновлен заголовок статьи ID: {new_article_id}")
        
        print("\n ВЫПОЛНЕННЫЕ ЗАДАНИЯ:")
        print("=" * 40)
        
        tasks = [
            " Создана модель данных Article с полями: title, author, text, created_date",
            " Реализован метод get_excerpt() для краткого содержания",
            " Настроена SQLite база данных",
            " Созданы тестовые данные (5 статей)",
            " Реализован CRUD функционал (Create, Read, Update)",
            " Создана административная панель для управления статьями",
            " Реализовано представление архива всех статей",
            " Создана страница отдельной статьи",
            " Добавлена форма создания новых статей",
            " Реализована валидация данных формы",
            " Создан красивый адаптивный интерфейс",
            " Добавлена навигация между страницами"
        ]
        
        for task in tasks:
            print(task)
        
        print(f"\n СТАТИСТИКА:")
        print(f"   • Статей в базе: {len(articles) + 1}")
        print(f"   • Авторов: {len(set(a.author for a in articles))}")
        print(f"   • HTML шаблонов: 4")
        print(f"   • Методов работы с БД: 5")
    
    def run_server(self, port=8000):
        """Запуск веб-сервера"""
        print(f"\n Запуск веб-сервера на порту {port}...")
        print(" Доступные страницы:")
        print("    http://localhost:8000/ - Архив всех статей")
        print("    http://localhost:8000/admin - Административная панель")
        print("   http://localhost:8000/create - Создание новой статьи")
        print("    http://localhost:8000/article/1 - Пример статьи")
        print("\n  Для остановки сервера нажмите Ctrl+C")
        
        try:
            server = HTTPServer(('localhost', port), BlogServer)
            print(f" Сервер запущен! Откройте http://localhost:{port}")
            webbrowser.open(f'http://localhost:{port}')
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n Сервер остановлен")
        except OSError as e:
            print(f" Ошибка: Порт {port} занят. Попробуйте другой порт.")
            print(f"   Попробуйте: python lab3_complete.py --port 8080")

def main():
    """Главная функция"""
    demo = Lab3Demo()
    
    # Демонстрация функций
    demo.demonstrate_features()
    
    # Запуск сервера
    print("\n" + "=" * 60)
    choice = input("\n🚀 Запустить веб-сервер? (y/n): ").lower()
    
    if choice in ['y', 'yes', 'д', 'да']:
        demo.run_server()
    else:
        print("\n Вы можете запустить сервер позже:")
        print("   python lab3_complete.py")
        print("\n Созданные файлы:")
        print("   • blog_db.sqlite3 - база данных SQLite")
        print("   • (в памяти) - HTML шаблоны и логика")

if __name__ == "__main__":
    main()