 # #path to input model for dump
 model_in=hdfs://ns1/tmp/mart_jdmp/xgboost/model_out

 # name of model dump file
 name_dump=hdfs://ns1/tmp/mart_jdmp/xgboost/dump.txt

 #whether dump statistics along with model 
 dump_stats=1

 #feature map, used for dump model
 fmap=hdfs://ns1/tmp/mart_jdmp/xgboost/featmap

 # if exist delete name_pred, or an error occurred
 hadoop fs -rm -r $name_dump

 ../package/tracker/dmlc-submit  ../package/xgboost \
 --cluster=yarn  \
 --num-workers=4 \
 --worker-cores=4 \
 --worker-memory=1g \
 --queue root.bdp_hecate_jdmp \
 parameters.conf    nthread=4 \
 model_in=$model_in\
 task=dump \
 name_dump=$name_dump \
 dump_stats=$dump_stats

 # test:data=$test_path \
