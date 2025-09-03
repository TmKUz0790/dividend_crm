# Отображение всех задач

**GET /api/sales-funnel-tasks/**

Возвращает список всех задач с их полями (client, varonka, title, status и др.).

Пример запроса:
```
GET http://<ваш_домен>/api/sales-funnel-tasks/
```

Пример ответа:
```
[
  {
    "id": 1,
    "client": 2,
    "varonka": 1,
    "title": "Позвонить клиенту",
    "status": "new"
    // ... другие поля ...
  },
  ...
]
```

---

# Создание новой задачи

**POST /api/sales-funnel-tasks/**

Создаёт новую задачу. Укажите id клиента (Application), id этапа (Varonka), название и статус.

Пример запроса:
```
POST http://<ваш_домен>/api/sales-funnel-tasks/
Content-Type: application/json

{
  "client": 2,
  "varonka": 1,
  "title": "Позвонить клиенту",
  "status": "new"
}
```

Пример ответа:
```
{
  "id": 5,
  "client": 2,
  "varonka": 1,
  "title": "Позвонить клиенту",
  "status": "new"
  // ... другие поля ...
}
```

---

**Примечание:**
- client — id существующего клиента (Application)
- varonka — id существующего этапа (Varonka)
- status — "new", "in_progress" или "done"
# API Kanban Board Documentation

## Эндпоинт: Kanban Board

**GET /api/board/**

Возвращает список этапов (Varonka) и задачи (SalesFunnelTask), сгруппированные по статусу:
- `new`
- `in_progress`
- `done`

### Пример ответа
```
[
  {
    "id": 1,
    "name": "Название этапа",
    "tasks": {
      "new": [ ...список задач... ],
      "in_progress": [ ...список задач... ],
      "done": [ ...список задач... ]
    }
  },
  ...
]
```

Каждая задача содержит все поля SalesFunnelTask, включая client, title, status, varonka и детали.

---

## Как менять статус задачи

1. Получите id задачи (SalesFunnelTask) из ответа `/api/board/`.
2. Отправьте PATCH/PUT-запрос на эндпоинт задачи:
   
   `PATCH /api/sales-funnel-tasks/{id}/`
   
   Тело запроса:
   ```json
   {
     "status": "in_progress" // или "done", "new"
   }
   ```
3. После успешного запроса задача появится в соответствующей колонке на доске.

---

## Прочие действия

- **Создать задачу:**  
  `POST /api/sales-funnel-tasks/`  
  Укажите client (id Application), varonka (id Varonka), title, status.

- **Изменить задачу:**  
  `PATCH/PUT /api/sales-funnel-tasks/{id}/`  
  Можно менять любые поля задачи.

- **Удалить задачу:**  
  `DELETE /api/sales-funnel-tasks/{id}/`

---

## Примечания
- Статус задачи определяет её положение на доске.
- Клиент и этап выбираются из существующих Application и Varonka.

---

Если нужна OpenAPI/Swagger-версия или примеры запросов — сообщите!
