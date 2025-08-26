#!/bin/bash

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install -i $(realpath aws-cli) -b $(realpath venv/bin)
rm -rf aws awscliv2.zip

# Get article info
export SSL_CERT_FILE=$(python3 -m certifi)
export REQUESTS_CA_BUNDLE=$(python3 -m certifi)
nohup python3 -u setup/articles.py > logs/nohup.out &

# Get gene info
Rscript setup/genes.R
