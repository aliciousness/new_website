import pulumi 
import pulumi_aws as aws
from cloudfront import * 
from zone import GetR53Zone


def CreateRecord(dns):
    zone = GetR53Zone(dns)
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