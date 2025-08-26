import pandas as pd

import argparse
import json
import os
import sqlite3
import sys

sys.path.append(os.getcwd())

from utils.sql import get_query

with open('paths.json') as file:
    paths = json.load(file)
    db = paths['db']['sqlite']


def get_ensembl_id(gene: str, con: sqlite3.Connection) -> str | None:
    """
    Given the name of a gene, get its Ensembl ID.
    :param gene: The gene name.
    :param con: A connection to the SQLite database.
    :return: The Ensembl ID of the gene or None if no corresponding Ensembl ID is found.
    """

    # Assuming the name refers to the gene name, get the Ensembl ID
    query_gene_name = pd.read_sql_query(get_query('gene_name'), con, params={'gene': gene})
    if not query_gene_name.empty:
        return query_gene_name.loc[0, 'ensembl_id']

    # Try treating the name as a synonym for another gene name and get the Ensembl ID
    query_gene_synonym_name = pd.read_sql_query(get_query('gene_synonym_name'), con, params={'synonym': gene})
    if not query_gene_synonym_name.empty:
        return query_gene_synonym_name.loc[0, 'ensembl_id']
    
    # Return None otherwise
    return None


def format_gene_signature(pmcid: str, genes: list[str], con: sqlite3.Connection) -> pd.DataFrame:
    """
    Format a gene signature found in an article to make it ready to insert into the SQLite database.
    :param pmcid: The PMCID of the article.
    :param genes: A list of genes in the gene signature.
    :param con: A connection to the SQLite database.
    :return: A DataFrame compliant with the database schema containing information on the gene signature.
    """

    # Format gene signature information
    table_gene_signature = pd.DataFrame({
        'article_pmcid': pmcid,
        'gene_ensembl_id': [get_ensembl_id(gene, con) for gene in genes],
    })
    table_gene_signature = table_gene_signature.dropna().drop_duplicates(ignore_index=True)
    return table_gene_signature



def insert_gene_signatures(requests_output: list[str], con: sqlite3.Connection) -> None:
    """
    Insert all gene signatures from a batch output into the SQLite database.
    :param requests_output: A list of output requests as strings.
    :param con: A connection to the SQLite database.
    """

    # Initialize a list for storing tables of invidual gene signatures
    table_gene_signature = []

    # Get gene signatures from each request
    for request_output in requests_output:
        request_output = json.loads(request_output)

        # Get the PMCID of the article and the gene signature found in the article if possible
        pmcid = request_output['custom_id']
        try:
            content = json.loads(request_output['response']['body']['choices'][0]['message']['content'])
            genes = content['genes']
        except json.JSONDecodeError as exception:
            print(f"{type(exception).__name__}: {exception}", file=sys.stderr)
            continue
        
        # Format the gene signature within the request to comply with the database schema
        table_gene_signature.append(format_gene_signature(pmcid, genes, con))
    
    # Insert gene signature information
    table_gene_signature = pd.concat(table_gene_signature, ignore_index=True)
    table_gene_signature.to_sql('GeneSignature', con, if_exists='append', index=False)


def main() -> None:
    """
    Insert gene signatures into a SQLite database.
    """

    # Command line help messages
    description = "Insert all gene signature from a batch output file into a SQLite database."
    help_prompt_number = "The number in the prompt filename."
    help_val_set = "Insert batch output from the validation set instead of the entire dataset."
    help_test_set = "Insert batch output from the test set instead of the entire dataset."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('prompt_number', type=int, help=help_prompt_number)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--val-set', action='store_true', help=help_val_set)
    group.add_argument('--test-set', action='store_true', help=help_test_set)
    args = parser.parse_args()

    # Get the batch ID
    match args.val_set, args.test_set:
        case False, False:
            batch_id = f'data_{args.prompt_number:02d}'
        case True, False:
            batch_id = f'val_{args.prompt_number:02d}'
        case False, True:
            batch_id = f'test_{args.prompt_number:02d}'

    # Read the batch file
    with open(paths['batch']['output'].format(batch_id=batch_id)) as file:
        requests_output = file.readlines()

    # Insert gene signature information
    con = sqlite3.connect(db)
    insert_gene_signatures(requests_output, con)
    con.close()


if __name__ == '__main__':
    main()
