#!/bin/bash

dir=`dirname $0`
export PYTHONPATH="$dir"
python3 $dir/midi_extractor.py $*