import numpy as np

import argparse
import json
import os

with open('paths.json') as file:
    paths = json.load(file)
    articles_texts = paths['data']['articles']['texts']


def sample_articles(n_samples: int) -> np.ndarray:
    """
    Randomly sample downloaded articles not already selected as a target.
    :param n_samples: The number of samples.
    :return: An array of filenames of the articles sampled.
    """

    # Get files already in the validation set
    with open(paths['run']['targets']['val']) as file:
        val_targets = json.load(file)

    # Get files already in the test set
    with open(paths['run']['targets']['test']) as file:
        test_targets = json.load(file)

    # Sample among articles not already sampled before
    articles_sampled = set(val_targets.keys()) | set(test_targets.keys())
    articles_filenames = np.array(list(set(os.listdir(articles_texts)) - articles_sampled))
    return np.random.default_rng().choice(articles_filenames, size=n_samples, replace=False)


def main() -> None:
    """
    Run sampling as needed.
    """

    # Command line help messages
    description = "Sample new articles not already included in a dataset."
    help_n_samples = "The number of new articles to sample."

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-n', '--n-samples', default=1, type=int, help=help_n_samples)
    args = parser.parse_args()

    # Sample a new article
    print(sample_articles(args.n_samples))


if __name__ == '__main__':
    main()
