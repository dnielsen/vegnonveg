#!/bin/bash

# setup paths, please use absolute path
INSTALL_HOME=/
export PATH=/root/anaconda3/bin:$PATH
export JAVA_HOME="/root/anaconda3/"
export SPARK_HOME=$INSTALL_HOME/spark-2.2.0-bin-hadoop2.7
export BigDL_HOME=$INSTALL_HOME/dist-spark-2.2.0-scala-2.11.8-linux64-0.3.0-dist

export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --allow-root --notebook-dir=./notebooks --ip=* --no-browser --certfile=mycert.pem --keyfile=mykey.key --NotebookApp.token='bigdl'"
VERSION=0.3.0
source activate py27
# tensorboard --logdir=/tmp/bigdl_summaries/lenet5-  2>&1 >tensorboard.log &

if [ -z "$CORES" ]; then
	CORES=2
fi

${SPARK_HOME}/bin/pyspark \
  --master local[$CORES] \
  --driver-memory 5g \
  --properties-file ${BigDL_HOME}/conf/spark-bigdl.conf \
  --py-files ${BigDL_HOME}/lib/bigdl-${VERSION}-python-api.zip \
  --jars ${BigDL_HOME}/lib/bigdl-SPARK_2.2-${VERSION}-jar-with-dependencies.jar \
  --conf spark.driver.extraClassPath=${BigDL_HOME}/lib/bigdl-SPARK_2.2-${VERSION}-jar-with-dependencies.jar \
  --conf spark.executor.extraClassPath=${BigDL_HOME}/lib/bigdl-SPARK_2.2-${VERSION}-jar-with-dependencies.jar
  
