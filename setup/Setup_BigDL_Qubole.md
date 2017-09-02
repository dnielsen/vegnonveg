# Setting up BigDL (Python) on Qubole

### Follow these instructions:

Set up a Qubole Account and link it to AWS: [Part 1](https://www.qubole.com/blog/deep-learning-qubole-using-intels-bigdl-apache-spark-part-1/)

Run BigDL on Qubole: [Part 2](https://www.qubole.com/blog/deep-learning-qubole-using-bigdl-apache-spark-part-2/)

The instructions provided above sets up a Qubole account so you can train a LeNet5 Model on the MNIST dataset using BigDL's Scala API on a Spark Cluster.

In order to get the Python API working on qubole:
1. Download the Python dependencies into your s3 bucket.  add the Python dependencies to your **Spark Context (sc)**.

'''python
%pyspark
sc.addPyFile('s3://<YOUR S3 BUCKET NAME>/external-jars/bigdl-0.2.0-python.zip')
'''

You can manually download the .zip file from here:    , inside this you can find a jar file and a python.zip file. Upload the .zip file to your aws s3 bucket and paste it in the link above.
