#!/bin/bash

#pyuic4 main_window_woop_nolayout.ui -o woop.py
#pyuic4 main_window_woop_noplot.ui -o woop.py
pyuic4 main_window_woop_NO_save_layout_.ui -o woop.py
# following has layout with choice SF data when saving
#pyuic4 main_window_woop_ancestor.ui -o woop.py
pyuic4 test.ui -o test.py



