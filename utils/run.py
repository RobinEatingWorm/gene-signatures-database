from openai import OpenAI
from openai.types.chat import ChatCompletion

import json
import re

with open("settings/params.json") as file:
    params = json.load(file)
    prompts_dir = params["prompts"]


def get_prompt(prompt_number: int, type: str) -> str:
    """
    Read a prompt from a file and format it correctly.
    :param prompt_number: The number in the prompt filename.
    :param type: The type of prompt. This can either be "train" or "valid".
    :return: A string containing the formatted rompt.
    """

    # Read all lines from the file
    with open(f"{prompts_dir}/{type}_{prompt_number:02d}.txt") as file:
        prompt = file.readlines()

    # Replace newlines with spaces
    return " ".join([line.strip() for line in prompt])


def get_relevant_lines(article_filename: str, gene_regex: str,
                       threshold: int) -> list[str]:
    """
    Get all lines in an article (excluding references) containing any gene
    symbols specified in a regular expression.
    :param article_filename: The filename of the article.
    :param gene_regex: A regular expression that matches gene symbols.
    :param threshold: The minimum number of gene symbols in each line to be
    returned.
    :return: A list of lines with gene symbols matching the regular expression.
    """

    # Read all lines in the article
    with open(article_filename, errors="ignore") as file:
        article = file.readlines()

    # Initialize a list to store relevant lines
    article_relevant = []

    # Find lines excluding references
    for line in article:
        if line == "==== Refs\n":
            break
        if len(set(re.findall(gene_regex, line))) >= threshold:
            article_relevant.append(line)
    return article_relevant


def create_chat_completion(prompt: str, text: str) -> ChatCompletion:
    """
    Get a response for the given chat conversation.
    :param prompt: A prompt to set the behaviour of the LLM.
    :param text: A message that the LLM should respond to.
    :return: A Chat Completions API response.
    """

    # API key
    with open("settings/api_key.txt") as file:
        api_key = file.readline().strip()
    
    # Run the LLM
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return response
