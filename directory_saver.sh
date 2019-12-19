#!/bin/bash
source config.conf
python3 functions.py $REPPATH $METH $IP_URL_ADDRESS $LOGIN $PASSWORD $NREP $VERSIONNUMBER
