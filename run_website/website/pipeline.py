import pulumi 
import pulumi_aws as aws 
from website.iam import *
import website.buckets



def CreatePipeline(dns,repository_id,connection_arn):
    
    
    
    
    #build project
    new_website = aws.codebuild.Project(f"build-project-{dns}",
                                        artifacts = aws.codebuild.ProjectArtifactsArgs(
                                            type = "CODEPIPELINE",
                                            location = buckets.codepipeline_artifact_store.arn.apply(lambda artifactS3 : f"{artifactS3}")
                                            ),
                                        environment = aws.codebuild.ProjectEnvironmentArgs(
                                            image= "aws/codebuild/standard:4.0",
                                            type = "LINUX_CONTAINER",compute_type= "BUILD_GENERAL1_SMALL",environment_variables= [aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                                                name= "S3_BUCKET",
                                                value= website.bucket._name, 
                                                type = "PLAINTEXT"
                                                )]
                                            ),
                                        service_role= codeBuild_role.arn,source= aws.codebuild.ProjectSourceArgs(
                                            type= "CODEPIPELINE",
                                            location = buckets.codepipeline_artifact_store.arn.apply(lambda artifactS3 : f"{artifactS3}"
                                                                                             )),
                                        build_timeout= 5,
                                        queued_timeout= 20,
                                        description= f"This build was built with pulumi for {dns}",
                                        tags={
                                            "Name": dns
                                        }
                                        )
    
    #pipeline
    
    codepipeline = aws.codepipeline.Pipeline(f"pipeline-{dns}",
    role_arn=codepipeline_role.arn,
    tags={
        "Name": dns
    },
    artifact_store=aws.codepipeline.PipelineArtifactStoreArgs(
        location=buckets.codepipeline_artifact_store.bucket,
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
                    "ConnectionArn": connection_arn,
                    "FullRepositoryId": f"{repository_id}",
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

