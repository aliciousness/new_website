import pulumi 
import pulumi_aws as aws 

dns = "richardcraddock.me"

#find aws hosted zone
zone = aws.route53.get_zone(
                               name = "richardcraddock.me",
                               private_zone= False,
                               
                               )

#website buckets 
website_buckets = []
#bucket for lambda
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
website_buckets.append(bucket)
  #bucket for redirect for www
www_bucket = aws.s3.Bucket(f"www.{dns}",
                           bucket= f"www.{dns}",
                           website= aws.s3.BucketWebsiteArgs(
                             redirect_all_requests_to= "https://richardcraddock.me"
                           ))
website_buckets.append(www_bucket)

#artifactbucket
codepipeline_artifact_store = aws.s3.Bucket("codepipelineBucketArtifactStore",)



#certs for cloudfront
#validate certs in the console 
cert = aws.acm.Certificate("resume_acm_cert",
                           domain_name = "richardcraddock.me",
                           tags={
                             "Name": "Pulumi_resume",
                             "Environment": "richardcraddock.me"
                           },
                           validation_method="DNS")

www_cert = aws.acm.Certificate("www_resume_acm_cert",
                           domain_name = "www.richardcraddock.me",
                           tags={
                             "Name": "Pulumi_resume",
                             "Environment": "www.richardcraddock.me"
                           },
                           validation_method="DNS")

# record = aws.route53.Record(f"{dns}",
#                         name = f"{dns}",
#                         type = "A",
#                         zone_id = zone.zone_id,
#                         aliases= [
#                             aws.route53.RecordAliasArgs(
#                                 evaluate_target_health= False,
#                                 name= bucket.website_domain,
#                                 zone_id=bucket.hosted_zone_id
#                         )]
#                         )


# www_record = aws.route53.Record(f"www.{dns}",
#                         name = f"www.{dns}",
#                         type = "A",
#                         zone_id = zone.zone_id,
#                         aliases= [
#                             aws.route53.RecordAliasArgs(
#                                 evaluate_target_health= False,
#                                 name= www_bucket.website_domain,
#                                 zone_id=www_bucket.hosted_zone_id
#                         )]
#                         )

#need to change if buckets.py changes into a function NOTE
Distribution = aws.cloudfront.Distribution(f'{dns}',
                                             enabled= True,
                                             is_ipv6_enabled=True,
                                             comment = "Resume built with Pulumi",
                                             default_root_object= "index.html",
                                             aliases=["richardcraddock.me"],
                                             wait_for_deployment= False,
                                             origins= [aws.cloudfront.DistributionOriginArgs(
                                               domain_name = bucket.bucket_regional_domain_name,
                                               origin_id= bucket.id
                                            )],
                                            default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
                                              allowed_methods= [
                                                "GET",
                                                "HEAD",
                                                ],
                                              cached_methods = [
                                                "GET",
                                                "HEAD"
                                                ],
                                              target_origin_id= bucket.id,
                                              viewer_protocol_policy= "redirect-to-https",
                                              forwarded_values= aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                                                query_string= False,
                                               cookies =  aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                                                 forward = "none"
                                               )
                                              )
                                            ),
                                            restrictions= aws.cloudfront.DistributionRestrictionsArgs(
                                              geo_restriction= aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                                                restriction_type= "whitelist",
                                                locations=[
                                                  "US",
                                                  "CA",
                                                  "GB",
                                                  "DE"
                                                ]
                                              )
                                            ),
                                            custom_error_responses= [aws.cloudfront.DistributionCustomErrorResponseArgs(
                                              error_code= 404,
                                              response_page_path="/error.html",
                                              response_code= 404
                                            )],
                                            viewer_certificate= aws.cloudfront.DistributionViewerCertificateArgs(
                                              acm_certificate_arn= cert.arn,
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": "Pulumi_resume",
                                              "evnironment": "richardcraddock.me"
                                            }
                                            )

  
www_Distribution = aws.cloudfront.Distribution(f'www.{dns}',
                                             enabled= True,
                                             is_ipv6_enabled=True,
                                             comment = "Resume built with Pulumi",
                                             default_root_object= "index.html",
                                             aliases=["www.richardcraddock.me"],
                                             wait_for_deployment= False,
                                             origins= [aws.cloudfront.DistributionOriginArgs(
                                               domain_name = www_bucket.bucket_regional_domain_name,
                                               origin_id= www_bucket.id
                                            )],
                                            default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
                                              allowed_methods= [
                                                "GET",
                                                "HEAD",
                                                ],
                                              cached_methods = [
                                                "GET",
                                                "HEAD"
                                                ],
                                              target_origin_id= www_bucket.id,
                                              viewer_protocol_policy= "redirect-to-https",
                                              forwarded_values= aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                                                query_string= False,
                                               cookies =  aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                                                 forward = "none"
                                               )
                                              )
                                            ),
                                            restrictions= aws.cloudfront.DistributionRestrictionsArgs(
                                              geo_restriction= aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                                                restriction_type= "whitelist",
                                                locations=[
                                                  "US",
                                                  "CA",
                                                  "GB",
                                                  "DE"
                                                ]
                                              )
                                            ),
                                            custom_error_responses= [aws.cloudfront.DistributionCustomErrorResponseArgs(
                                              error_code= 404,
                                              response_page_path="/error.html",
                                              response_code= 404
                                            )],
                                            viewer_certificate= aws.cloudfront.DistributionViewerCertificateArgs(
                                              acm_certificate_arn= www_cert.arn,
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": "Pulumi_resume",
                                              "evnironment": "www.richardcraddock.me"
                                            }
                                            )


record = aws.route53.Record(f"{dns}",
                        name = f"{dns}",
                        type = "A",
                        zone_id = zone.zone_id,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= Distribution.domain_name,
                                zone_id=Distribution.hosted_zone_id
                        )]
                        )
www_record = aws.route53.Record(f"www.{dns}",
                        name = f"www.{dns}",
                        type = "A",
                        zone_id = zone.zone_id,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= www_Distribution.domain_name,
                                zone_id=www_Distribution.hosted_zone_id
                        )]
                        )