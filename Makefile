install:
	python -m pip install -e ".[dev]"
run:
	streamlit run app/streamlit_app.py
test:
	pytest -q
