import json

with open('paths.json') as file:
    paths = json.load(file)


def get_query(query_name: str) -> str:
    """
    Read a SQL query from a file.
    :query_name: The name of the query.
    :return: A SQL query.
    """

    # Read the file
    with open(paths['db']['query'].format(query_name=query_name)) as file:
        query = file.readlines()

    # Format the query
    return ''.join(query)
