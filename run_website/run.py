import pulumi, json
import pulumi_aws as aws

from run_website.website import Pipeline, Zone, s3, r53,cloudfront,acm


class Website():
    def __init__(self,dns,repository_id,provider_type="GitHub"):
        self.dns = dns
        #DNS registered 
        self.repository_id = repository_id
        #IE. GitHub - aliciousness/resume
        self.provider_type = provider_type
        # repository provider IE
        
        self.acm = acm.CreateCerts(
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
        
        