"""An AWS Python Pulumi program"""
from ast import alias
import pulumi, json
import pulumi_aws as aws
from iam import *

#connection for Github
connection = aws.codestarconnections.Connection(
    "github_connection", 
    provider_type="GitHub")


#find aws hosted zone
zone = aws.route53.get_zone(
                               name = "richardcraddock.me",
                               private_zone= False,
                               
                               )

#certs for cloudfront
#validate certs in the console 
cert = aws.acm.Certificate("resume_cert",
                           domain_name = "richardcraddock.me",
                           tags={
                             "Environment": "richardcraddock.me"
                           },
                           validation_method="DNS")

cert = aws.acm.Certificate("www_resume_cert",
                           domain_name = "www.richardcraddock.me",
                           tags={
                             "Environment": "www.richardcraddock.me"
                           },
                           validation_method="DNS")

# need to change if buckets.py changes into a function NOTE
# cloudfront_dns = []
# for n in website_buckets:
  
#   Distribution = aws.cloudfront.Distribution('resume_pulumi',
#                                             origins= [aws.cloudfront.DistributionOriginArgs(
#                                               domain_name = n.bucket_regional_domain_name,
#                                               origin_id= 
#                                             )],
#                                             default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
#                                               allowed_methods= [""]
#                                             ))




#kms key
# s3kmskey = aws.kms.Key("key",
#                        deletion_window_in_days=10,
#                        description= "key1")
# kmsalias = aws.kms.Alias("alias", target_key_id=s3kmskey.key_id)

#lambda function for pipeline
# pipelineLambda = aws.lambda_.Function("Pulumifunction",
#   code = pulumi.FileArchive("./lambda.zip"),
#   role = lambdarole.arn,
#   runtime = "python3.8",
#   handler = "index.handler",
#   timeout= 30
# #   environment = 
# )


# lambda_permission = aws.lambda_.Permission("lambdaPermission", 
#     action="lambda:*",
#     principal="s3.amazonaws.com",
#     function= pipelineLambda)

#codebuild project
new_website = aws.codebuild.Project("new_website",
  artifacts = aws.codebuild.ProjectArtifactsArgs(
      type = "CODEPIPELINE",
      location = codepipeline_artifact_store.arn.apply(lambda artifactS3 : f"{artifactS3}")
      ),
  environment = aws.codebuild.ProjectEnvironmentArgs(
    image= "aws/codebuild/standard:4.0",
    type = "LINUX_CONTAINER",
    compute_type= "BUILD_GENERAL1_SMALL",
    environment_variables= [aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
        name= "S3_BUCKET",
        value= bucket._name, 
        type = "PLAINTEXT"
    )]
  ),
  service_role= codeBuild_role.arn,
  source= aws.codebuild.ProjectSourceArgs(
    type= "CODEPIPELINE",
    location = codepipeline_artifact_store.arn.apply(lambda artifactS3 : f"{artifactS3}"
  )),
  build_timeout= 5,
  queued_timeout= 20,
  description= "This build was built with pulumi",
  )


codepipeline = aws.codepipeline.Pipeline("Pulumi",
    role_arn=codepipeline_role.arn,
    artifact_store=aws.codepipeline.PipelineArtifactStoreArgs(
        location=codepipeline_artifact_store.bucket,
        type="S3",
    ),
    stages=[
        aws.codepipeline.PipelineStageArgs(
            name="Source",
            actions=[aws.codepipeline.PipelineStageActionArgs(
                name="Source",
                category="Source",
                owner="AWS",
                provider="CodeStarSourceConnection",
                version="1",
                output_artifacts=["source_output"],
                configuration={
                    "ConnectionArn": connection.arn,
                    "FullRepositoryId": "aliciousness/resume",
                    "BranchName": "main",
                    
                },
            )],
        ),
        aws.codepipeline.PipelineStageArgs(
            name="Build",
            actions=[aws.codepipeline.PipelineStageActionArgs(
                name="Build",
                category="Build",
                owner="AWS",
                provider="CodeBuild",
                input_artifacts=["source_output"],
                output_artifacts=["build_output"],
                version="1",
                configuration={
                    "ProjectName": new_website.name.apply(lambda project_name : f"{project_name}")
                },
            )],
        ),
        # aws.codepipeline.PipelineStageArgs(
        #     name="Invoke",
        #     actions=[aws.codepipeline.PipelineStageActionArgs(
        #         name="Invoke",
        #         category="Invoke",
        #         owner="AWS",
        #         provider="Lambda",
        #         input_artifacts=["build_output"],
        #         version="1",
        #         configuration= {
        #           "FunctionName": pipelineLambda.name.apply(lambda function_name : f"{function_name}")
        #         },
        #     )],
        # ),
    ])



pulumi.export("Connect",{
    "connection arn" : connection.arn,
    "connection status": connection.connection_status,
    "connection id": connection.id,
    "connection": connection.name})
pulumi.export("CodeBuild", {
    "arn": new_website.arn,
    "name": new_website.name
})
pulumi.export("connect arn", connection.arn)
# pulumi.export("lambda arn", pipelineLambda.arn)
pulumi.export("codebuild",  {
    "arn": new_website.arn,
    "id": new_website.id
})