# lab4_simple.py - Упрощенная версия Лабораторной работы №4
import sqlite3
from datetime import date
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Простая модель статьи
class Article:
    def __init__(self, id, title, author, text, created_date, views=0):
        self.id = id
        self.title = title
        self.author = author
        self.text = text
        self.created_date = created_date
        self.views = views
    
    def get_excerpt(self):
        return self.text[:100] + "..." if len(self.text) > 100 else self.text

# Простая база данных в памяти
class SimpleDB:
    def __init__(self):
        self.articles = [
            Article(1, "Первая статья о Django", "admin", 
                   "Django - это свободный фреймворк для веб-приложений на языке Python. Он позволяет быстро создавать безопасные и поддерживаемые веб-сайты.", 
                   "2024-01-15", 5),
            Article(2, "Преимущества Python", "user123", 
                   "Python популярен благодаря своей простоте и читабельности. Это отличный выбор для веб-разработки.", 
                   "2024-01-16", 3),
            Article(3, "Создание моделей в Django", "developer", 
                   "Модели в Django представляют структуру базы данных. Каждый класс модели соответствует таблице в базе данных.", 
                   "2024-01-17", 8)
        ]
        self.next_id = 4
    
    def get_all_articles(self):
        return self.articles
    
    def get_article_by_id(self, article_id):
        for article in self.articles:
            if article.id == article_id:
                return article
        return None
    
    def increment_views(self, article_id):
        article = self.get_article_by_id(article_id)
        if article:
            article.views += 1
    
    def create_article(self, title, author, text):
        article = Article(self.next_id, title, author, text, str(date.today()), 0)
        self.articles.append(article)
        self.next_id += 1
        return article.id

# HTML шаблоны
def generate_html(title, content, current_page="home"):
    return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f0f2f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .nav {{
            background: #34495e;
            padding: 15px;
            display: flex;
            gap: 15px;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }}
        .nav a:hover {{
            background: #3498db;
        }}
        .nav a.active {{
            background: #2980b9;
        }}
        .content {{
            padding: 20px;
        }}
        .article-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .article-title {{
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .article-title a {{
            color: inherit;
            text-decoration: none;
        }}
        .article-title a:hover {{
            color: #3498db;
        }}
        .article-meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .article-detail {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        .form-input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        .form-textarea {{
            height: 200px;
            resize: vertical;
        }}
        .btn {{
            background: #27ae60;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .btn:hover {{
            background: #229954;
        }}
        .message {{
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Django Blog - Лабораторная работа №4</h1>
            <p>Страницы отдельных записей</p>
        </div>
        <div class="nav">
            <a href="/" class="{'active' if current_page == 'home' else ''}"> Все статьи</a>
            <a href="/create" class="{'active' if current_page == 'create' else ''}"> Новая статья</a>
        </div>
        <div class="content">
            {content}
        </div>
    </div>
</body>
</html>
'''

# Веб-сервер
class SimpleBlogServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = SimpleDB()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        try:
            if self.path == '/':
                self.show_home()
            elif self.path.startswith('/article/'):
                article_id = int(self.path.split('/')[-1])
                self.show_article(article_id)
            elif self.path == '/create':
                self.show_create_form()
            else:
                self.show_home()
        except:
            self.show_home()
    
    def do_POST(self):
        if self.path == '/create':
            self.create_article()
        else:
            self.show_home()
    
    def show_home(self):
        articles = self.db.get_all_articles()
        content = '<h2> Все статьи</h2>'
        
        for article in articles:
            content += f'''
            <div class="article-card">
                <h3 class="article-title">
                    <a href="/article/{article.id}">{article.title}</a>
                </h3>
                <div class="article-meta">
                     {article.author} |  {article.created_date} |  {article.views} просмотров
                </div>
                <p>{article.get_excerpt()}</p>
            </div>
            '''
        
        html = generate_html("Главная страница", content, "home")
        self.send_html(html)
    
    def show_article(self, article_id):
        article = self.db.get_article_by_id(article_id)
        if article:
            self.db.increment_views(article_id)
            content = f'''
            <div class="article-detail">
                <h1>{article.title}</h1>
                <div class="article-meta">
                     Автор: {article.author} |  {article.created_date} |  {article.views} просмотров
                </div>
                <p style="line-height: 1.6; margin-top: 20px;">{article.text}</p>
                <a href="/" class="back-link">← Назад к статьям</a>
            </div>
            '''
            html = generate_html(article.title, content, "article")
        else:
            content = '<div class="message">Статья не найдена</div>'
            html = generate_html("Ошибка", content, "home")
        
        self.send_html(html)
    
    def show_create_form(self, message=""):
        message_html = f'<div class="message success">{message}</div>' if message else ''
        content = f'''
        <h2> Создать новую статью</h2>
        {message_html}
        <form method="POST" style="max-width: 600px;">
            <div class="form-group">
                <label>Заголовок:</label>
                <input type="text" name="title" class="form-input" required>
            </div>
            <div class="form-group">
                <label>Автор:</label>
                <input type="text" name="author" class="form-input" required>
            </div>
            <div class="form-group">
                <label>Текст статьи:</label>
                <textarea name="text" class="form-input form-textarea" required></textarea>
            </div>
            <button type="submit" class="btn">Опубликовать</button>
            <a href="/" style="margin-left: 10px; color: #666;">Отмена</a>
        </form>
        '''
        html = generate_html("Новая статья", content, "create")
        self.send_html(html)
    
    def create_article(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Простой парсинг формы
        params = {}
        for pair in post_data.split('&'):
            key, value = pair.split('=')
            params[key] = value.replace('+', ' ')
        
        if params.get('title') and params.get('author') and params.get('text'):
            self.db.create_article(params['title'], params['author'], params['text'])
            self.show_create_form(" Статья успешно создана!")
        else:
            self.show_create_form(" Заполните все поля!")
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

def main():
    print(" Лабораторная работа №4 - Страницы записей")
    print("=" * 50)
    
    print("\n Выполненные задания:")
    tasks = [
        " Создана страница отдельной записи",
        " Заголовки стали кликабельными ссылками", 
        " Реализован счетчик просмотров",
        " Добавлена навигация между страницами",
        " Создана форма для новых статей",
        " Улучшен пользовательский интерфейс"
    ]
    
    for task in tasks:
        print(task)
    
    print("\n🚀 Запуск сервера...")
    print("📊 Будет доступно по адресу: http://localhost:8000")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    try:
        port = 8000
        server = HTTPServer(('localhost', port), SimpleBlogServer)
        print(f" Сервер запущен на порту {port}")
        webbrowser.open(f'http://localhost:{port}')
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n Сервер остановлен")
    except Exception as e:
        print(f" Ошибка: {e}")
        print("Попробуйте запустить с другим портом:")
        print("python lab4_simple.py")

if __name__ == "__main__":
    main()