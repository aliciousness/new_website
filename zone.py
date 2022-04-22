import pulumi 
import pulumi_aws as aws 

#find aws hosted zone
def GetR53Zone(dns):
    zone = aws.route53.get_zone(
                               name = f"{dns}",
                               private_zone= False,
                               
                               )