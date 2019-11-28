#!/bin/bash
filename=$1
location=$2
tar xvzf $filename -C $location

#First parameter is the tar file name and location
#Second parameter is the location to extract it to
#For example: ./installer.sh /home/mb/Desktop/backendSample.tar.gz /home/mb/git/installertest
