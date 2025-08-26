#!/bin/bash

# Virtual environment
source venv/bin/activate

# Validation set batches
for (( i=1 ; i<=8 ; i++ ))
do
    python3 run/run.py $i -c --val-set
done

# A demonstration of asynchronously processing a batch (using the validation set and prompt 5)
# python3 run/run.py 5 -es --val-set

# A demonstration of asynchronously processing a batch (using the validation set and prompt 5)
# python3 run/run.py 5 -e --val-set
