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
    ])



pulumi.export("Connect",{
    "connection_arn" : connection.arn,
    "connection_status": connection.connection_status,
    "connection_id": connection.id,
    "connection": connection.name})
pulumi.export("CodeBuild", {
    "arn": new_website.arn,
    "name": new_website.name
})
pulumi.export("connect_arn", connection.arn)
# pulumi.export("lambda arn", pipelineLambda.arn)
pulumi.export("codebuild",  {
    "arn": new_website.arn,
    "id": new_website.id
})