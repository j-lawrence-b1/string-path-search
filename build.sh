#!/bin/bash
# Assumes GNU make is installed and the path to the make program is in your shell PATH.
exec make -f Makefile.linux $*
