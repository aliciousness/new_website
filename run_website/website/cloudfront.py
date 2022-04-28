import pulumi 
import pulumi_aws as aws 




def CreateDistribution(dns,certs,bucket_regional_domain_name,bucket_id):
    

    Distribution = aws.cloudfront.Distribution(f'{dns}',
                                             enabled= True,
                                             is_ipv6_enabled=True,
                                             comment = f"{dns} built with Pulumi",
                                             default_root_object= "index.html",
                                             aliases=[f"{dns}"],
                                             wait_for_deployment= False,
                                             origins= [aws.cloudfront.DistributionOriginArgs(
                                               domain_name = bucket_regional_domain_name[0],
                                               origin_id= bucket_id[0]
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
                                              target_origin_id= bucket_id[0],
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
                                              acm_certificate_arn= certs[0],
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": dns,
                                              "environment": dns
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
                                               domain_name = bucket_regional_domain_name[1],
                                               origin_id= bucket_id[1]
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
                                              target_origin_id= bucket_id[1],
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
                                              acm_certificate_arn= certs[1],
                                              ssl_support_method='sni-only'
                                            ),
                                            tags= {
                                              "Name": "Pulumi_resume",
                                              "environment": f"www.{dns}"
                                            }
                                            )
    
    return {
      "Distribution":
        [Distribution.domain_name,Distribution.hosted_zone_id],
      "www_Distribution":
        [www_Distribution.domain_name,www_Distribution.hosted_zone_id]}
    