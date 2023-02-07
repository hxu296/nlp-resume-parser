#! /bin/sh

# Build Assumptions:
# Python3 and pip3 are installed properly
# apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
mkdir -p application/uploads
pip3 install -r build/requirements.txt
echo "$0 finished running"
