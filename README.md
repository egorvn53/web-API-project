# 📚 Personal Collection Manager

Web API сервис для управления личной коллекцией (книги, видеоигры, фильмы и другое).

## 🎯 Функционал

- ✅ Добавление новых предметов в коллекцию
- ✅ Редактирование информации о предметах
- ✅ Удаление предметов
- ✅ Поиск по названию
- ✅ Фильтрация по типу (книги, игры, фильмы)
- ✅ Оценивание предметов (0-10)
- ✅ Отслеживание статуса (не начинал, в процессе, завершено)
- ✅ Добавление заметок

## 🛠 Технологии

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript (Bootstrap)
- **API:** REST

## 📦 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/egorvn53/web-API-project.git
cd web-API-project
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Запуск приложения
```bash
python app.py
```

Приложение будет доступно на `http://localhost:5000`

## 🔌 API Endpoints

### GET /api/items
Получить все предметы

**Query Parameters:**
- `search` (optional) - поиск по названию
- `type` (optional) - фильтр по типу (book, game, movie, other)

**Пример:**
```bash
curl http://localhost:5000/api/items?search=Harry&type=book
```

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Harry Potter",
    "item_type": "book",
    "author": "J.K. Rowling",
    "genre": "Fantasy",
    "status": "completed",
    "rating": 9.5,
    "notes": "Amazing series!",
    "created_at": "2026-04-21T12:00:00"
  }
]
```

### POST /api/items
Добавить новый предмет

**Body:**
```json
{
  "title": "The Witcher 3",
  "item_type": "game",
  "author": "CD Projekt Red",
  "genre": "RPG",
  "status": "in_progress",
  "rating": 9.0,
  "notes": "Epic gaming experience"
}
```

**Ответ:** 201 Created

### GET /api/items/<id>
Получить конкретный предмет

**Пример:**
```bash
curl http://localhost:5000/api/items/1
```

### PUT /api/items/<id>
Обновить предмет

**Body:** (любые поля для обновления)
```json
{
  "status": "completed",
  "rating": 10
}
```

### DELETE /api/items/<id>
Удалить предмет

```bash
curl -X DELETE http://localhost:5000/api/items/1
```

## 📋 Структура данных

Каждый предмет содержит:
- `id` - уникальный идентификатор
- `title` - название предмета
- `item_type` - тип (book, game, movie, other)
- `author` - автор/разработчик
- `genre` - жанр
- `status` - статус (not_started, in_progress, completed)
- `rating` - оценка (0-10)
- `notes` - заметки
- `created_at` - дата создания

## 🎨 Frontend

Интуитивный веб-интерфейс с:
- Формой для добавления новых предметов
- Таблицей со всеми предметами
- Поиском и фильтрацией в реальном времени
- Кнопками для удаления предметов
- Красивым дизайном на Bootstrap

## 📝 Примеры использования

### Добавить книгу
```javascript
fetch('http://localhost:5000/api/items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: "1984",
    item_type: "book",
    author: "George Orwell",
    genre: "Dystopian",
    status: "completed",
    rating: 8.5,
    notes: "Thought-provoking"
  })
})
```

### Получить все игры
```javascript
fetch('http://localhost:5000/api/items?type=game')
  .then(r => r.json())
  .then(data => console.log(data))
```

## 🐛 Troubleshooting

**Порт 5000 уже используется:**
```bash
python app.py --port 5001
```

**Ошибка подключения к БД:**
Удалите файл `collection.db` и запустите приложение заново.

## 📄 Лицензия

MIT

---

**Автор:** egorvn53  
**Проект для:** Yandex Liceum
