#/bin/bash
i=1

while [ $i -le 10 ]
do
	echo $i
	sleep 0.5
	let ++i
done
