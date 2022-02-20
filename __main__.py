"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

connection = aws.codestarconnections.Connection(
    "github_connection", 
    provider_type="GitHub")
codepipeline_bucket = aws.s3.Bucket("codepipelineBucket", acl = "private")
codepipeline_role = aws.iam.Role("codepipelineRole", assume_role_policy = """{
   "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
} 
}""")
s3kmskey = aws.kms.get_alias(name="alias/mykmskey")
codepipeline = aws.codepipeline.Pipeline("PulumiCodePipeline",
    role_arn=codepipeline_role.arn,
    artifact_store=aws.codepipeline.PipelineArtifactStoreArgs(
        location=codepipeline_bucket.bucket,
        type="S3",
        encryption_key=aws.codepipeline.PipelineArtifactStoreEncryptionKeyArgs(
            id=s3kmskey.arn,
            type="KMS",
        ),
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
                    "FullRepositoryId": "my-organization/example",
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
            name="Deploy",
            actions=[aws.codepipeline.PipelineStageActionArgs(
                name="Deploy",
                category="Deploy",
                owner="AWS",
                provider="CloudFormation",
                input_artifacts=["build_output"],
                version="1",
                configuration={
                    "ActionMode": "REPLACE_ON_FAILURE",
                    "Capabilities": "CAPABILITY_AUTO_EXPAND,CAPABILITY_IAM",
                    "OutputFileName": "CreateStackOutput.json",
                    "StackName": "MyStack",
                    "TemplatePath": "build_output::sam-templated.yaml",
                },
            )],
        ),
    ])



pulumi.export("arn", connection.arn)
pulumi.export("connection status", connection.connection_status)
pulumi.export("connection id", connection.id)