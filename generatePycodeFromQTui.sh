#!/bin/bash

#pyuic4 main_window_woop_nolayout.ui -o woop.py
#pyuic4 main_window_woop_noplot.ui -o woop.py
pyuic4 main_window_woop_ancestor.ui -o woop.py
pyuic4 test.ui -o test.py



