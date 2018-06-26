#!/bin/bash

clear

printf "Kör Sapis\n"
echo
python3 SAPIS.py
wait
echo
printf "Sapis klar\n"
echo
printf "Testar träd\n"
echo
python2 dep_test.py
echo
printf "Färdigt\n"
