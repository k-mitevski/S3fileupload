import boto3
import sys
import os
import time
import threading

class ProgressPercentage(object): #class used for progress tracking of file

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

inputFile = str(sys.argv[1]) #pass the input file as cmd argument

def uploadtoS3(bucketName):

    s3 = boto3.client('s3')
    response = s3.list_buckets()
    bucketName = ('files-from-desktop') # name of the bucket(you will need to change it)
    list = []

    for i in range(0,len(response['Buckets'])):
        list.append(response['Buckets'][i]['Name']) # bucket checks if it exists pass, else to create a new one
    if bucketName in list:
        print(bucketName + ' bucket already exists')
    else:
        flag = s3.create_bucket(Bucket=bucketName,CreateBucketConfiguration={
            'LocationConstraint': 'eu-central-1'
        })
        if flag['ResponseMetadata']['HTTPStatusCode'] == 200: # OK response check
            print('Bucket creation successful')

        response_acl = s3.put_public_access_block( # lock the bucket so it doesn't go public
            Bucket=bucketName,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        if response_acl['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Block public access successful')

    head, tail = os.path.split(inputFile) # get the path from the input file
    s3.upload_file(inputFile, bucketName, tail, Callback=ProgressPercentage(inputFile)) # file upload

    print('\nfile: ' + tail + ' uploaded.')
    time.sleep(2)

uploadtoS3(inputFile)
