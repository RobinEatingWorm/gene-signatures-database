import pandas as pd

import re


def generate_gene_regex(filename: str, column: str) -> str:
    """
    Generate a regular expression containing genes from a TSV.
    :param filename: The filename of the TSV.
    :param column: The column label of a column containing genes.
    :return: A regular expression that matches genes present in the TSV column.
    """

    # Load the TSV and get the column
    gene_list = pd.read_csv(filename, sep="\t", dtype=object)[column]

    # Remove empty values and duplicates
    gene_list = gene_list.dropna().unique()

    # Join genes together using newlines
    gene_list = "\n".join(gene_list)

    # Find special characters in the gene list
    specials = re.finditer(r"[.^$*+?{}\\[\]?|()]", gene_list)

    # Build a regular expression by escaping all special characters
    gene_regex = ""
    index_prev = 0
    index_curr = 0
    for special in specials:
        index_curr = special.start()
        gene_regex += gene_list[index_prev:index_curr] + "\\"
        index_prev = special.start()
    gene_regex += gene_list[index_curr:]

    # Replace newlines with the special character "|"
    return re.sub(r"\n", r"|", gene_regex)


def cap_gene_regex(gene_regex: str) -> str:
    """
    Add additional specifications to a regular expression with genes to ensure
    that genes matched are not coincidentally parts of other words.
    :param gene_regex: A regular expression that matches genes generated from
    generate_gene_regex().
    :return: The same regular expression with additional specifications.
    """

    # Do not match Unicode word character directly before or after gene names
    return r"(?:\A|\W)(" + gene_regex + r")(?:\Z|\W)"
