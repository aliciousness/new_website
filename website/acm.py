import pulumi 
import pulumi_aws as aws

#certs for cloudfront
#IMPORTANT 
# CERTS MUCTS BE VALIDATED IN THE CONSOLE 

def CreateCerts(dns):
    cert = aws.acm.Certificate(f"{dns}",
                           domain_name = f"dns",
                           tags={
                             "Name": dns,
                             "Environment": dns
                           },
                           validation_method="DNS")

    www_cert = aws.acm.Certificate(f"www.{dns}",
                           domain_name = f"www.{dns}",
                           tags={
                             "Name": f"www.{dns}",
                             "Environment": f"www.{dns}"
                           },
                           validation_method="DNS")
    return [cert.arn,www_cert.arn]