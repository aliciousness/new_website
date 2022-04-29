#Infrastructure

This is the infrastructure with AWS codepipeline, codebuild, lambda, and all dependencies to run a CI/CD platform for https://github.com/aliciousness/resume.

CERTS AND CONNECTION MUST BE VALIDATED IN THE CONSOLE BEFORE CREATING OTHER RESOURCES.
after certificates issued and connection available run -pulumi refresh- to refresh pulumi stack resources and output values. Then run -pulumi up- again.
