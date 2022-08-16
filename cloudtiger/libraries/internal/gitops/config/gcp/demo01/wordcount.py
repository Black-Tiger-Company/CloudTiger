import sys
 
from pyspark import SparkContext, SparkConf
from datetime import date, datetime
# import cloudstorage as gcs
import google.cloud.storage as gcs

BUCKET_NAME_OUTPUT = "eg-blacktiger"
BUCKET_NAME_SOURCE = "eg-blacktiger-notif"

if __name__ == "__main__":
	
	print("Begin process")
	# create Spark context with necessary configuration
	sc = SparkContext("local","PySpark Word Count Exmaple")
	
	# read data from text file and split each line into words
	textFile = sc.textFile("gs://" + BUCKET_NAME_SOURCE + "/roiLear.txt")
	words = textFile.flatMap(lambda line: line.split(" "))
	# display some information
	start = datetime.now()
	# dd/mm/YY
	d1 = start.strftime("%d/%m/%Y")
	textName = textFile.name().split("/")[-1]
	print('New File detected: ', textName, ' ', d1)
	
	# count the occurrence of each word
	wordCounts = words.map(lambda word: (word, 1)).reduceByKey(lambda a,b:a +b)

	# save the counts to output
	pathGCP = "gs://"+ BUCKET_NAME_OUTPUT +"/pyspark/output/" + textName.split('.')[0] + "_result"
	pathGCP2 = "pyspark/output/" + textName.split('.')[0] + "_result"
	storage_client = gcs.Client()
	bucket = storage_client.get_bucket(BUCKET_NAME_OUTPUT)
	"""Delete object under folder"""
	print("start deleting: ", "pyspark/output/" + textName.split('.')[0] + "_result/")
	blobs = list(bucket.list_blobs(prefix="pyspark/output/" + textName.split('.')[0] + "_result"))
	bucket.delete_blobs(blobs)
	print("Folder deleted.")
	wordCounts.saveAsTextFile(pathGCP)
	end = datetime.now()
	bucket.blob(pathGCP2 + "/information.txt")
	storage_client.close()
	#wordCounts.toDF().write.format("txt").mode("overwrite").save(pathGCP)
	# with open(pathGCP + "/information.txt", "w") as file:
	# 	file.write('execution time = ', datetime.timestamp(end) - datetime.timestamp(start) ," ms")
