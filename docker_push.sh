#!/bin/bash
echo "Waiting 2 minutes for the package to be available on PyPI"
sleep 2m
cd docker/
make publish
