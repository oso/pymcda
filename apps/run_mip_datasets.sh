#!/bin/sh

SCRIPT=test_mip_mrsort_csv.py
DATADIR=$HOME/pymcda-data

run_mip() {
	dataset=$1
	size="$2"
	timestamp=$(date +"%Y%m%d-%H%M")
	python $SCRIPT -i ../datasets/$dataset -p $size \
		-f $DATADIR/mip-$dataset-$timestamp.csv -s 100
}

run_mip dbs.csv 20,50,80
run_mip cpu.csv 20,50,80
run_mip bcc.csv 20
run_mip mpg.csv 20
run_mip esl.csv 20,50,80
run_mip mmg.csv 20
run_mip era.csv 20,50,80
run_mip lev.csv 20,50,80
