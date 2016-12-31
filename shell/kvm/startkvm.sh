#!/bin/bash
xmlf="kvm_hadp.xml"
for f in `ls *.xml|grep -v temp|grep -v $xmlf`
    do
        name=${f%%\.*}
        virsh define $f
        virsh start $name
    done
