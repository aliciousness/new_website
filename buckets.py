import pulumi 
import pulumi_aws as aws 


#website buckets 
website_buckets = []

  #bucket for lambda
lambda_bucket = aws.s3.Bucket("richardcraddock.me",
                              bucket = "richardcraddock.me",  #need to change bucket name to .me and change it in the lambda and zip it up 
                              acl= "public-read",
                              # hosted_zone_id= zone.zone_id,
                              # website_domain= "http://richardcraddock.me",
                              website=aws.s3.BucketWebsiteArgs(
                                index_document="index.html",
                                error_document = "error.html"
                              ))
website_buckets.append(lambda_bucket)
  #bucket for redirect for www
www_bucket = aws.s3.Bucket("www.richardcraddock.me",
                           bucket= "www.richardcraddock.me",
                           website= aws.s3.BucketWebsiteArgs(
                             redirect_all_requests_to= "http://richardcraddock.me"
                           ))
website_buckets.append(www_bucket)

#artifactbucket
codepipeline_artifact_store = aws.s3.Bucket("codepipelineBucketArtifactStore",)