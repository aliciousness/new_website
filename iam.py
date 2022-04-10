import pulumi, json
import pulumi_aws as aws 


#artifactbucket
codepipeline_artifact_store = aws.s3.Bucket("codepipelineBucketArtifactStore",)

#bucket for the build to zip all the files
codepipeline_zipped = aws.s3.Bucket("codepipelinebucketzipped",
                                    bucket = "codepipelinebucketzipped",
                                    # opts = pulumi.ResourceOptions(delete_before_replace = True)
)

#bucket for lambda to put unzipped artifacts 
lambda_bucket = aws.s3.Bucket("codepipelinebucketunzipped",
                              bucket = "richardcraddock.com")

# role for lambda 
lambdarole = aws.iam.Role("roleForLambda", assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
""")

#role for pipeline 
codepipeline_role = aws.iam.Role("codepipelineRole", assume_role_policy = """{
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

codeBuild_role = aws.iam.Role("codebuildRolePulumi", assume_role_policy="""{
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
lambda_policy = aws.iam.Policy('LambdaPolicyWebsite',
                               policy= codepipeline_zipped.arn.apply(lambda zippeds3 : f'''{{
    "Version": "2012-10-17",
      "Statement": [
        {{
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "{zippeds3+"/*",
                zippeds3,"arn:aws:s3:::codepipelinebucketzipped"}" 
    ]
        }},
        {{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }}
    ]
}}'''))
codebuild_policy = aws.iam.Policy("NewWebsiteCodebuild",
                                  policy= codepipeline_artifact_store.arn.apply(lambda artifactS3 : f'''{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Resource": [
                "arn:aws:logs:us-east-2:037484876593:log-group:/aws/codebuild/new_website-8a91cb9",
                "arn:aws:logs:us-east-2:037484876593:log-group:/aws/codebuild/new_website-8a91cb9:*"
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
                "s3:PutObject",
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
                "lambda:*"
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

role_policy_attachment = aws.iam.RolePolicyAttachment("lambdaRoleAttachment",
    role=lambdarole.name, 
    policy_arn=lambda_policy.arn)


codeBuild_attachment = aws.iam.RolePolicyAttachment(
  "codebuildAttachment2",
  role=codeBuild_role.name,
  policy_arn= aws.iam.ManagedPolicy.ADMINISTRATOR_ACCESS
)
 
codePipeline_attachment = aws.iam.RolePolicyAttachment(
  "codePipelineAttachment",
  role=codepipeline_role.name,
  policy_arn= aws.iam.ManagedPolicy.AWS_CODE_PIPELINE_FULL_ACCESS
)

pulumi.export("IAM",{
  "codebuild role arn": codeBuild_role.arn,
  "codepipeline role arn": codepipeline_role.arn,
  "lambda role": lambdarole.arn
})