import pulumi 
import pulumi_aws as aws 

#find aws hosted zone
def GetZone(dns):
    zone = aws.route53.get_zone(
                               name = f"{dns}",
                               private_zone= False,
                               
                               )
    return zone.zone_id