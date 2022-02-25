"""An AWS Python Pulumi program"""

from cgitb import handler
from operator import index
import pulumi
import pulumi_aws as aws
from iam import *

#connection for Github
connection = aws.codestarconnections.Connection(
    "github_connection", 
    provider_type="GitHub")
#bucket for the build to zip all the files
codepipeline_bucketzip = aws.s3.Bucket("codepipelineBucketZipped")

#bucket for lambda to put unzipped artifacts 
lambda_bucket = aws.s3.Bucket("codepipelinePulumi")
#lambda role

#lambda function for pipeline
pipelineLambda = aws.lambda_.function("Pulumifunction",
  code = pulumi.FileArchive("./lambda.zip"),
  role = lambdarole.arn,
  runtime = "python3.8",
  handler = "lambda.handler",
  )

# s3kmskey = aws.kms.get_alias(name="alias/mykmskey")
#encryption key
codepipeline = aws.codepipeline.Pipeline("PulumiCodePipeline",
    role_arn=codepipeline_role.arn,
    artifact_store=aws.codepipeline.PipelineArtifactStoreArgs(
        location=codepipeline_bucketzip.bucket,
        type="S3",
        #take the key out for now and see if i can do without the encryption for now 
        # encryption_key=aws.codepipeline.PipelineArtifactStoreEncryptionKeyArgs(
        #     id=s3kmskey.arn,
        #     type="KMS",
        # ),
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
                    "FullRepositoryId": "aliciousness/new_website",
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
                    "ProjectName": "test",
                },
            )],
        ),
        aws.codepipeline.PipelineStageArgs(
            name="Invoke",
            actions=[aws.codepipeline.PipelineStageActionArgs(
                name="Invoke",
                category="Invoke",
                owner="AWS",
                provider="Lamba",
                input_artifacts=["build_output"],
                version="1",
                configuration={
                  "FunctionName": "PulumiFunction"
                    
                },
            )],
        ),
    ])



pulumi.export("arn", connection.arn)
pulumi.export("connection status", connection.connection_status)
pulumi.export("connection id", connection.id)