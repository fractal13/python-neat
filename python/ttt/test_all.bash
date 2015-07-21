#!/bin/bash

for i in `seq 1 9`; do
    rm -f winner.$i
    for j in `seq 1 100`; do
	echo "$i $j"
	python ttt_main.py $i >> winner.$i
    done

done

for i in `seq 1 9`; do
    echo $i
    cat winner.$i | grep ^Winner | sort | uniq -c
    echo
done

