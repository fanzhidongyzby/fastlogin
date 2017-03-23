#!/bin/bash
cd $(dirname $0)
ROOT=$(pwd)
python $ROOT/main.py $@
