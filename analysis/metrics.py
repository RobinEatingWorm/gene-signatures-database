import numpy as np
import pandas as pd

import argparse
import json
import os
import re
import sys

sys.path.append(os.getcwd())

from utils.cost import calculate_cost_batch_input, calculate_cost_batch_output

with open('paths.json') as file:
    paths = json.load(file)


def calculate_accuracies(requests_output: list[str], targets: dict[str, list], batch_id: str) -> tuple[int, int]:
    """
    Calculate the positive accuracy (accuracy on articles containing gene signature) and negative accuracy (accuracy on
    articles not containing gene signatures) of a batch.
    :param requests_output: A list of output requests as strings.
    :param targets: A dictionary mapping article PMCIDs in the set to their expected targets.
    :param batch_id: A unique identifier for the batch.
    :return: A tuple containing the positive and negative accuracies.
    """

    # Store accuracy information
    correct = {'positive': 0, 'negative': 0}
    total = {'positive': 0, 'negative': 0}

    # Log request and accuracy information
    with open(paths['logs']['analysis']['accuracy'].format(batch_id=batch_id), 'w') as log:

        # Load individual requests
        for request_output in requests_output:
            request_output = json.loads(request_output)

            # Log request information and expected target
            pmcid = request_output['custom_id']
            target = targets[pmcid]
            try:
                content = json.loads(request_output['response']['body']['choices'][0]['message']['content'])
                prediction = content['genes']
            except json.JSONDecodeError as exception:
                print(f"{type(exception).__name__}: {exception}", file=sys.stderr)
                content = f"{type(exception).__name__}: {exception}"
                prediction = None
            log.write(f"PMCID: {pmcid}\n")
            log.write(f"Content: {content}\n")
            log.write(f"Target: {target}\n")
            log.write(f"Prediction: {prediction}\n")

            # Determine article type and model correctness
            contains = 'positive' if len(target) > 0 else 'negative'
            total[contains] += 1
            if prediction is not None and set(prediction) == set(target):
                correct[contains] += 1
                log.write("Correct\n")
            else:
                log.write("Incorrect\n")

            # Visual separator for log
            log.write(f"{'-' * 120}\n")

        # Log overall accuracy information
        log.write(f"Correct Positive Examples: {correct['positive']} out of {total['positive']}\n")
        log.write(f"Correct Negative Examples: {correct['negative']} out of {total['negative']}\n")

    # Calculate accuracies
    return correct['positive'] / total['positive'], correct['negative'] / total['negative']


def calculate_costs(requests_output: list[str]) -> tuple[float, float]:
    """
    Calculate the total costs of a batch.
    :param requests_output: A list of output requests as strings.
    :return: A tuple containing the total input and output costs.
    """

    # Initialize cost metrics
    cost_input = 0
    cost_output = 0

    # Total costs from each request
    for request_output in requests_output:
        request_output = json.loads(request_output)

        # Extract information from chat completion
        tokens_input = request_output['response']['body']['usage']['prompt_tokens']
        tokens_output = request_output['response']['body']['usage']['completion_tokens']
        model = request_output['response']['body']['model']

        # Calculate input and output costs
        cost_input += calculate_cost_batch_input(tokens_input, model)
        cost_output += calculate_cost_batch_output(tokens_output, model)

    # Return costs
    return cost_input, cost_output


def save_metrics(metrics: pd.Series) -> None:
    """
    Save calculated metrics to a CSV file.
    :param metrics: Metrics to add to the file.
    """

    # Read an existing CSV
    try:
        df = pd.read_csv(paths['analysis']['metrics'], dtype={
            'set': object,
            'prompt_number': np.int64,
            'positive_accuracy': np.float64,
            'negative_accuracy': np.float64,
            'cost_input': np.float64,
            'cost_output': np.float64,
        })

    # Create a new DataFrame if a CSV does not exist
    except FileNotFoundError as exception:
        print(f"{type(exception).__name__}: {exception}", file=sys.stderr)
        df = pd.DataFrame(columns=[
            'set',
            'prompt_number',
            'positive_accuracy',
            'negative_accuracy',
            'cost_input',
            'cost_output',
        ])

    # Replace existing data for the set and prompt if any
    if ((df['set'] == metrics['set']) & (df['prompt_number'] == metrics['prompt_number'])).any():
        df[(df['set'] == metrics['set']) & (df['prompt_number'] == metrics['prompt_number'])] = metrics

    # Add a new row for the set and prompt if none exist
    else:
        df = pd.concat([df, metrics.to_frame().T])

    # Format and save the data
    df = df.sort_values(['set', 'prompt_number'])
    df.to_csv(paths['analysis']['metrics'], index=False)



def main() -> None:
    """
    Calculate and save metrics.
    """

    # Command line help messages
    description = "Evaluate prompt accuracy and cost of a batch on the validation or test set."
    help_prompt_number = "The number in the prompt filename."
    help_val_set = "Calculate metrics on the validation set."
    help_test_set = "Calculate metrics on the test set."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('prompt_number', type=int, help=help_prompt_number)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--val-set', action='store_true', help=help_val_set)
    group.add_argument('--test-set', action='store_true', help=help_test_set)
    args = parser.parse_args()

    # Get set-specific information
    match args.val_set, args.test_set:
        case True, False:
            with open(paths['run']['targets']['val']) as file:
                targets = json.load(file)
            set_name = 'val'
        case False, True:
            with open(paths['run']['targets']['test']) as file:
                targets = json.load(file)
            set_name = 'test'

    # Read the batch file
    batch_id = f'{set_name}_{args.prompt_number:02d}'
    with open(paths['batch']['output'].format(batch_id=batch_id)) as file:
        requests_output = file.readlines()

    # Calculate and save accuracies and cost
    positive_accuracy, negative_accuracy = calculate_accuracies(requests_output, targets, batch_id)
    cost_input, cost_output = calculate_costs(requests_output)
    save_metrics(pd.Series({
        'set': set_name,
        'prompt_number': args.prompt_number,
        'positive_accuracy': positive_accuracy,
        'negative_accuracy': negative_accuracy,
        'cost_input': cost_input,
        'cost_output': cost_output,
    }))


if __name__ == '__main__':
    main()
