 #!/bin/bash

# setup pathes, please use absolute path


SPARK_HOME=<path to folder you created>/spark-2.1.1-bin-hadoop2.7
BigDL_HOME=<path to folder you created>/dist-spark-2.1.1-scala-2.11.8-mac-0.2.0-dist

# export PYSPARK_DRIVER_PYTHON=/Users/roshkhadka/anaconda/bin/jupyter
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --notebook-dir=./ --ip=* --no-browser"
VERSION=0.2.0

${SPARK_HOME}/bin/pyspark \
  --master local[2] \
  --driver-memory 5g \
  --properties-file ${BigDL_HOME}/conf/spark-bigdl.conf \
  --py-files ${BigDL_HOME}/lib/bigdl-${VERSION}-python-api.zip \
  --jars ${BigDL_HOME}/lib/bigdl-SPARK_2.1-${VERSION}-jar-with-dependencies.jar \
  --conf spark.driver.extraClassPath=${BigDL_HOME}/lib/bigdl-SPARK_2.1-${VERSION}-jar-with-dependencies.jar \
  --conf spark.executor.extraClassPath=${BigDL_HOME}/lib/bigdl-SPARK_2.1-${VERSION}-jar-with-dependencies.jar
