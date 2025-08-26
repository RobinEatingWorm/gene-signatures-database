import pandas as pd

import json
import sqlite3

with open('paths.json') as file:
    paths = json.load(file)
    articles_info = paths['data']['articles']['info']
    genes_info = paths['data']['genes']['info']
    db = paths['db']['sqlite']


def insert_articles_info(con: sqlite3.Connection) -> None:
    """
    Insert information on articles into a SQLite database.
    :param con: A connection to the database.
    """

    # Read data on articles
    data = pd.read_csv(articles_info, sep='\t', dtype=object)

    # Insert article information
    table_article = data.drop(columns=['author']).drop_duplicates(ignore_index=True)
    table_article.to_sql('Article', con, if_exists='append', index=False)

    # Insert author information
    table_author = data['author'].dropna().drop_duplicates(ignore_index=True).to_frame(name='name')
    table_author['id'] = table_author.index + 1
    table_author.to_sql('Author', con, if_exists='append', index=False)

    # Insert information on which authors contributed to which articles
    table_article_author = pd.merge(
        data[['pmcid', 'author']].dropna().drop_duplicates(ignore_index=True),
        table_author,
        how='inner',
        left_on='author',
        right_on='name',
    )
    table_article_author = table_article_author[['pmcid', 'id']].rename(columns={
        'pmcid': 'article_pmcid',
        'id': 'author_id',
    })
    table_article_author.to_sql('ArticleAuthor', con, if_exists='append', index=False)


def insert_genes_info(con: sqlite3.Connection) -> None:
    """
    Insert information on articles into a SQLite database.
    :param con: A connection to the database.
    """

    # Read data on genes
    data = pd.read_csv(genes_info, sep='\t', dtype=object)

    # Insert gene information
    table_gene = data.drop(columns=['external_synonym']).drop_duplicates(ignore_index=True)
    table_gene = table_gene.rename(columns={
        'ensembl_gene_id': 'ensembl_id',
        'external_gene_name': 'name',
        'chromosome_name': 'chromosome',
    })
    table_gene.to_sql('Gene', con, if_exists='append', index=False)

    # Insert gene synonym information
    table_gene_synonym = data[['ensembl_gene_id', 'external_synonym']].dropna().drop_duplicates(ignore_index=True)
    table_gene_synonym = table_gene_synonym.rename(columns={
        'ensembl_gene_id': 'gene_ensembl_id',
        'external_synonym': 'name',
    })
    table_gene_synonym.to_sql('GeneSynonym', con, if_exists='append', index=False)


def main() -> None:
    """
    Insert existing data into a SQLite database.
    """

    # Open a connection to the database
    con = sqlite3.connect(db)

    # Insert information on articles and genes
    insert_articles_info(con)
    insert_genes_info(con)

    # Close the connection
    con.close()


if __name__ == '__main__':
    main()
