import pulumi 
import pulumi_aws as aws 
from buckets import *
from acm import CreateCerts 


def CreateDistribution(dns):
    cert = CreateCerts(dns)

    Distribution = aws.cloudfront.Distribution(f'{dns}',
                                             enabled= True,
                                             is_ipv6_enabled=True,
                                             comment = f"{dns} built with Pulumi",
                                             default_root_object= "index.html",
                                             aliases=[f"{dns}"],
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
                                              acm_certificate_arn= cert[0],
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": dns,
                                              "evnironment": dns
                                            }
                                            )

  
    www_Distribution = aws.cloudfront.Distribution(f'www.{dns}',
                                             enabled= True,
                                             is_ipv6_enabled=True,
                                             comment = f"www.{dns} built with Pulumi",
                                             default_root_object= "index.html",
                                             aliases=[f"www.{dns}"],
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
                                              acm_certificate_arn= cert[1],
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": "Pulumi_resume",
                                              "evnironment": "www.richardcraddock.me"
                                            }
                                            )
    