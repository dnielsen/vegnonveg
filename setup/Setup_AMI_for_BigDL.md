# Setting up Amazon Machine Image (linux) with BigDL dependencies

## This tutorial will teach you how to set up an AMI with software configuration to run BigDL deep learning applications.

## Launch an AWS EC2 Instance

1) Create an AMI.  Choose **Ubuntu Server 14.04 LTS (HVM)**

## SSH into your AMI

```
ssh -i "<yourkey>.pem" ubuntu@<your instance id>
```

Example:

ssh -i "mykey.pem" ubuntu@ec2-55-174-6-213.compute-1.amazonaws.com


## Install Dependencies

### 1) Install Anaconda
In your home directory, **/home/ubuntu**, install anaconda with this command:
```
curl -O https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh
```
Run the script:
```
bash Anaconda3-4.2.0-Linux-x86_64.sh
```
Follow the command prompt to finish the installation. When prompted:

Do you wish the installer to prepend the Anaconda3 install location
to PATH in your /home/sammy/.bashrc ? [yes|no]

Choose "yes" so you can use the conda command.

Verify installation of anaconda by typing the command:
```
conda list
```
You’ll receive output of all the packages you have available through the Anaconda installation.

### 2) Install Java on root:
```
conda install -c reeder java-jdk
```
### 3) Create a Python 2.7 virtual environment

Use the command:
```
conda create -n py27 python=2.7 anaconda
```
Switch to the Python 2.7 environment.

Run:
```
source activate py27
```

### 4) Install Java on your new environment

```
conda install -c reeder java-jdk
```

### 5) Install BigDL

Create a folder called bigdl and cd:

```
mkdir bigdl
cd bigdl
```

Download bigdl:

```
wget https://repo1.maven.org/maven2/com/intel/analytics/bigdl/dist-spark-2.1.1-scala-2.11.8-linux64/0.2.0/dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist.zip
```

Unzip the zip file by running these commands:
```
sudo apt-get install unzip
mkdir dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist
unzip dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist.zip dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist
```

Your **dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist** folder should have lib, conf and bin folders.

### 6) Install Spark

Make sure you are in the **bigdl** directory.  Run:
```
wget https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.7.tgz
```

Unzip:
```
tar -xzf spark-2.1.1-bin-hadoop2.7.tgz
```

### 7) Download the starter script

Create a file called **start_notebook.sh**. Copy and paste the contents from the code below into start_notebook.sh:

```
SPARK_HOME=/home/ubuntu/bigdl/spark-2.1.1-bin-hadoop2.7
BigDL_HOME=/home/ubuntu/bigdl/dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist

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
```

### 8) Create the lenet jupyter notebook to test out.

Copy and paste the contents from [cnn.ipynb](cnn.ipynb) to a file called **lenet.ipynb**.

### 9) Create a utils.py file

#### Copy and paste the following code into a file called **utils.py**.

```python
import numpy as np
from bigdl.util import common
from bigdl.dataset import mnist

def get_mnist(sc, mnist_path):
    # target is start from 0,
    (train_images, train_labels) = mnist.read_data_sets(mnist_path, "train")
    (test_images, test_labels) = mnist.read_data_sets(mnist_path, "test")
    training_mean = np.mean(train_images)
    training_std = np.std(train_images)
    rdd_train_images = sc.parallelize(train_images)
    rdd_train_labels = sc.parallelize(train_labels)
    rdd_test_images = sc.parallelize(test_images)
    rdd_test_labels = sc.parallelize(test_labels)

    rdd_train_sample = rdd_train_images.zip(rdd_train_labels).map(lambda (features, label):
                                        common.Sample.from_ndarray(
                                        (features - training_mean) / training_std,
                                        label + 1))
    rdd_test_sample = rdd_test_images.zip(rdd_test_labels).map(lambda (features, label):
                                        common.Sample.from_ndarray(
                                        (features - training_mean) / training_std,
                                        label + 1))
    return (rdd_train_sample, rdd_test_sample)
```
### 10) Verify that your bigdl folder has the following things:

-dist-spark-2.1.1-scala-2.11.8-linux64-0.2.0-dist

-spark-2.1.1-bin-hadoop2.7  

-lenet.ipynb

-utils.py

-start_notebook.sh

### 11) Run the script to launch Jupyter Notebooks:
```
./start_notebook.sh
```

This should launch the Jupyter Notebooks server. Make sure your AWS instance is up and running.

In your browser type in, for example:

**ec2-34-229-7-73.compute-1.amazonaws.com:8888**

If you are prompted to enter a password:

**Password: deepblue**

Try running lenet.ipynb.

## Run inception_v1

### 1) Clone the vegnonveg repository into your bigdl folder.

```
git clone https://github.com/dnielsen/vegnonveg.git
```

### 2) Install the package **opencv**.

```
conda install opencv
```

### 3) Navigate to the /vegnonveg/python/inception_v1 folder.  Then, download caffe's pre-trained model with this command:

```
wget http://dl.caffe.berkeleyvision.org/bvlc_googlenet.caffemodel
```


### 4) Run **inception_v1.ipynb**.

Go run Jupyter Notebooks by going back to the **bigdl** directory and running **./start_notebook.sh**.

note: inception_v1.ipynb is located in ./vegnonveg/python/inception_v1.
