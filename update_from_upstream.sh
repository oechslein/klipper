#!/bin/sh

git remote add -f upstream https://github.com/KevinOConnor/klipper.git
git checkout master && git -v --progress pull && git fetch -v --progress "upstream" master && git push -v --progress "origin" master:master && git checkout Ender3Pro_MKSGenL && git merge master && git push -v --progress "origin" Ender3Pro_MKSGenL:Ender3Pro_MKSGenL

