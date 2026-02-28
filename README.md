# Task Manager

Simple task management app. Flask + React + Postgres + Redis.

## Quick Start

```bash
docker compose up --build
```

App runs at http://localhost:3000

## API

- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `GET /api/search?q=` - Search
- `GET /api/stats` - Stats
- `GET /health` - Health check
