 #path to input model for test,
 model_in=hdfs://ns1/tmp/mart_jdmp/xgboost/model_out

 #The path of test data to do prediction
 test_path=hdfs://ns1/tmp/mart_jdmp/xgboost/data/test_100W_737_ORDER

 #name of prediction file directory
 name_pred=hdfs://ns1/tmp/mart_jdmp/xgboost/pred

 # if exist delete name_pred, or an error occurred
 hadoop fs -rm -r $name_pred

 ../package/tracker/dmlc-submit  ../package/xgboost \
 --cluster=yarn  \
 --num-workers=4 \
 --worker-cores=1 \
 --worker-memory=12g \
 --queue root.bdp_hecate_jdmp \
 parameters.conf    nthread=4 \
 model_in=$model_in\
 task=pred \
 test:data=$test_path \
 name_pred=$name_pred
