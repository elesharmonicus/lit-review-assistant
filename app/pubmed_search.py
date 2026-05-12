# Search PubMed for a query term
# Return the first PubMed ID, title and abstract of the first result
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time

# Read search query from command line arguments
import sys
if len(sys.argv) < 2:
    print("Usage: python pubmed.py <search query>")
    sys.exit(1)

query = " ".join(sys.argv[1:])
sort = "relevance" # relevance, pubdate, author, journal

retnax = 20
results = []
def search_pubmed(query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&sort={sort}&retmode=json"
    response = requests.get(url)
    data = response.json()
    if 'esearchresult' in data and 'idlist' in data['esearchresult'] and len(data['esearchresult']['idlist']) > 0:
        for pubmed_id in data['esearchresult']['idlist'][:retnax]:
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
            title = root.findtext('.//ArticleTitle', '')
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
            results.append((pubmed_id, title, abstract, year, authors, journal, doi))
    return results


result = search_pubmed(query)
if result:
    for pubmed_id, title, abstract, year, authors, journal, doi in result:
        print(f"PubMed ID: {pubmed_id}")
        print(f"Title: {title}")
        print(f"Abstract: {abstract}")
        print(f"Year: {year}")
        print(f"Authors: {', '.join(authors)}")
        print(f"Journal: {journal}")
        print(f"DOI: {doi}")
        print()
else:
    print("No results found.")
    
df = pd.DataFrame(result, columns=['pubmed_id', 'title', 'abstract', 'year', 'authors', 'journal', 'doi'])
df.to_csv('data/pubmed_results.csv', index=False)

