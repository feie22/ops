#!/bin/bash                                                               
#判断用户输入的是否是数字                                         
count=1
read -p "请输入一个数值: " num                                  
                                                                                   
while :                                                                        
do                                                                               
        if [[ $num =~ ^[0-9]+$ ]];then                        
                break                                                         
        else                                                                    
		if [ $count -eq 3 ];then
			echo "输入3次错误，程序退出!"
			exit 1
		fi
                read -p "不是数字，请重新输入数值: " num  
        fi                                                                         
	let count++
done                                                                           
                                                                                   
echo "你输入的数字是: $num"
