install:
	pip install -e '.[dev]'
run:
	streamlit run app/streamlit_app.py
mcp:
	python -m mars.mcp.server
test:
	pytest -q
lint:
	ruff check .
docker:
	docker compose up --build
