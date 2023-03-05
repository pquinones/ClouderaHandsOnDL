from pyspark.sql import SparkSession
from datetime import datetime
import sys
import configparser

config = configparser.ConfigParser()
config.read('/app/mount/parameters.conf')
data_lake_name=config.get("general","data_lake_name")
s3BucketName=config.get("general","s3BucketName")
username=config.get("general","username")

print("Running as Username: ", username)

spark = SparkSession \
    .builder \
    .appName("ICEBERG LOAD") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")\
    .config("spark.sql.catalog.spark_catalog.type", "hive")\
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
    .config("spark.yarn.access.hadoopFileSystems", data_lake_name)\
    .getOrCreate()

#---------------------------------------------------
#               INSERT DATA
#---------------------------------------------------

# INSERT DATA - APPEND FROM DATAFRAME

spark.sql("TRUNCATE TABLE spark_catalog.{}.telco_data_curated".format(username))

temp_df = spark.sql("SELECT multiplelines, paperlessbilling, d.description as gender, onlinesecurity, internetservice, techsupport, b.description as contract, churn, seniorcitizen, deviceprotection, streamingtv, streamingmovies, totalcharges, c.description as partner, monthlycharges, customerid, e.description as dependents, onlinebackup, phoneservice, tenure, paymentmethod FROM {}.telco_iceberg_kafka a JOIN master_data.contract b ON b.id = contract JOIN master_data.misc c ON c.id = partner JOIN master_data.misc d ON d.id = gender JOIN master_data.misc e ON e.id = dependents".format(username))
temp_df.writeTo("spark_catalog.{}.telco_data_curated".format(username)).append()
