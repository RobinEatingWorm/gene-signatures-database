from openai import BadRequestError

import json
import os
import re
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


def validate_content(content_train: dict, paragraph: str, prompt_valid_pos: str,
                     prompt_valid_neg: str) -> dict:
    """
    Perform validation on content from a response received during training.
    :param content_train: A dictionary with the content of the response.
    :param paragraph: The paragraph used to obtain the response.
    :param prompt_valid_pos: A prompt for validating positive responses.
    :param prompt_valid_neg: A prompt for validating negative responses.
    :return: A dictionary containing the results of validation.
    """

    # Get the list of genes found
    genes = content_train["genes"]

    # Validate the response from training
    if genes:
        prompt_valid_pos = prompt_valid_pos.format(genes=genes)
        response_valid = create_chat_completion(prompt_valid_pos, paragraph)
    else:
        response_valid = create_chat_completion(prompt_valid_neg, paragraph)
    
    # Extract the validation result
    content_str_valid = response_valid.choices[0].message.content
    content_valid = json.loads(content_str_valid)
    return content_valid


def train_accuracy(train_number: int, valid_pos_number: int,
                   valid_neg_number: int) -> tuple[float, float]:
    """
    Run all articles in the training set through the LLM using the specified
    prompt.
    :param train_number: The number in the filename of the training prompt.
    :param valid_pos_number: The number in the filename of the validation prompt
    for positive results.
    :param valid_neg_number: The number in the filename of the validation prompt
    for negative results.
    :return: A tuple with two floats. The first is the accuracy of positive
    examples (articles with gene signatures), and the second is the accuracy of
    negative examples (articles without gene signatures).
    """

    # Get the prompts
    prompt_train = get_prompt(train_number, "train")
    prompt_valid_pos = get_prompt(valid_pos_number, "valid")
    prompt_valid_neg = get_prompt(valid_neg_number, "valid")

    # Create a regular expression with all genes and their synonyms
    gene_names_regex = generate_gene_regex(genes_file, names_column)
    gene_synonyms_regex = generate_gene_regex(genes_file, synonyms_column)
    gene_regex = cap_gene_regex(gene_names_regex + r"|" + gene_synonyms_regex)

    # Track the number of articles correctly processed
    correct_pos = 0
    correct_neg = 0

    # Process each article
    for article in targets_training:

        # Display article information
        print(f"Article: {article}")
        print(f"Targets: {targets_training[article]}")
        
        # Path of the article within the training directory
        article_path = f"{inputs_dir_training}/{article}"

        # Attempt to run the LLM
        ok = 0
        threshold = 2
        while not ok:
            try:

                # All paragraphs which have more than one gene symbol
                lines = get_relevant_lines(article_path, gene_regex, threshold)
                paragraphs = "".join(lines)

                # Create a chat completion
                response_train = create_chat_completion(prompt_train,
                                                        paragraphs)
                content_str_train = response_train.choices[0].message.content
                content_train = json.loads(content_str_train)
                content_valid = validate_content(content_train, paragraphs,
                                                 prompt_valid_pos,
                                                 prompt_valid_neg)

            # There may be too many tokens in the input
            except BadRequestError as e:
                print(f"{type(e).__name__}: {e}")

                # Increase the threshold if the context length is exceeded
                if e.code == "context_length_exceeded":
                    threshold += 1
                    continue
                
                # Something else went wrong with the chat completion
                ok = 1
                continue


            # Something else went wrong with the chat completion
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
                print("-" * 50)
                ok = 1
                continue

            # Display results
            print(f"Predictions: {content_train['genes']}")
            print(f"Training Content: {content_train}")
            print(f"Validation Content: {content_valid}")

            # Update correct results
            if set(targets_training[article]) == set(content_train["genes"]):
                if targets_training[article]:
                    correct_pos += 1
                else:
                    correct_neg += 1
                print("Correct")
            else:
                print("Wrong")
            print("-" * 50)
            ok = 1

    # Total correct results
    print(f"Correct Positive Examples: {correct_pos}")
    print(f"Correct Negative Examples: {correct_neg}")
    return correct_pos, correct_neg


def main() -> None:
    """
    Run training functions.
    """

    # Training accuracy of a prompt
    for i in range(1, 7):
        print("=" * 100)
        print(f"NOW TRAINING PROMPT {i}")
        print("=" * 100)
        train_accuracy(i, 1, 2)


if __name__ == "__main__":
    main()
