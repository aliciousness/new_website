import json
import pulumi_aws as aws
from pulumi import get_stack, StackReference, get_project
from run_website.website import Acm, Pipeline, Zone, s3, r53,cloudfront


class Website():
    def __init__(self,dns,repository_id,provider_type="GitHub"):
        self.dns = dns
        #DNS registered 
        self.repository_id = repository_id
        #IE. GitHub - aliciousness/resume
        self.provider_type = provider_type
        # repository provider IE
        
        self.acm = Acm.CreateCerts(
            dns = self.dns,
            provider_type = self.provider_type
        )
        self.zone =Zone.GetZone(dns=self.dns)
    
        
    def run_website(self):
        buckets =s3.CreateBuckets(dns=self.dns)
        
        pipeline=Pipeline.CreatePipeline(
            dns=self.dns,
            repository_id=self.repository_id,
            connection_arn = self.acm["connection"],
            artifact_bucket= buckets['artifact_bucket'][1],
            artifact_bucket_arn=buckets['artifact_bucket'][0],
            main_bucket_name=buckets['bucket_name'])
        
        distribution=cloudfront.CreateDistribution(
            dns=self.dns,
            certs = self.acm["certs"],
            bucket_regional_domain_name= buckets['bucket_id'],
            bucket_id= buckets['bucket_regional_domain_name'])
        
        record = r53.CreateRecord(
            dns=self.dns,
            distribution = distribution["Distribution"],
            www_distribution = distribution["www_Distribution"],
            zone_id= self.zone)
    
    #checks validation for connect for pipeline 
    def check_validation(self,company):
        project = get_project()
        stack = get_stack()
        output = StackReference(f"{company}/{project}/{stack}").get_output('Connect') #needs to be changed to "connection_status" BUG

        #if connection status is available then it runs the rest of the products 
        if output['connection_status'] == "aVAILABLE":
            #needs to take out key BUG
            self.run_website()
        else:
            print("please validate the proper resources. to continue forward or wait until connection status is available, this may take some time ")
        
        