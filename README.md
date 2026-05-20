# lit-review-assistant

CLI tool for searching PubMed, analysing abstracts, and finding similar papers.

## Setup
pip install -r requirements.txt

## Usage
python app/main.py fetch --query "lung cancer" --max 100
python app/main.py analyze
python app/main.py similar --query "microrna"
python app/main.py export --format markdown