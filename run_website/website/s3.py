import pulumi 
import pulumi_aws as aws 



def CreateBuckets(dns):
    bucket_policy = f'''{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::{dns}/*"
                ]
            }}
        ]
    }}'''
    
    www_policy = f'''{{
        "Version": "2012-10-17",
        "Statement": [
            {{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::www.{dns}/*"
                ]
            }}
        ]
    }}'''
    
    bucket = aws.s3.Bucket(f"{dns}",
                                  bucket = f"{dns}",   
                                  acl= "public-read",
                                  tags= {
                                      "Name": dns,
                                         "Environment": "Pulumi"},
                                  policy = bucket_policy,
                                  website=aws.s3.BucketWebsiteArgs(
                                    index_document="index.html",
                                    error_document = "error.html"
                                  ))
    
      #bucket for redirect for www
    www_bucket = aws.s3.Bucket(f"www.{dns}",
                              bucket= f"www.{dns}",
                              tags= {
                                  "Name": f"www.{dns}",
                                  "Environment": "Pulumi"
                              },
                              policy = www_policy,
                              website= aws.s3.BucketWebsiteArgs(
                                redirect_all_requests_to= "https://richardcraddock.me"
                              ))
    

    #artifactbucket
    codepipeline_artifact_store = aws.s3.Bucket("codepipelineBucketArtifactStore",
                                              tags={
                                                  "Name": "artifact_bucket",
                                                  "Environment": "Pulumi"
                                              })
  
    pulumi.export("Buckets",{
    "richardcraddock_bucket_arn": bucket.arn,
    "www.richardcraddock_bucket_arn": www_bucket.arn,
    "artifact_bucket_arn": codepipeline_artifact_store.arn
    })
    return {
        "bucket_id":
            [bucket.id,www_bucket.id],
        "bucket_regional_domain_name":
            [bucket.bucket_regional_domain_name,www_bucket.bucket_regional_domain_name],
        "artifact_bucket": codepipeline_artifact_store.bucket,
        "artifact_bucket_arn": codepipeline_artifact_store.arn,
        "bucket_name": bucket._name
              }



