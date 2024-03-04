import json
import os
import sys

sys.path.append('utils/')

from regex import *
from run import *

with open("settings/params.json") as file:
    params = json.load(file)    
    genes_file = params["genes"]["file"]
    names_column = params["genes"]["names"]
    synonyms_column = params["genes"]["synonyms"]
    inputs_dir_training = params["training"]["inputs"]
    inputs_dir_extra = params["training"]["extra"]["inputs"]

with open(params["training"]["targets"]) as file:
    targets_training = json.load(file)

with open(params["training"]["extra"]["targets"]) as file:
    targets_extra = json.load(file)


def train_accuracy(prompt_number: int) -> tuple[float, float]:
    """
    Run all articles in the training set through the LLM using the specified
    prompt.
    :return: A tuple with two floats. The first is the accuracy of positive
    examples (articles with gene signatures), and the second is the accuracy of
    negative examples (articles without gene signatures).
    """

    # Get the prompt
    prompt = get_prompt(prompt_number)

    # Create a regular expression with all genes and their synonyms
    gene_names_regex = generate_gene_regex(genes_file, names_column)
    gene_synonyms_regex = generate_gene_regex(genes_file, synonyms_column)
    gene_regex = cap_gene_regex(gene_names_regex + r"|" + gene_synonyms_regex)

    # Process each article
    for article in os.listdir(inputs_dir_training):
        
        # Path of the article within the training directory
        article_path = f"{inputs_dir_training}/{article}"

        # All paragraphs which have more than one gene symbol
        paragraphs = get_relevant_lines(article_path, gene_regex)

        # Process each paragraph
        for paragraph in paragraphs:
            response = create_chat_completion(prompt, paragraph)

            break # TODO

        break # TODO


def main() -> None:
    """
    Run training functions.
    """

    # Training accuracy of a prompt
    training_accuracy(1)


if __name__ == "__main__":
    main()
