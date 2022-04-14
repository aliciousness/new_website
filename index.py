from distutils.log import info
import zipfile,boto3,os
from io import BytesIO

#to update the zip package---
#zip -g lambda.zip index.py
print('Initialising')
BUCKET='codepipelinebucketzipped'
key='resume.zip'
s3 = boto3.resource('s3')
my_bucket = s3.Bucket(BUCKET)

def handler(event,context):

  filebytes = BytesIO()

  my_bucket.download_fileobj(key, filebytes)

  file = zipfile.ZipFile(filebytes)

  print("start uploading files", file)
  file.extractall('/tmp')
  path = '/tmp'
  
  for root,dirs,files in os.walk(path):
    for name in files:
      
      upload_file_bucket = os.path.join(root,name)
      combo = upload_file_bucket[5::]
      print(f"file {combo} added to bucket")
      bucket = 'richardcraddock.me'
      s3.meta.client.upload_file(upload_file_bucket,bucket,combo)
  
  return "SUCCESS"
  