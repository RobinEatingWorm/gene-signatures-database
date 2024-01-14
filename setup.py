from Bio import Entrez
from pymed import PubMed

import pandas as pd

from datetime import date
import json
import os
import sys
import time

with open("params.json") as file:
    params = json.load(file)
    articles_dir = params["articles"]["dir"]
    articles_file = params["articles"]["file"]
    email = params["email"]

# === Statistics as of Dec 24 2023 ===
# Number of PubMed Articles: 352720
# Number of PMC Articles: 193547
# Number of PMC Open Access Subset Articles: 85165


def query(year_first: int, year_last: int) -> None:
    """
    Query PubMed for articles using PyMed.
    :param year_first: The earliest publication year to send in the query.
    :param year_last: The latest publication year to send in the query.
    """

    # Initialize objects to retrieve and store article data
    data = []
    pubmed = PubMed(tool="pymed", email=email)

    # Send separate queries for each month in each year
    for year in range(year_first, year_last):
        for month in range(1, 13):
            print(f"Date: {year}/{month:02d}", end=" ")

            # Send HTTP requests until a successful one occurs
            ok = 0
            while not ok:
                try:
                    results = pubmed.query(f"(gene signature OR gene set) AND {year}/{month} [dp]", max_results=9999)

                    # Extract relevant information
                    data_temp = []
                    for article in results:
                        data_temp.append(pd.DataFrame({
                            "title": [article.title],
                            "journal": [article.journal if hasattr(article, "journal") else ""],
                            "publication_date": [article.publication_date],
                            "pmid": [article.pubmed_id.split("\n")[0]],
                        }))
                    ok = 1
                except Exception as e:
                    print(f"{type(e).__name__}: {e}", file=sys.stderr)

            # Keep complete article information
            print(f"Number of Articles: {len(data_temp)}")
            data.extend(data_temp)
            time.sleep(0.1)

    # Save the data as a file
    data = pd.concat(data, axis=0)
    data.to_csv(articles_file, sep="\t", index=False)


def get_pmcid(pmid: str) -> str:
    """
    Get the PMCID of an article given its PMID.
    :param pmid: The PMID of the article.
    :return: The PMCID of the article.
    """

    # Get the PMCID from a handle
    ok = 0
    while not ok:
        try:
            handle = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pmc")
            record = Entrez.read(handle)
            handle.close()
            ok = 1
        except Exception as e:
            print(f"{type(e).__name__}: {e}", file=sys.stderr)

    # Format the PMCID correctly if one exists
    pmcid = ""
    if record[0]["LinkSetDb"]:
        pmcid = "PMC" + record[0]["LinkSetDb"][0]["Link"][0]["Id"]
    print(pmcid)
    return pmcid


def get_pmcids() -> None:
    """
    Add PMCIDs to all articles in the file.
    """

    # Read the data from the file
    data = pd.read_csv(articles_file, sep="\t", dtype=object)
    print(f"Number of Articles: {data.shape[0]}")

    # Set email for Entrez
    Entrez.email = email

    # Add a column of PMCIDs
    data["pmcid"] = data["pmid"].map(get_pmcid)

    # Save the data
    data.to_csv(articles_file, sep="\t", index=False)


def get_pmcids_batch(batch_size: int, start: int) -> None:
    """
    Add PMCIDs to articles in the file beginning from the article at the start
    index. Save the file periodically after every batch_size PMCIDs are
    added.
    :param batch_size: The number of articles to search for PMCIDs before
    saving the file.
    :param start: The index of the first article to start adding PMCIDs.
    """

    # Read the data from the file
    data = pd.read_csv(articles_file, sep="\t", dtype=object)
    print(f"Number of Articles: {data.shape[0]}")

    # Set email for Entrez
    Entrez.email = email

    # Add an empty column for PMCIDs if necessary
    if "pmcid" not in data:
        data["pmcid"] = ""

    # Iterate through file beginning at start index to get PMCIDs
    while start < data.shape[0]:
        end = min([start + batch_size, data.shape[0]])
        print(f"Retrieving PMCIDs for articles {start} to {end - 1}...")

        # Add PMCIDs for indices from start index to end index
        data.loc[start:end, "pmcid"] = data.loc[start:end, "pmid"].map(get_pmcid)

        # Save the data
        data.to_csv(articles_file, sep="\t", index=False)
        start = end


def get_article_text(max_processes: int) -> None:
    """
    Get text from articles in the PMC Open Access Subset.
    :param max_processes: The maximum number of child processes to create.
    """

    # Read the data from the file
    data = pd.read_csv(articles_file, sep="\t", dtype=object)

    # Get all PMCIDs
    pmcids = data["pmcid"].dropna().to_numpy()
    print(f"Number of Articles: {pmcids.size}")

    # Command to run
    cmd = "aws s3 cp s3://pmc-oa-opendata/{dir}/txt/all/{pmcid}.txt --no-sign-request {articles_dir}"

    # Iterate through PMCIDs
    start = 0
    while start < pmcids.size:
        end = min([start + max_processes, pmcids.size])

        # Use the AWS CLI to download article text
        print(f"Retrieving texts for articles {start} to {end - 1}...")
        for i in range(start, end):
            if os.fork() == 0:
                os.system(cmd.format(dir="oa_comm", pmcid=pmcids[i], articles_dir=articles_dir))
                os.system(cmd.format(dir="oa_noncomm", pmcid=pmcids[i], articles_dir=articles_dir))
                os.system(cmd.format(dir="phe_timebound", pmcid=pmcids[i], articles_dir=articles_dir))
                print(f"Index: {i} PMCID: {pmcids[i]}")
                sys.exit()

        # Wait for all child processes to exit
        for i in range(start, end):
            os.wait()
        start = end


def main() -> None:
    """
    Run all setup functions in order.
    """

    # Run queries from 1951 (date of the first gene set/signature article) to next year
    # query(1951, date.today().year + 1)

    # Get PMCIDs for each article
    # get_pmcids()

    # Alternate function to get PMCIDs
    # get_pmcids_batch(500, 0)

    # Get a sample of articles
    get_article_text(500)


if __name__ == "__main__":
    main()
