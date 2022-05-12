Infrastructure

This is the infrastructure with AWS codepipeline, codebuild, lambda, and all dependencies to run a CI/CD platform for my [resume](https://github.com/aliciousness/resume).

Prerequisites:
-Registered DNS Hosted in Route53 with qualifying NS and SOA records

When implementing DNS name to the init function, make sure that the DNS name is EXACTLY the same as the hosted zone in Route53. Any input errors of DNS name will causing following errors with finding DNS and serving certs.

CERTS AND CONNECTION MUST BE VALIDATED IN THE CONSOLE BEFORE CREATING ANY OTHER RESOURCES IN [AWS](https://aws.amazon.com/). \*

after certificates issued and connection available run -pulumi refresh- to refresh pulumi stack resources and output values. Then run -pulumi up- again.
