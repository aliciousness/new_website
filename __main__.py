"""An AWS Python Pulumi program"""
import pulumi, json
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


#lambda function for pipeline
pipelineLambda = aws.lambda_.Function("Pulumifunction",
  code = pulumi.FileArchive("./lambda.zip"),
  role = lambdarole.arn,
  runtime = "python3.8",
  handler = "index.test"
)

#lambda permission
lambda_permission = aws.lambda_.Permission("lambdaPermission", 
    action="lambda:InvokeFunction",
    principal="s3.amazonaws.com",
    function= pipelineLambda)

new_website = aws.codebuild.Project("new_website",
  artifacts = aws.codebuild.ProjectArtifactsArgs(type = "CODEPIPELINE"),
  environment = aws.codebuild.ProjectEnvironmentArgs(
    image= "aws/codebuild/standard:4.0",
    type = "LINUX_GPU_CONTAINER",
    compute_type= "BUILD_GENERAL1_LARGE"
  ),
  service_role= codeBuild_role.arn,
  source= aws.codebuild.ProjectSourceArgs(
    type= "CODEPIPELINE",
    location = "aliciousness/new_website"
  ),
  build_timeout= 5,
  description= "This build was built with pulumi",
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
                    "ProjectName": new_website.name
                },
            )],
        ),
        aws.codepipeline.PipelineStageArgs(
            name="Invoke",
            actions=[aws.codepipeline.PipelineStageActionArgs(
                name="Invoke",
                category="Invoke",
                owner="AWS",
                provider="Lambda",
                input_artifacts=["build_output"],
                version="1",
                configuration= {
                  "FunctionName": "PulumiFunction"
                },
            )],
        ),
    ])


connectPolicy = aws.iam.RolePolicy("connectionPolicy",
  role = codepipeline_role.id,
  policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
                "Action": 
                     ["codestar-connections:UseConnection",
                      "codebuild:BatchGetBuilds",
                      "codebuild:StartBuild"],
                "Effect": "Allow",
                "Resource":"arn:aws:codestar-connections:us-east-1:037484876593:connection/fd390b15-f09d-41f7-8382-1a477b9f2455",
                
            }]
    }))

pulumi.export("connection arn", connection.arn)
pulumi.export("connection status", connection.connection_status)
pulumi.export("connection id", connection.id)
pulumi.export("lambda arn", pipelineLambda.arn)