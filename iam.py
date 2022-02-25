import pulumi
import pulumi_aws as aws 
from __main__ import *

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
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
} 
}""")
role_policy_attachment = aws.iam.RolePolicyAttachment("lambdaRoleAttachment",
    role=lambdarole.name, 
    policy_arn=aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE)

codepipeline_policy = aws.iam.RolePolicy("codepipelinePolicy",
    role=codepipeline_role.id,
    policy=pulumi.Output.all(codepipeline_bucketzip.arn, connection.arn).apply(lambda codepipelineBucketArn, codepipelineBucketArn1, connectionArn: f"""{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "{codepipeline_bucket_arn}",
        "{codepipeline_bucket_arn1}/*"
      ]
    }},
    {{
      "Effect": "Allow",
      "Action": [
        "codestar-connections:UseConnection"
      ],
      "Resource": "{connection_arn}"
    }},
    {{
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    }}
  ]
}}
"""))