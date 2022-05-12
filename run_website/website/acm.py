import pulumi,json
import pulumi_aws as aws

#certs for cloudfront
#IMPORTANT 
# CERTS  AND CONNECTION MUST BE VALIDATED IN THE CONSOLE 



def CreateCerts(dns,provider_type="Github"):
  
    #connection for Github
    connection = aws.codestarconnections.Connection(
        f"{provider_type}_connection", 
        provider_type=f"{provider_type}",
        tags={
                             "Name": dns,
                             "Environment": "Pulumi"
                           })
    
    cert = aws.acm.Certificate(f"{dns}",
                           domain_name = f"{dns}",
                           tags={
                             "Name": dns,
                             "Environment": "Pulumi"
                           },
                           validation_method="DNS")

    www_cert = aws.acm.Certificate(f"www.{dns}",
                           domain_name = f"www.{dns}",
                           tags={
                             "Name": f"www.{dns}",
                             "Environment": "Pulumi"
                           },
                           validation_method="DNS")
    
    pulumi.export("connection_status", connection.connection_status)
    
    return {
      "connection": connection.arn,
      "certs":
        [cert.arn, www_cert.arn]
      }