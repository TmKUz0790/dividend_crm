# API Документация: Канбан-доска задач

## Endpoint
`GET /api/board/`

## Структура ответа
```
[
  {
    "id": 1,
    "name": "Этап 1",
    "tasks": {
      "new": [
        {
          "id": 101,
          "name": "Позвонить клиенту",
          "status": "new",
          "application_id": 201,
          "application_name": "ООО Ромашка"
        }
      ],
      "in_progress": [
        {
          "id": 102,
          "name": "Отправить КП",
          "status": "in_progress",
          "application_id": 202,
          "application_name": "ИП Иванов"
        }
      ],
      "done": [
        {
          "id": 103,
          "name": "Заключить договор",
          "status": "done",
          "application_id": 203,
          "application_name": "ООО Лето"
        }
      ]
    }
  },
  ...
]
```

## Описание полей
- `id`, `name` — этап (колонка).
- Внутри `tasks` — задачи, сгруппированные по статусу.
- У каждой задачи:
  - `id`, `name` — задача.
  - `status` — статус задачи (`new`, `in_progress`, `done`).
  - `application_id`, `application_name` — клиент, к которому относится задача.

## DnD (Drag & Drop)
- Перетаскивайте задачи между статусами внутри этапа.
- Для обновления статуса задачи используйте PATCH/PUT на endpoint задачи (например, `/api/tasks/{id}/`).

## Отображение клиента
- Используйте поля `application_id` и `application_name` в карточке задачи.

---
Если нужен пример запроса на обновление статуса или создание задачи — напишите!
