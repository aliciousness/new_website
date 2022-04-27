import pulumi 
import pulumi_aws as aws
from website.cloudfront import * 
from website.zone import GetR53Zone



def CreateRecord(dns,distribution,www_distribution,zone_id):
    zone = GetR53Zone(dns)
    record = aws.route53.Record(f"{dns}",
                        name = f"{dns}",
                        type = "A",
                        zone_id = zone,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= distribution[0],
                                zone_id=distribution[1]
                        )]
                        )
    www_record = aws.route53.Record(f"www.{dns}",
                        name = f"www.{dns}",
                        type = "A",
                        zone_id = zone,
                        aliases= [
                            aws.route53.RecordAliasArgs(
                                evaluate_target_health= False,
                                name= www_distribution[0],
                                zone_id=www_distribution[1]
                        )]
                        )