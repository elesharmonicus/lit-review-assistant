# lit-review-assistant

CLI tool for searching PubMed, analysing abstracts, and finding similar papers.

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py fetch --query "lung cancer" --max 100
python main.py analyze
python main.py similar --query "microrna"
python main.py export --format markdown
```
