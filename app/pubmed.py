# Search PubMed for a query term
# Return the first PubMed ID, title and abstract of the first result
import requests
import xml.etree.ElementTree as ET

# Read search query from command line arguments
import sys
if len(sys.argv) < 2:
    print("Usage: python pubmed.py <search query>")
    sys.exit(1)

query = " ".join(sys.argv[1:])

def search_pubmed(query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&sort=relevance&retmode=json"
    response = requests.get(url)
    data = response.json()
    if 'esearchresult' in data and 'idlist' in data['esearchresult'] and len(data['esearchresult']['idlist']) > 0:
        pubmed_id = data['esearchresult']['idlist'][0]
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pubmed_id}&rettype=abstract&retmode=xml"
        response = requests.get(url)
        root = ET.fromstring(response.content)
        title = root.findtext('.//ArticleTitle', '')
        abstract = root.findtext('.//AbstractText', '')
        return pubmed_id, title, abstract
    return None


result = search_pubmed(query)
if result:
    pubmed_id, title, abstract = result
    print(f"PubMed ID: {pubmed_id}")
    print(f"Title: {title}")
    print(f"Abstract: {abstract}")
else:
    print("No results found.")