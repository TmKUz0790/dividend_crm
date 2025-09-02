# Kanban API Документация для фронта

## Эндпоинты

### 1. Этапы
- `GET /api/stages/` — список этапов
- `POST /api/stages/` — создать этап
- `GET /api/stages/{id}/` — получить этап
- `PUT/PATCH /api/stages/{id}/` — обновить этап
- `DELETE /api/stages/{id}/` — удалить этап

#### Пример создания этапа
```json
POST /api/stages/
{
	"name": "Этап 1",
	"order": 1
}
```

### 2. Клиенты
- `GET /api/clients/` — список клиентов
- `POST /api/clients/` — создать клиента
- `GET /api/clients/{id}/` — получить клиента
- `PUT/PATCH /api/clients/{id}/` — обновить клиента
- `DELETE /api/clients/{id}/` — удалить клиента

#### Пример создания клиента
```json
POST /api/clients/
{
	"name": "Клиент 1",
	"stage_id": 1
}
```

### 3. Задачи
- `GET /api/tasks/` — список задач
- `POST /api/tasks/` — создать задачу
- `GET /api/tasks/{id}/` — получить задачу
- `PUT/PATCH /api/tasks/{id}/` — обновить задачу
- `DELETE /api/tasks/{id}/` — удалить задачу
- `PATCH /api/tasks/{id}/change-status/` — сменить статус задачи (DnD)

#### Пример создания задачи
```json
POST /api/tasks/
{
	"title": "Задание 1",
	"description": "описание задачи",
	"client_id": 1
}
```

#### Пример смены статуса задачи
```json
PATCH /api/tasks/5/change-status/
{
	"status": "in_progress"
}
```

### 4. Kanban-доска
- `GET /api/kanban/board/` — получить структуру доски

#### Пример ответа
```json
[
	{
		"stage_id": 1,
		"stage_name": "Этап 1",
		"tasks": {
			"new": [ ... ],
			"in_progress": [ ... ],
			"done": [ ... ]
		}
	},
	...
]
```

### 5. Статистика
- `GET /api/kanban/stats/` — статистика по этапам, клиентам, задачам и статусам

#### Пример ответа
```json
{
	"total_stages": 4,
	"total_clients": 10,
	"total_tasks": 25,
	"tasks_by_status": {
		"new": 8,
		"in_progress": 12,
		"done": 5
	}
}
```

---
Все эндпоинты поддерживают стандартные методы DRF. Для DnD используйте PATCH `/api/tasks/{id}/change-status/`.
