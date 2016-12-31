 # path to input model, it's an optional argument, xgboost will continue training from the input model
 model_in=hdfs://ns1/tmp/mart_jdmp/xgboost/model_in

 #The path of training data
 train_path=hdfs://ns1/tmp/mart_jdmp/xgboost/data/train_1000W_737_ORDER

 # for evaluating statistics 
 eval_path=hdfs://ns1/tmp/mart_jdmp/xgboost/data/test_100W_737_ORDER

 # path to output model after training finishes, if not specified, will output like 0003.model where 0003 is number of rounds to do boosting
 model_out_path=hdfs://ns1/tmp/mart_jdmp/xgboost/model_out

 #The output directory of the saved models during training
 model_dir=hdfs://ns1/tmp/mart_jdmp/xgboost/model_dir

 # if exist delete model_out path, or an error occurred 
 hadoop fs -rm -r $model_out_path

 ../package/tracker/dmlc-submit  ../package/xgboost \
 --cluster=yarn  \
 --num-workers=10 \
 --worker-cores=4 \
 --worker-memory=16g \
 --queue root.bdp_hecate_jdmp \
  parameters.conf    nthread=4 \
  data=$train_path \
  eval[test]=$eval_path \
  model_out=$model_out_path \
