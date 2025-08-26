from Bio import Entrez

import pandas as pd

import argparse
import json
import os
import sys
import time

with open('paths.json') as file:
    paths = json.load(file)
    articles_info = paths['data']['articles']['info']
    articles_texts = paths['data']['articles']['texts']

with open('settings.json') as file:
    settings = json.load(file)
    email = settings['email']


def query() -> None:
    """
    Query PubMed Central for articles using Entrez.
    """

    # Set email for Entrez
    Entrez.email = email

    # Get article PMCIDs
    handle_esearch = Entrez.esearch(db='pmc', term='"gene signature" OR "gene set"', retmax=2 ** 31 - 1)
    record_esearch = Entrez.read(handle_esearch)
    handle_esearch.close()
    print(f"Number of Articles: {record_esearch['Count']}")
    print(f"Number of PMCIDs: {len(record_esearch['IdList'])}")

    # Get article summaries
    record_esummary = []
    batch_size = 9999
    n_iters = int(record_esearch['Count']) // batch_size + (int(record_esearch['Count']) % batch_size > 0)
    for i in range(n_iters):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, int(record_esearch['Count']))
        print(f"Retrieving summaries for indices {start_index} to {end_index - 1}...")
        handle_esummary = Entrez.esummary(db='pmc', id=record_esearch['IdList'][start_index:end_index], retmax=batch_size)
        record_esummary += Entrez.read(handle_esummary)
        handle_esummary.close()
    record_esummary.sort(key=lambda summary: int(summary['Id']))
    print(f"Number of Article Summaries: {len(record_esummary)}")

    # Extract relevant information
    data = pd.DataFrame({
        'doi': [
            summary['ArticleIds']['doi'] if 'doi' in summary['ArticleIds'] else ''
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'pmcid': [
            summary['ArticleIds']['pmcid']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'title': [
            summary['Title']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'author': [
            author
            for summary in record_esummary for author in summary['AuthorList']
        ],
        'journal': [
            summary['FullJournalName']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'volume': [
            summary['Volume']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'issue': [
            summary['Issue']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'pages': [
            summary['Pages']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
        'date':  [
            summary['PubDate']
            for summary in record_esummary for _ in range(len(summary['AuthorList']))
        ],
    })
    data.to_csv(articles_info, sep='\t', index=False)


def get_articles_texts(max_processes: int) -> None:
    """
    Get text from articles in the PMC Open Access Subset.
    :param max_processes: The maximum number of child processes to create.
    """

    # Retrieve all PMCIDs
    data = pd.read_csv(articles_info, sep='\t', dtype=object)
    pmcids = data['pmcid'].dropna().unique()

    # Command to run
    cmd = 'aws s3 cp s3://pmc-oa-opendata/{dir}/txt/all/{pmcid}.txt {articles_texts} --no-sign-request'

    # Use PMCIDs to download articles
    n_iters = pmcids.shape[0] // max_processes + (pmcids.shape[0] % max_processes > 0)
    for i in range(n_iters):
        start_index = i * max_processes
        end_index = min((i + 1) * max_processes, pmcids.shape[0])
        start_time = time.time()
        for j in range(start_index, end_index):

            # If child, use the AWS CLI to download article text
            if os.fork() == 0:
                os.system(cmd.format(dir='oa_comm', pmcid=pmcids[j], articles_texts=articles_texts))
                os.system(cmd.format(dir='oa_noncomm', pmcid=pmcids[j], articles_texts=articles_texts))
                os.system(cmd.format(dir='phe_timebound', pmcid=pmcids[j], articles_texts=articles_texts))
                print(f"Index: {j}, PMCID: {pmcids[j]}")
                sys.exit()

        # If parent, wait for all child processes to exit
        for j in range(start_index, end_index):
            os.wait()

        # Print elapsed time
        end_time = time.time()
        print(f"Iteration Time: {end_time - start_time}")


def main() -> None:
    """
    Run setup functions for retrieving articles.
    """

    # Command line help messages
    description = "Query and retrieve articles in the PMC Open Access Subset using AWS."
    help_max_processes = "The maximum number of processes to use for fetching articles."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-m', '--max-processes', default=5, type=int, help=help_max_processes)
    args = parser.parse_args()

    # Run queries for articles potentially containing gene signatures
    query()

    # Get all OA articles
    get_articles_texts(args.max_processes)


if __name__ == '__main__':
    main()
