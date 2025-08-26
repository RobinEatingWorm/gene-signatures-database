from openai import OpenAI

import pandas as pd

import json
import re

with open('paths.json') as file:
    paths = json.load(file)

with open('settings.json') as file:
    settings = json.load(file)
    api_key = settings['api_key']


def get_relevant_lines(article_lines: list[str], genes_regex: str, threshold: int) -> list[str]:
    """
    Get all lines in an article (excluding references) containing any gene symbols specified in a regular expression.
    :param article: A list of lines in the article.
    :param genes_regex: A regular expression that matches gene symbols.
    :param threshold: The minimum number of unique gene symbols a line must have to be returned.
    :return: A list of lines with gene symbols matching the regular expression.
    """

    # Search for relevant lines
    article_relevant = []
    for line in article_lines:
        if line == '==== Refs\n':
            break
        if len(set(re.findall(genes_regex, line))) >= threshold:
            article_relevant.append(line)
    return article_relevant


def write_batch_input(batch_id: str, articles: dict[str, str], prompt: str) -> None:
    """
    Write a JSONL file for use with the OpenAI Batch API.
    :param batch_id: A unique identifier for the batch.
    :param articles: The filenames of all articles to be included in the batch.
    :param prompt_number: The number in the prompt filename.
    :return: The path to the JSONL file.
    """

    # Request input template
    request_input = {
        'custom_id': '',
        'method': 'POST',
        'url': '/v1/chat/completions',
        'body': {
            'model': 'gpt-4.1-nano',
            'messages': [
                {'role': 'developer', 'content': ''},
                {'role': 'user', 'content': ''},
            ],
            'max_completion_tokens': 2048,
            'response_format': {'type': 'json_object'},
            'temperature': 0,
        },
    }

    # Set the developer message to the prompt
    request_input['body']['messages'][0]['content'] = prompt

    # Write each request to the batch input file
    with open(paths['batch']['input'].format(batch_id=batch_id), 'w') as batch_file:
        for article_pmcid in articles:
            request_input['custom_id'] = article_pmcid
            article = ''.join(articles[article_pmcid])
            request_input['body']['messages'][1]['content'] = article

            # Serialize the request input
            json.dump(request_input, batch_file)
            batch_file.write('\n')


def execute_batch(batch_id: str) -> None:
    """
    Execute a batch from a file of requests.
    :param batch_id: A unique identifier for the batch.
    """

    # Upload the request file
    client = OpenAI(api_key=api_key)
    batch_input_file = client.files.create(
        file=open(paths['batch']['input'].format(batch_id=batch_id), 'rb'),
        purpose='batch'
    )

    # Create a batch request
    client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint='/v1/chat/completions',
        completion_window='24h'
    )


def execute_chat_completion(kwargs: dict) -> dict:
    """
    Execute a single chat completion synchronously.
    :param kwargs: Keyword arguments passed to the chat completion request body.
    :return: The chat completion object.
    """

    # Create a chat completion for one request
    client = OpenAI(api_key=api_key)
    return client.chat.completions.create(**kwargs)
