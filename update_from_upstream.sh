#!/bin.sh

git checkout master && git fetch -v --progress "upstream" master && git push -v --progress "origin" master:master && git checkout Ender3Pro_MKSGenL && git merge master && git push -v --progress "origin" Ender3Pro_MKSGenL:Ender3Pro_MKSGenL
