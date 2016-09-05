#!/bin/sh

SCRIPT=test_lp_avfsort_csv.py
DATADIR=$HOME/pymcda-data
DATASETS="cpu.csv era.csv lev.csv mpg.csv cev.csv dbs.csv \
	  esl.csv mmg.csv swd.csv bcc.csv
	  lev_5_categories.csv era_4_categories.csv \
	  cpu_4_categories.csv cev_4_categories.csv"
NSEGMENTS=10

for dataset in $DATASETS; do
	echo $dataset
	timestamp=$(date +"%Y%m%d-%H%M")
	python $SCRIPT -i ../datasets/$dataset -p 20,50,80 -k $NSEGMENTS \
		-f $DATADIR/lp_avfsort-$dataset-$timestamp.csv -s 100
done
