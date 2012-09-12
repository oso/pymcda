#!/bin/sh

cat "$1" | column -s, -t | less -#8 -N -S
