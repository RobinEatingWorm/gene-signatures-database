import argparse
import json
import os
import sys

sys.path.append(os.getcwd())

from utils.cost import count_tokens_input, calculate_cost_batch_input, calculate_cost_batch_output


with open('paths.json') as file:
    paths = json.load(file)


def estimate_costs(requests_input: list[str]) -> tuple[int, float, float]:
    """
    Get an estimate of the number of tokens in, the input cost of, and the maximum output cost of the request input.
    :param requests_input: A list of input requests as strings.
    :return: A tuple containing the estimate number of tokens, the estimated input cost, and the maximum output cost.
    """

    # Initialize cost metrics
    tokens = 0
    cost_input = 0
    max_cost_output = 0

    # Total the estimated number of input tokens, estimated input cost, and maximum output cost
    for request_input in requests_input:
        request_input = json.loads(request_input)
        tokens_current = count_tokens_input(request_input)
        tokens += tokens_current
        cost_input += calculate_cost_batch_input(tokens_current, request_input['body']['model'])
        max_cost_output += calculate_cost_batch_output(request_input['body']['max_completion_tokens'], request_input['body']['model'])
    return tokens, cost_input, max_cost_output


def main() -> None:
    """
    Get token and cost estimates.
    """

    # Command line help messages
    description = (
        "Display token and cost estimates for a batch. "
        "This script assumes that the batch file specified already exists."
    )
    help_prompt_number = "The number in the prompt filename."
    help_val_set = "Use the validation set instead of the entire dataset."
    help_test_set = "Use the test set instead of the entire dataset."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('prompt_number', type=int, help=help_prompt_number)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--val-set', action='store_true', help=help_val_set)
    group.add_argument('--test-set', action='store_true', help=help_test_set)
    args = parser.parse_args()

    # Get the identifier of the batch file
    match args.val_set, args.test_set:
        case False, False:
            batch_id = f'data_{args.prompt_number:02d}'
        case True, False:
            batch_id = f'val_{args.prompt_number:02d}'
        case False, True:
            batch_id = f'test_{args.prompt_number:02d}'

    # Read the batch file
    with open(paths['batch']['input'].format(batch_id=batch_id)) as file:
        requests_input = file.readlines()

    # Calculate and display cost metrics
    tokens, cost_input, max_cost_output = estimate_costs(requests_input)
    print(f"Estimated Number of Input Tokens: {tokens}")
    print(f"Estimated Input Cost: ${cost_input}")
    print(f"Maximum Output Cost: ${max_cost_output}")


if __name__ == '__main__':
    main()
