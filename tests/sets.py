import json
import os
import sys

sys.path.append('training/')

from sample import in_training_set
from extra.extra import in_extra_set

with open("settings/params.json") as file:
    params = json.load(file)
    inputs_dir_training = params["training"]["inputs"]
    inputs_dir_extra = params["training"]["extra"]["inputs"]

with open(params["training"]["targets"]) as file:
    targets_training = json.load(file)

with open(params["training"]["extra"]["targets"]) as file:
    targets_extra = json.load(file)


def test_training_match_inputs_targets() -> list[str]:
    """
    Check whether all articles in the training set are both an input and a
    target. Inputs and targets are both added manually, and hence this function
    checks for consistency.
    :return: A list of article filenames that do not appear in both the inputs
    directory and the targets file.
    """

    # Initialize a list to hold ummatched filenames
    unmatched = []

    # Check if each file in the inputs directory is in both locations
    inputs_filenames = os.listdir(inputs_dir_training)
    for (i, result) in enumerate(map(in_training_set, inputs_filenames)):
        if result != (True, True):
            unmatched.append(inputs_filenames[i])

    # Check if each file in the targets file is in both locations
    targets_filenames = list(targets_training.keys())
    for (i, result) in enumerate(map(in_training_set, targets_filenames)):
        if result != (True, True):
            unmatched.append(targets_filenames[i])
    
    # Return all files not in both locations
    return unmatched


def test_extra_match_inputs_targets() -> list[str]:
    """
    Check whether all articles in the extra set are both an input and a target.
    Inputs and targets are both added manually, and hence this function checks
    for consistency.
    :return: A list of article filenames that do not appear in both the inputs
    directory and the targets file.
    """

    # Initialize a list to hold ummatched filenames
    unmatched = []

    # Check if each file in the inputs directory is in both locations
    inputs_filenames = os.listdir(inputs_dir_extra)
    for (i, result) in enumerate(map(in_extra_set, inputs_filenames)):
        if result != (True, True):
            unmatched.append(inputs_filenames[i])

    # Check if each file in the targets file is in both locations
    targets_filenames = list(targets_extra.keys())
    for (i, result) in enumerate(map(in_extra_set, targets_filenames)):
        if result != (True, True):
            unmatched.append(targets_filenames[i])
    
    # Return all files not in both locations
    return unmatched


def test_training_extra_duplicates() -> list[str]:
    """
    Check if each article included in any set is only included in a single set.
    :return: A list of article filenames that are in both the training and extra
    sets.
    """

    # Training set files
    training_filenames = (set(os.listdir(inputs_dir_training)) |
                          set(targets_training.keys()))
    
    # Extra set files
    extra_filenames = (set(os.listdir(inputs_dir_extra)) |
                       set(targets_extra.keys()))
    
    # Find all files in both sets
    return list(training_filenames & extra_filenames)


def main() -> None:
    """
    Run tests for sets.
    """

    # Consistency between inputs and targets
    print("Unmatched Files in Training Set: ", end="")
    print(test_training_match_inputs_targets())
    print("Unmatched Files in Extra Set: ", end="")
    print(test_extra_match_inputs_targets())

    # Consistency across sets
    print("Files in Both Sets: ", end="")
    print(test_training_extra_duplicates())


if __name__ == "__main__":
    main()
