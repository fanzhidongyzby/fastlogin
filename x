#!/bin/bash
if [[ -z $(readlink $0) ]]; then
  cd $(dirname $0)
else
  cd $(dirname $(readlink $0))
fi
ROOT=$(pwd)
python $ROOT/main.py "$@"
