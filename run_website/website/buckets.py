import pulumi 
import pulumi_aws as aws 




def CreateBuckets(dns):
  bucket = aws.s3.Bucket(f"{dns}",
                                  bucket = f"{dns}",   
                                  acl= "public-read",
                                  policy = f'''{{
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
    }}''',
                                  website=aws.s3.BucketWebsiteArgs(
                                    index_document="index.html",
                                    error_document = "error.html"
                                  ))
    
      #bucket for redirect for www
  www_bucket = aws.s3.Bucket(f"www.{dns}",
                              bucket= f"www.{dns}",
                              policy = f'''{{
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
}}''',
                              website= aws.s3.BucketWebsiteArgs(
                                redirect_all_requests_to= "https://richardcraddock.me"
                              ))
    

    #artifactbucket
  codepipeline_artifact_store = aws.s3.Bucket("codepipelineBucketArtifactStore",)
  
  pulumi.export("Buckets",{
    "richardcraddock_bucket_arn": bucket.arn,
    "www.richardcraddock_bucket_arn": www_bucket.arn,
    "artifact_bucket_arn": codepipeline_artifact_store.arn
    })
  



