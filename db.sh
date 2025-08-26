#!/bin/bash

# Virtual environment
source venv/bin/activate

# Create a database and insert data
sqlite3 db/sqlite.db -init db/schema.sql | :
python3 db/insert_data.py

# A demonstration of inserting gene signatures (from validation results for prompt 5)
# python3 db/insert_gene_signatures.py 5 --val-set
