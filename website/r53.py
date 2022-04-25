import pulumi 
import pulumi_aws as aws
from website.cloudfront import * 
from website.zone import GetR53Zone
import website.cloudfront as cloudfront


def CreateRecord(dns):
    zone = GetR53Zone(dns)
    record = aws.route53.Record(f"{dns}",
                        name = f"{dns}",
                        type = "A",
                        zone_id = zone.zone_id,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= cloudfront.Distribution.domain_name,
                                zone_id=cloudfront.Distribution.hosted_zone_id
                        )]
                        )
    www_record = aws.route53.Record(f"www.{dns}",
                        name = f"www.{dns}",
                        type = "A",
                        zone_id = zone.zone_id,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= cloudfront.www_Distribution.domain_name,
                                zone_id=cloudfront.www_Distribution.hosted_zone_id
                        )]
                        )