# Search PubMed for a query term
# Return the first PubMed ID, title and abstract of the first result
import requests
import xml.etree.ElementTree as ET
import time
import sys
import pandas as pd

def search_pubmed(query, max_results, sort_mode):
    results = []
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&sort={sort_mode}&retmax={max_results}&retmode=json"
    response = requests.get(url)
    data = response.json()
    if 'esearchresult' in data and 'idlist' in data['esearchresult'] and len(data['esearchresult']['idlist']) > 0:
        for pubmed_id in data['esearchresult']['idlist'][:max_results]:
            print(f"Fetching {pubmed_id}...")
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pubmed_id}&rettype=abstract&retmode=xml"
            response = requests.get(url)
            time.sleep(0.34)  # stay within NCBI's 3 requests/sec limit
            if not response.content.strip().startswith(b'<'):
                print(f"Warning: unexpected response for ID {pubmed_id}, skipping.", file=sys.stderr)
                continue
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                print(f"Warning: XML parse error for ID {pubmed_id}: {e}, skipping.", file=sys.stderr)
                continue
            title_parts = []
            for el in root.findall('.//ArticleTitle'):
                title_parts.append(''.join(el.itertext()).strip())
            title = ' '.join(title_parts)
            abstract_parts = []
            for el in root.findall('.//AbstractText'):
                label = el.get('Label')
                text = ''.join(el.itertext()).strip()
                if text:
                    abstract_parts.append(f"{label}: {text}" if label else text)
            abstract = ' '.join(abstract_parts)
            year = root.findtext('.//PubDate/Year', '')
            authors = [author.findtext('LastName', '') + " " + author.findtext('ForeName', '') for author in root.findall('.//Author')]
            journal = root.findtext('.//Journal/Title', '')
            doi = root.findtext('.//ELocationID[@EIdType="doi"]', '')
            results.append({'pubmed_id': pubmed_id, 'title': title, 'abstract': abstract, 'year': year, 'authors': authors, 'journal': journal, 'doi': doi})
    return results

def save_results(results, directory):
    df = pd.DataFrame(results, columns=['pubmed_id', 'title', 'abstract', 'year', 'authors', 'journal', 'doi'])
    df.to_csv(directory, index=False)

def print_results(results):
    for result in results:
        print(f"PubMed ID: {result['pubmed_id']}")
        print(f"Title: {result['title']}")
        print(f"Abstract: {result['abstract']}")
        print(f"Year: {result['year']}")
        print(f"Authors: {', '.join(result['authors'])}")
        print(f"Journal: {result['journal']}")
        print(f"DOI: {result['doi']}")
        print()

def main(query, max_results, sort_mode, directory):
    results = search_pubmed(query, max_results, sort_mode)
    print_results(results[0:5])  # print first 5 results
    save_results(results, directory)
