#! /bin/bash
vdb-config --prefetch-to-cwd

while read line; do
        echo importing $line
        prefetch $line
        fasterq-dump $line
        rm -r $line
done < ids.csv

