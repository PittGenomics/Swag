#!/bin/bash

##############################################################
### Start-up graphic
##############################################################
# Graphic colors
ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"

echo -e "$COL_BLUE--------------------------------------------------$COL_RESET"
echo -e "$COL_BLUE--------------------------------------------------$COL_RESET"
echo -e "$COL_GREEN     ____          _  __ _   ____             $COL_RESET"
echo -e "$COL_GREEN    / ___|_      _(_)/ _| |_/ ___|  ___  __ _ $COL_RESET"
echo -e "$COL_GREEN    \___ \ \ /\ / / | |_| __\___ \ / _ \/ _\` |$COL_RESET"
echo -e "$COL_GREEN     ___) \ V  V /| |  _| |_ ___) |  __/ (_| |$COL_RESET"
echo -e "$COL_GREEN    |____/ \_/\_/ |_|_|  \__|____/ \___|\__, |$COL_RESET"
echo -e "$COL_GREEN                                           |_|$COL_RESET"
echo -e "$COL_RED  Developed by Jason J. Pitt and Lorenzo L. Pesce $COL_RESET"
echo "    pittjj@uchicago.edu     lpesce@uchicago.edu"
echo "    Institute for Genomics and Systems Biology"
echo "              Computation Institute"
echo "            The University of Chicago" 
echo -e "$COL_BLUE--------------------------------------------------$COL_RESET"
echo -e "$COL_BLUE--------------------------------------------------$COL_RESET"
# Graphic from Figlet
