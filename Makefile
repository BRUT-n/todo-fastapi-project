.PHONY: run test db-start db-stop app-start stop docker-app-run docker-app-stop

PYTHONPATH = .
CONTAINER_NAME = todo_app_postgres_db

db-start:
	@echo "Запуск контейнера с PostgreSQL для запуска приложения локально"
	docker compose up database -d

	@echo "Ожидание готовности PostgreSQL"
	@until docker exec $(CONTAINER_NAME) pg_isready -U brutn -d todo_app_db -h localhost; do \
		echo "База еще не запустилась, еще попытка через 1 секунду"; \
		sleep 1; \
	done

	@echo "PostgreSQL полностью готов к работе"

db-stop:
	@echo "Остановка контейнера с базой"
	docker compose down database

app-start:
	@echo "Запуск приложения локально"
	PYTHONPATH=$(PYTHONPATH) uv run uvicorn src.main:app --reload

run: db-start app-start
	@echo "Запуск приложения в связке с контейнером"

stop: db-stop

docker-app-run:
	@echo "Сборка и запуск БД и приложения в изолированных контейнерах"
	docker compose up --build

docker-app-stop:
	@echo "Остановка приложения полностью"
	docker compose down

test:
	@echo "No tests yet"
