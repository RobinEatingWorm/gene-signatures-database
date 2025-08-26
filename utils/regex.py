import numpy as np

import re


def create_genes_regex(genes: np.ndarray) -> str:
    """
    Create a regular expression that matches gene names without matching parts of words that coincidentally contain gene
    names.
    :param genes: An array of gene names and/or synonyms.
    :return: A regular expression.
    """

    # Join gene names together using tabs
    genes_regex = '\t'.join(genes)

    # Escape all special characters
    genes_regex = re.sub(r'[.^$*+?{}\\[\]|()]', r'\\\g<0>', genes_regex)

    # Replace tabs with the special character '|'
    genes_regex = re.sub(r'\t', r'|', genes_regex)

    # Do not match Unicode word characters directly beside gene names
    return r'(?:\A|\W)(' + genes_regex + r')(?:\Z|\W)'


def get_pmcid_from_filename(filename: str) -> str:
    """
    Extract an article's PMCID from its filename.
    :param filename: The filename of the article.
    :return: The PMCID of the article.
    """

    # Use a regex to find the PMCID
    return re.search(r'^(?P<pmcid>PMC[0-9]*)\.txt$', filename).group('pmcid')
