#!/bin/sh

NB_TEST_SETS=5
PYTHON_SCRIPT=MRSortMeta.py

CURRENT_DIR=$(pwd)
cd ..
for i in $(seq $NB_TEST_SETS); do
	python $PYTHON_SCRIPT --in $CURRENT_DIR/in$i --out $CURRENT_DIR/out$i
	if [ $? == 0 ]; then
		echo "Test $i ok";
	else
		echo "Test $i failed";
	fi
done
echo "Test 5 fails... it's 'normal' ;-)"
