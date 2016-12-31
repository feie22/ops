 # Notes:
 # This script is an extension to yarn-pred.sh.
 # test file contains row id, this script will
 # remove the ids for prediction, and merge the
 # ids to prediction result.

 #path to input model for test,
 model_in=hdfs://ns2/tmp/user_loss/model_2015_04

 #The path of test data to do prediction
 test_path=hdfs://ns2/tmp/user_loss/test_2015_04 

 #name of prediction file directory
 name_pred=hdfs://ns2/tmp/user_loss/result.pred
 
 pred_result="pred_result"

 # if exist delete name_pred, or an error occurred
 hadoop fs -rm -r $name_pred

 local_test_path=${test_path##*/}
 pred_file=${local_test_path}_
 id_file='ids.txt'
 hdfs dfs -get ${test_path}
 ./split ${local_test_path} $id_file ${pred_file}
 if [ $? -ne 0 ]; then
    exit 1
 fi
 
 target_path=$test_path
 if [ -f ${local_test_path} ]; then
    len=$((${#test_path}-${#local_test_path}))
    target_path=${test_path:0:len}
 fi
 target_test_file="${test_path}/${pred_file}"
 hdfs dfs -put `pwd`/$pred_file $target_path 2>&1 > /dev/null
 
 echo "predicting with $target_test_file "
 ../package/tracker/dmlc-submit  ../package/xgboost \
 --cluster=yarn  \
 --num-workers=4 \
 --worker-cores=1 \
 --worker-memory=12g \
 --queue root.bdp_hecate_jdmp \
 parameters.conf    nthread=4 \
 model_in=$model_in\
 task=pred \
 test:data=${target_test_file} \
 name_pred=$name_pred

 hdfs dfs -get $name_pred 2>&1 >/dev/null
 ./merge ${id_file} ${name_pred##*/} $pred_result

 /bin/rm $pred_file
 /bin/rm $id_file
 /bin/rm -r ${name_pred##*/}
 hdfs dfs -rm ${target_path}/${pred_file}

