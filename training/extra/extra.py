import json
import os
import shutil

with open("settings/params.json") as file:
    params = json.load(file)
    articles_dir = params["articles"]["dir"]
    inputs_dir = params["training"]["extra"]["inputs"]

with open(params["training"]["extra"]["targets"]) as file:
    targets = json.load(file)


def add_to_extra_set(filename: str) -> None:
    """
    Add the article with the specified filename to the extra set.
    :param filename: The filename of the article.
    """

    # Copy the file into the extra inputs directory
    shutil.copy(f"{articles_dir}/{filename}", inputs_dir)


def in_extra_set(filename: str) -> tuple[bool, bool]:
    """
    Check if an article with the specified filename is included in the extra
    inputs and labels.
    :param filename: The filename of an article.
    :return: A tuple of Booleans. The first Boolean shows whether the article
    is included in the inputs, and the second shows whether the article is
    included in the labels.
    """

    # Check whether the article is in the inputs directory
    in_inputs = filename in set(os.listdir(inputs_dir))

    # Check whether the article is in the labels file
    in_targets = filename in set(targets.keys())

    # Return both values
    return in_inputs, in_targets
