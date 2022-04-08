"""An AWS Python Pulumi program"""
import pulumi, json
import pulumi_aws as aws
from iam import *

#connection for Github
connection = aws.codestarconnections.Connection(
    "github_connection", 
    provider_type="GitHub")
#bucket for the build to zip all the files, also have to go to the console to get bucket full name for buildspec bucket location 
codepipeline_zipped = aws.s3.Bucket("codepipelinebucketzipped")


#bucket for lambda to put unzipped artifacts 
lambda_bucket = aws.s3.Bucket("codepipelinePulumi",)

#kms key
s3kmskey = aws.kms.Key("key",
                       deletion_window_in_days=10,
                       description= "key1")
kmsalias = aws.kms.Alias("alias", target_key_id=s3kmskey.key_id)

#lambda function for pipeline
pipelineLambda = aws.lambda_.Function("Pulumifunction",
  code = pulumi.FileArchive("./lambda.zip"),
  role = lambdarole.arn,
  runtime = "python3.8",
  handler = "index.test"
)

#lambda permission
lambda_permission = aws.lambda_.Permission("lambdaPermission", 
    action="lambda:*",
    principal="s3.amazonaws.com",
    function= pipelineLambda)

#codebuild project
new_website = aws.codebuild.Project("new_website",
  artifacts = aws.codebuild.ProjectArtifactsArgs(
      type = "CODEPIPELINE",
      location = codepipeline_artifact_store.arn.apply(lambda artifactS3 : f"{artifactS3}")
      ),
  environment = aws.codebuild.ProjectEnvironmentArgs(
    image= "aws/codebuild/standard/3.0",
    type = "LINUX_GPU_CONTAINER",
    compute_type= "BUILD_GENERAL1_LARGE",
    environment_variables= aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
        name= "S3_BUCKET",
        value= codepipeline_zipped.arn.apply(lambda s3 : f"{s3}"),
        type = "S3"
    )
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
        # encryption_key = aws.codepipeline.PipelineArtifactStoreEncryptionKeyArgs(
        #     id =kmsalias.arn,
        #     tpye = "KMS"
        # )
        
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
                    "ProjectName": new_website.name.apply(lambda project_name : f"{project_name}")
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
                  "FunctionName": pipelineLambda.name.apply(lambda function_name : f"{function_name}")
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
                     ["Iam:PassRole",
                      "codestar-connections:*",
                      "codebuild:BatchGetBuilds",
                      "codebuild:StartBuild"],
                "Effect": "Allow",
                "Resource":"*",
                
            }]
    }))

pulumi.export("Connect",{
    # "connection arn" : connection.arn,
    "connection status": connection.connection_status,
    "connection id": connection.id,
    "connection": connection.name})
pulumi.export("connect arn", connection.arn)
pulumi.export("lambda arn", pipelineLambda.arn)
pulumi.export("codebuild",  {
    "arn": new_website.arn,
    "id": new_website.id
})