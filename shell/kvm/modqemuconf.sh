#!/bin/bash
net=103
qemup="/etc/libvirt/qemu"
xmlf="kvm_hadp.xml"
domain="kvm_hadp"
imgp="/data0/kvm"
imgp_b="/data0/kvm_base"
imgt="qcow2"
imgf="kvm_hadp.$imgt"

#new="hadp"
for i in `seq 51 60`
    do
        new="$net$i"
        #virsh dumpxml $domain > $qemup/kvm_hadp_$new.xml
        cp $xmlf $qemup/kvm_hadp_$new.xml
        if [[ ! -s $imgp/kvm_hadp_$new.$imgt ]]
            then
                qemu-img create -f qcow2  $imgp/kvm_hadp_$new.$imgt -o backing_file=$imgp_b/$imgf
                for k in {b..m}
                    do
                        qemu-img create -f qcow2  $imgp/kvm_hadp_${new}_vd$k.$imgt -o backing_file=$imgp_b/kvm_hadp_vd$k.$imgt
                    done
        else
            echo "$imgp/kvm_hadp_$new.img exists!"
        fi
        #cp -rvf $qemup/$xmlf $qemup/kvm_hadp_$new.xml
        #cp -av $imgp/$imgf $imgp/kvm_hadp_$new.img
        #echo $f
        
        name=${domain}_$new
        f=${name}.xml
        uuid=`uuidgen`
        vip="172.19.$net.$i"
        #macaddr=`openssl rand -hex 6|sed 's/\(..\)/\1:/g;s/:$//g'`
        #macaddr=`openssl rand -hex 6 |sed -r 's/(..)(..)(..)(..)(..)(..)/52:54:\3:\4:\5:\6/'`
        macaddr=`awk -v ip=$vip '{if($2==ip){print $1}}' mac-ip.list`
        echo $name
        echo $uuid
        echo $macaddr
        sed -i "s;<name>.*<\/name>;<name>$name<\/name>;g" $f
        sed -i "s;<uuid>.*<\/uuid>;<uuid>$uuid<\/uuid>;g" $f
        sed -i "s;<mac address=.*/>;<mac address='$(echo $macaddr)'/>;g" $f
        sed -i "s;<source file='/data0/kvm/kvm_hadp.qcow2'/>;<source file='/data0/kvm/$(echo $name).$imgt'/>;g" $f
        for n in {b..m}
            do
                sed -i "s;/data0/kvm/kvm_hadp_vd$n.qcow2;/data0/kvm/kvm_hadp_${new}_vd$n.qcow2;g" $f
            done
    done

