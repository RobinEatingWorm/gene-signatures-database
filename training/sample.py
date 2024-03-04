import numpy as np

import json
import os
import shutil

from extra.extra import *

with open("settings/params.json") as file:
    params = json.load(file)
    articles_dir = params["articles"]["dir"]
    inputs_dir = params["training"]["inputs"]

with open(params["training"]["targets"]) as file:
    targets = json.load(file)


def sample_articles(n_samples: int) -> np.ndarray:
    """
    Randomly sample downloaded articles.
    :param n_samples: The number of samples.
    :return: An array of filenames of the articles sampled.
    """

    # Get all filenames of downloaded articles
    articles_filenames = np.array(os.listdir(articles_dir))

    # Sample random indices of the filenames array
    rng = np.random.default_rng()
    indices = rng.integers(0, articles_filenames.size, size=n_samples)
    return articles_filenames[indices]


def add_to_training_set(filename: str) -> None:
    """
    Add the article with the specified filename to the training set.
    :param filename: The filename of the article.
    """

    # Copy the file into the training inputs directory
    shutil.copy(f"{articles_dir}/{filename}", inputs_dir)


def in_training_set(filename: str) -> tuple[bool, bool]:
    """
    Check if an article with the specified filename is included in the training
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
    return (in_inputs, in_targets)


def main() -> None:
    """
    Run sample functions as needed.
    """

    # Sample an article not already in the training set
    # article = sample_articles(1)[0]
    # while (in_training_set(article) != (False, False)
    #        and in_extra_set(article) != (False, False)):
    #     article = sample_articles(1)[0]
    # print(article)

    # Add an article to the training set
    # add_to_training_set("")

    # Add an article to the extra set
    # add_to_extra_set("")


if __name__ == "__main__":
    main()
