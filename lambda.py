import zipfile,boto3,os

from io import BytesIO

def lambda_handler(event,context):
  BUCKET='codepipelineBucketZipped'
  key='lambda.zip'
  s3 = boto3.resource('s3')
  my_bucket = s3.Bucket(BUCKET)

  filebytes = BytesIO()

  my_bucket.download_fileobj(key, filebytes)

  file = zipfile.ZipFile(filebytes)

  file.extractall('/tmp')
  path = '/tmp'

  for root,dirs,files in os.walk(path):
    for name in files:
      
      upload_file_bucket = os.path.join(root,name)
      key = upload_file_bucket[5::]
      bucket = 'codepipelinePulumi'
      s3.meta.client.upload_file(upload_file_bucket,bucket,key)