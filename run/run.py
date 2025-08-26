import numpy as np
import pandas as pd

import argparse
import json
from multiprocessing import Pool
import os
import sys

sys.path.append(os.getcwd())

from utils.regex import create_genes_regex, get_pmcid_from_filename
from utils.run import get_relevant_lines, write_batch_input, execute_batch, execute_chat_completion

with open('paths.json') as file:
    paths = json.load(file)
    articles_texts = paths['data']['articles']['texts']
    genes_info = paths['data']['genes']['info']


def format_get_relevant_lines_dict_item(
    article_pmcid: str,
    article_lines: list[str],
    genes_regex: str,
    threshold: int
) -> tuple[str, str]:
    """
    A wrapper for get_relevant_lines that joins all lines and returns a valid key-value pair for adding to a dictionary.
    :param article_pmcid: The article's PMCID.
    :param article_lines: A list of lines in the article.
    :param genes_regex: A regular expression that matches gene symbols.
    :param threshold: The minimum number of unique gene symbols a line must have to be returned.
    :return: A tuple containing the article's PMCID (key) and a string with all relevant lines from the article (value).
    """

    # Call get_relevant_lines and create a tuple
    return article_pmcid, ''.join(get_relevant_lines(article_lines, genes_regex, threshold))


def create_batch_input(batch_id: str, article_pmcids: list[str], prompt_number: int, max_processes: int) -> None:
    """
    Create a batch of requests with a specific prompt.
    :param batch_id: A unique identifier to appear within the filename of the batch.
    :param article_pmcids: A list of PMCIDs of all articles to be included in the batch.
    :param prompt_number: The number in the prompt filename.
    :max_processes: The maximum number of processes in a pool.
    """

    # Load the prompt
    with open(paths['prompts']['prompt'].format(prompt_number=prompt_number)) as file:
        prompt = ''.join(file.readlines())

    # Create a regex for detecting gene symbols
    data = pd.read_csv(genes_info, sep='\t', dtype=object)
    genes = np.concatenate([
        data['external_gene_name'].dropna().unique(),
        data['external_synonym'].dropna().unique()
    ], axis=0)
    genes_regex = create_genes_regex(genes)

    # Prepare articles as arguments for mapping
    args = []
    threshold = 2
    for article_pmcid in article_pmcids:
        with open(f'{paths['data']['articles']['texts']}/{article_pmcid}.txt', errors='ignore') as file:
            args.append((article_pmcid, file.readlines(), genes_regex, threshold))

    # Get relevant lines from articles
    with Pool(max_processes) as pool:
        articles = dict(pool.starmap(format_get_relevant_lines_dict_item, args))

    # Write batch
    write_batch_input(batch_id, articles, prompt)


def execute_chat_completions(batch_id: str) -> None:
    """
    Execute all requests in a batch as separate chat completions for synchronous processing.
    :param batch_id: A unique identifier for the batch.
    """

    # Read all requests from the batch
    with open(paths['batch']['input'].format(batch_id=batch_id)) as file:
        requests_input = file.readlines()

    # Save outputs in a batch-like format
    with open(paths['batch']['output'].format(batch_id=batch_id), 'w') as file:

        # Create a chat completion for each request
        for request_input in requests_input:
            request_input = json.loads(request_input)
            completion = execute_chat_completion(request_input['body'])

            # Format and write each chat completion
            request_output = {
                'custom_id': request_input['custom_id'],
                'response': {
                    'body': completion.to_dict()
                }
            }
            json.dump(request_output, file)
            file.write('\n')


def main() -> None:
    """
    Run functions for processing articles.
    """

    # Command line help messages
    description = "Perform operations for processing requests for a specified prompt and set of articles."
    help_prompt_number = "The number in the prompt filename."
    help_create = "Create a file of requests for the prompt and set of articles."
    help_execute = "Execute a batch of requests from an existing file for the prompt and set of articles."
    help_synchronous = "If executing a batch, instead excute as individual synchronous chat completions."
    help_val_set = "Use the validation set instead of the entire dataset."
    help_test_set = "Use the test set instead of the entire dataset."
    help_max_processes = "The maximum number of processes to use for regex processing."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('prompt_number', type=int, help=help_prompt_number)
    parser.add_argument('-c', '--create', action='store_true', help=help_create)
    parser.add_argument('-e', '--execute', action='store_true', help=help_execute)
    parser.add_argument('-s', '--synchronous', action='store_true', help=help_synchronous)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--val-set', action='store_true', help=help_val_set)
    group.add_argument('--test-set', action='store_true', help=help_test_set)
    parser.add_argument('-m', '--max-processes', default=5, type=int, help=help_max_processes)
    args = parser.parse_args()

    # Set up input information
    match args.val_set, args.test_set:

        # Entire dataset
        case False, False:
            batch_id = f'data_{args.prompt_number:02d}'
            article_pmcids = [
                get_pmcid_from_filename(article_filename)
                for article_filename in os.listdir(articles_texts)
            ]

        # Validation set
        case True, False:
            with open(paths['run']['targets']['val']) as file:
                val_targets = json.load(file)
            batch_id = f'val_{args.prompt_number:02d}'
            article_pmcids = list(val_targets.keys())

        # Test set
        case False, True:
            with open(paths['run']['targets']['test']) as file:
                test_targets = json.load(file)
            batch_id = f'test_{args.prompt_number:02d}'
            article_pmcids = list(test_targets.keys())

    # Create a JSONL file containing a batch of requests
    if args.create:
        create_batch_input(batch_id, article_pmcids, args.prompt_number, args.max_processes)

    # Run a batch using the JSONL file
    if args.execute:
        execute_chat_completions(batch_id) if args.synchronous else execute_batch(batch_id)


if __name__ == '__main__':
    main()
