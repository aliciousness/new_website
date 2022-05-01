import pulumi, json
import pulumi_aws as aws 





def CreatePipeline(dns,repository_id,connection_arn,artifact_bucket_arn,artifact_bucket,main_bucket_name):
    
    name = dns.split('.')
    if len(name) > 3 or len(name) == 3:
        domain = name[1]
    else:
        domain = name[0]
    
    #build project
    new_website = aws.codebuild.Project(f"build-project-{domain}",
                                        artifacts = aws.codebuild.ProjectArtifactsArgs(
                                            type = "CODEPIPELINE",
                                            location = artifact_bucket_arn.apply(lambda artifactS3 : f"{artifactS3}")
                                            ),
                                        environment = aws.codebuild.ProjectEnvironmentArgs(
                                            image= "aws/codebuild/standard:4.0",
                                            type = "LINUX_CONTAINER",compute_type= "BUILD_GENERAL1_SMALL",environment_variables= [aws.codebuild.ProjectEnvironmentEnvironmentVariableArgs(
                                                name= "S3_BUCKET",
                                                value= main_bucket_name, 
                                                type = "PLAINTEXT"
                                                )]
                                            ),
                                        service_role= codeBuild_role.arn,source= aws.codebuild.ProjectSourceArgs(
                                            type= "CODEPIPELINE",
                                            location = artifact_bucket_arn.apply(lambda artifactS3 : f"{artifactS3}"
                                                                                             )),
                                        build_timeout= 5,
                                        queued_timeout= 20,
                                        description= f"This build was built with pulumi for {dns}",
                                        tags={
                                            "Name": dns,
                                            "Environment": "Pulumi"
                                        }
                                        )
    
    #pipeline
    
    codepipeline = aws.codepipeline.Pipeline(f"pipeline-{dns}",
    role_arn=codepipeline_role.arn,
    tags={
        "Name": dns,
        "Environment": "Pulumi"
    },
    artifact_stores=[aws.codepipeline.PipelineArtifactStoreArgs(
        location=artifact_bucket,
        type="S3",
    )],
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
    
    #codebuild policy
    codebuild_policy = aws.iam.Policy("NewWebsiteCodebuild",
                                  tags= {
                                      "Environment": "Pulumi"
                                  },
                                  policy= artifact_bucket_arn.apply(lambda artifactS3 : f'''{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Resource": [
                "arn:aws:logs:us-east-2:037484876593:log-group:/aws/codebuild/new_website-*",
                "arn:aws:logs:us-east-2:037484876593:log-group:/aws/codebuild/new_website-*:*"
            ],
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        }},
        {{
            "Effect": "Allow",
            "Resource": [
                "{artifactS3}"
            ],
            "Action": [
                "s3:*",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetBucketAcl",
                "s3:GetBucketLocation"
            ]
        }},
        {{
            "Effect": "Allow",
            "Resource": [
                "*"
            ],
            "Action": [
                "lambda:InvokeFunction",
                "lambda:ListFunctions"
            ]
        }},
        {{
            "Effect": "Allow",
            "Action": [
                "codebuild:CreateReportGroup",
                "codebuild:CreateReport",
                "codebuild:UpdateReport",
                "codebuild:BatchPutTestCases",
                "codebuild:BatchPutCodeCoverages",
                "codebuild:BatchGetBuilds",
                "codebuild:StartBuild"
            ],
            "Resource": [
                "arn:aws:codebuild:us-east-2:037484876593:report-group/new_website-*"
            ]
        }}
    ]
}}'''))
    
    #connection policy
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
    
    
    #code build attachment
    codeBuild_attachment = aws.iam.RolePolicyAttachment(
  "codebuildAttachment2",
  role=codeBuild_role.name,
  policy_arn= aws.iam.ManagedPolicy.ADMINISTRATOR_ACCESS
)
    
    #codepipeline attachment
    codePipeline_attachment = aws.iam.RolePolicyAttachment(
  "codePipelineAttachment",
  role=codepipeline_role.name,
  policy_arn= aws.iam.ManagedPolicy.AWS_CODE_PIPELINE_FULL_ACCESS
)
    pulumi.export("IAM",{
  "codebuild role arn": codeBuild_role.arn,
  "codepipeline role arn": codepipeline_role.arn
})
    


codeBuild_role = aws.iam.Role("codebuildRolePulumi",
                              tags= {"Environment":"Pulumi"},
                              assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
""")

#role for pipeline 
codepipeline_role = aws.iam.Role("codepipelineRole",
                                 tags= {"Environment": "Pulumi"},
                                 assume_role_policy = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}""")