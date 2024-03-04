from openai import OpenAI

import pandas as pd

import json
import re
from typing import Any


def generate_gene_regex(filename: str, column: str) -> str:
    """
    Generate a regular expression containing genes from a TSV.
    :param filename: The filename of the TSV.
    :param column: The column label of a column containing genes.
    :return: A regular expression that matches genes present in the TSV column.
    """

    # Load the TSV and get the column
    gene_list = pd.read_csv(filename, sep="\t", dtype=object)[column]

    # Remove empty values and duplicates
    gene_list = gene_list.dropna().unique()

    # Join genes together to form a regular expression
    return r"|".join(gene_list)


def get_relevant_lines(article: list[str], gene_regex: str) -> list[str]:
    """
    Get all lines in an article (excluding references) containing any gene
    symbols specified in a regular expression.
    :param article: A list of all lines in the article.
    :param gene_regex: A regular expression that matches gene symbols.
    :return: A list of lines with gene symbols matching the regular expression.
    """

    # Initialize a list to store relevant lines
    article_relevant = []

    # Find lines with gene symbols excluding references
    for line in article:
        if line == "=== Refs\n":
            break
        if re.search(gene_regex, line):
            article_relevant.append(line)
    return article_relevant


def create_chat_completion(prompt: str, text: str) -> Any:
    """
    Get a response for the given chat conversation.
    :param prompt: A prompt to set the behaviour of the LLM.
    :param text: A message that the LLM should respond to.
    :return: 
    """

    # API key
    with open("settings/api_key.txt") as file:
        api_key = file.readline().strip()
    
    # Run the LLM
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5.turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json-object"},
        temperature=0,
    )
    print(type(response)) # FIX
    return response
