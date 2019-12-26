#!/bin/bash
source config.conf
python3 functions.py "$DIRPATH" $METH $IP_URL_ADDRESS $LOGIN $PASSWORD $SAVEPATH $NREP $VERSIONNUMBER
