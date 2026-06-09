.PHONY: run test db-start db-stop app-start stop

PYTHONPATH = .
CONTAINER_NAME = todo_app_postgres_db

db-start:
	@echo "Запуск контейнера с PostgreSQL"
	docker compose up -d

	@echo "Ожидание готовности PostgreSQL"
	@until docker exec $(CONTAINER_NAME) pg_isready -U brutn -d todo_app_db -h localhost; do \
		echo "База еще не запустилась, еще попытка через 1 секунду"; \
		sleep 1; \
	done

	@echo "PostgreSQL полностью готов к работе"

db-stop:
	@echo "Остановка контейнера"
	docker compose down

app-start:
	@echo "Запуск приложения"
	PYTHONPATH=$(PYTHONPATH) uv run uvicorn src.main:app --reload

run: db-start app-start
	@echo "Запуск приложения в связке с контейнером"

stop: db-stop

test:
	@echo "No tests yet"
