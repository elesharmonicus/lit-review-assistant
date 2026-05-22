import argparse

from src.utils import setup_logging
from src.config import load_config
from src.pubmed_client import main as fetch_main
from src.analysis import main as analyze_main
from src.embeddings import main as tensors_main
from src.export import main as export_main

def main():
    setup_logging()
    config = load_config()
    parser = argparse.ArgumentParser(description="Lit review assistant")
    subparsers = parser.add_subparsers(dest='command')
    fetch_parser = subparsers.add_parser('fetch')
    fetch_parser.add_argument('--query', required=True, nargs='+', help="Search query for PubMed")
    fetch_parser.add_argument('--max', type=int, default=config.get('pubmed', {}).get('max_results', 100), help="Maximum number of PubMed results to fetch")
    fetch_parser.add_argument('--sort', choices=['relevance', 'pubdate', 'author', 'journal'], default=config.get('pubmed', {}).get('sort_mode', 'relevance'), help="Sort mode for PubMed search")
    fetch_parser.add_argument('--output', default=config.get('paths', {}).get('output_file', 'data/pubmed_results.csv'), help="Output CSV file for PubMed results")
    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.add_argument('--input', default=config.get('paths', {}).get('output_file', 'data/pubmed_results.csv'), help="CSV file with PubMed results to analyze")
    similar_parser = subparsers.add_parser('similar')
    similar_parser.add_argument('--input', default=config.get('paths', {}).get('output_file', 'data/pubmed_results.csv'), help="CSV file with PubMed results to analyze")
    similar_parser.add_argument('--query', required=True, type=str, help="Search query to find similar papers for")
    export_parser = subparsers.add_parser('export')
    export_parser.add_argument('--format', choices=['csv', 'json', 'markdown'], default='csv', help="Export format")
    export_parser.add_argument('--input', default=config.get('paths', {}).get('output_file', 'data/pubmed_results.csv'), help="CSV file with PubMed results to export")
    args = parser.parse_args()
    print("Literature AI Assistant")
    if args.command == 'fetch':
        query = ' '.join(args.query)
        fetch_main(query, args.max, args.sort, args.output)
    elif args.command == 'analyze':
        analyze_main(args.input)
    elif args.command == 'similar':
        tensors_main(args.input, args.query)
    elif args.command == 'export':
        export_main(args.input, args.format)
    else: parser.print_help()

if __name__ == "__main__":
    main()