import pulumi, json
import pulumi_aws as aws
import website


class Website():
    def __init__(self,dns,repository_id,provider_type="GitHub"):
        self.dns = dns
        #DNS registered 
        self.repository_id = repository_id
        #IE. GitHub - aliciousness/resume
        self.provider_type = provider_type
        # repository provider IE
        
        self.acm = website.acm(
            dns = self.dns,
            provider_type = self.provider_type
        )
        self.zone = website.GetR53Zone(dns=self.dns)
        
    def run_website(self):
        buckets =website.CreateBuckets(dns=self.dns)
        
        pipeline=website.CreatePipeline(
            dns=self.dns,
            repository_id=self.repository_id,
            connection_arn = self.acm["connection"])
        
        distribution=website.CreateDistribution(
            dns=self.dns,
            certs = self.acm["certs"])
        
        record = website.CreateRecord(
            dns=self.dns,
            distribution = distribution["distribution"],
            www_distribution = distribution["www_distribution"],
            zone_id= self.zone)
        