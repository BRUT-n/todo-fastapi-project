PYTHONPATH = .

run:
	PYTHONPATH=$(PYTHONPATH) uv run uvicorn src.main:app --reload

test:
	@echo "No tests yet"
