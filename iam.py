import pulumi, json
import pulumi_aws as aws 


# role for lambda 
lambdarole = aws.iam.Role("iamForLambda", assume_role_policy="""{
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

codeBuild_role = aws.iam.Role("exampleRole", assume_role_policy="""{
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
role_policy_attachment = aws.iam.RolePolicyAttachment("lambdaRoleAttachment",
    role=lambdarole.name, 
    policy_arn=aws.iam.ManagedPolicy.LAMBDA_FULL_ACCESS)

pipeline_attachment = aws.iam.RolePolicyAttachment(
    "pipelineRoleAttachment",
    role = codepipeline_role.name,
    policy_arn= aws.iam.ManagedPolicy.AWS_CODE_PIPELINE_FULL_ACCESS
)
codeBuild_attachment = aws.iam.RolePolicyAttachment(
  "codebuildAttachment",
  role=codeBuild_role.name,
  policy_arn= aws.iam.ManagedPolicy.AWS_CODE_BUILD_DEVELOPER_ACCESS 
)

# connectPolicy = aws.iam.RolePolicy("CodeStarConnectionPolicy",
#   role = codepipeline_role.id,
#   policy = aws.iam.ManagedPolicy.AWS_CODE_STAR_FULL_ACCESS)
