#!/bin/bash

#pyuic4 main_window_woop_nolayout.ui -o CORMAT_GUI.py
#pyuic4 main_window_woop_noplot.ui -o CORMAT_GUI.py
#pyuic4 main_window_woop_NO_save_layout_.ui -o CORMAT_GUI.py
# following has layout with choice SF data when saving
#pyuic4 main_window_woop_ancestor.ui -o CORMAT_GUI.py
#pyuic4 main_window_woop_layout2.ui -o CORMAT_GUI.py
#pyuic4 main_window_woop_layout_saveworkspace.ui -o CORMAT_GUI.py
#pyuic4 main_window_woop_layout_manualcorrection_widget.ui -o CORMAT_GUI.py
pyuic4 main_window_woop_layout_manualcorrection_widget_bigger_log.ui -o CORMAT_GUI.py
pyuic4 accept_suggestion.ui -o accept_suggestion.py

#uic main_window_woop_layout.ui -o CORMAT_GUI.h
#uic main_window_woop_layout.ui -i CORMAT_GUI.h -o CORMAT_GUI.cpp
#pyuic4 test.ui -o test.py



