import pulumi, json
import pulumi_aws as aws
from run_website.website.acm import CreateCerts
from run_website.website.buckets import CreateBuckets
from run_website.website.cloudfront import CreateDistribution
from run_website.website.pipeline import CreatePipeline
from run_website.website.r53 import CreateRecord
from run_website.website.zone import GetZone


class Website():
    def __init__(self,dns,repository_id,provider_type="GitHub"):
        self.dns = dns
        #DNS registered 
        self.repository_id = repository_id
        #IE. GitHub - aliciousness/resume
        self.provider_type = provider_type
        # repository provider IE
        
        self.acm = CreateCerts(
            dns = self.dns,
            provider_type = self.provider_type
        )
        self.zone =GetZone(dns=self.dns)
        
    def run_website(self):
        buckets =CreateBuckets(dns=self.dns)
        
        pipeline=CreatePipeline(
            dns=self.dns,
            repository_id=self.repository_id,
            connection_arn = self.acm["connection"],
            artifact_bucket= buckets['artifact_bucket'][1],
            artifact_bucket_arn=buckets['artifact_bucket'][0],
            main_bucket_name=buckets['bucket_name'])
        
        distribution=CreateDistribution(
            dns=self.dns,
            certs = self.acm["certs"],
            bucket_regional_domain_name= buckets['bucket_id'],
            bucket_id= buckets['bucket_regional_domain_name'])
        
        record = CreateRecord(
            dns=self.dns,
            distribution = distribution["Distribution"],
            www_distribution = distribution["www_Distribution"],
            zone_id= self.zone)
        
        