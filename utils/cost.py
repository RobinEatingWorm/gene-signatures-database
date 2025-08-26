import tiktoken

import sys


def count_tokens_input(request_input: dict) -> int:
    """
    Count the number of tokens in a request input. For models not supported by tiktoken, the number is only an estimate.
    :param request_input: The request input.
    :return: The number of tokens.
    """

    # Get encoding
    try:
        encoding = tiktoken.encoding_for_model(request_input['body']['model'])
    except KeyError as exception:
        print(f"{type(exception).__name__}: {exception}", file=sys.stderr)
        print("Using cl100k_base encoding as default.", file=sys.stderr)
        encoding = tiktoken.get_encoding('cl100k_base')

    # Token counting procedure from OpenAI Cookbook
    tokens = 3
    for message in request_input['body']['messages']:
        tokens += 3
        for key in message:
            tokens += len(encoding.encode(message[key]))
            tokens += 1 if key == 'name' else 0
    return tokens


def calculate_cost_batch_input(tokens: int, model: str) -> float:
    """
    Calculate the cost of a batch input.
    :param tokens: The number of tokens in the batch input.
    :param model: The model to use. Currently, only gpt-4.1-nano is supported.
    :return: The total cost of the batch input.
    """

    # LUT for cost per one million input tokens using the batch API
    cost_per_million = {'gpt-4.1-nano': 0.05, 'gpt-4.1-nano-2025-04-14': 0.05}

    # Calculate cost
    return tokens * cost_per_million[model] / (10 ** 6)


def calculate_cost_batch_output(tokens: int, model: str) -> float:
    """
    Calculate the cost of a batch output.
    :param tokens: The number of tokens in the batch output.
    :param model: The model to use. Currently, only gpt-4.1-nano is supported.
    :return: The total cost of the batch output.
    """

    # LUT for cost per one million output tokens using the batch API
    cost_per_million = {'gpt-4.1-nano': 0.2, 'gpt-4.1-nano-2025-04-14': 0.2}

    # Calculate cost
    return tokens * cost_per_million[model] / (10 ** 6)
