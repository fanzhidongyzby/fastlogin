#!/bin/bash
chmod +x ./inner.py
./inner.py $@ && ./dossh.exp

