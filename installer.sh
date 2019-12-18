#!/bin/bash
filename=$1

unzip -o ./bin/bundle.zip sim-meta.json -d ./bin/

for ((i=0;i<$(jq '. | length' ./bin/sim-meta.json);i++))
        do
                var1=$(jq -j .[$i]'["folderName"]' ./bin/sim-meta.json)
                echo $var1
                var2=$(jq -j .[$i]'["unpackTo"]' ./bin/sim-meta.json)
                echo $var2
                #var3=~/Desktop/
                #echo $var2$var3


                #if [ $var2 = "/Desktop/" ]
                #then
                #       unzip -o $filename $var1/* -d ~/Desktop/
                #else
                #       unzip -o $filename $var1/* -d $var2
                #fi

                unzip -o $filename $var1/* -d /home/$USER$var2

        done


#To run use the following command:
#./installer.sh ./bin/bundle.zip
#
#If extracting to Desktop, make sure to either include full path in json file such as "/home/mb/Desktop/" or use "/Desktop/" and unquote the if loop I wrote, then remove the second unzip command. For some reason "~/Desktop/" or just "Desktop" by itself will not work when using a json file variable. 
