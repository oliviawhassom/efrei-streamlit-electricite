install:
	pip install -r requirements.txt

data:
	python scripts/download_data.py

run:
	streamlit run app.py
