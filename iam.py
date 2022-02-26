import pulumi
import pulumi_aws as aws 
import __main__

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
role_policy_attachment = aws.iam.RolePolicyAttachment("lambdaRoleAttachment",
    role=lambdarole.name, 
    policy_arn=aws.iam.ManagedPolicy.ADMINISTRATOR_ACCESS)

pipeline_attachment = aws.iam.RolePolicyAttachment(
    "pipelineRoleAttachment",
    role = codepipeline_role.name,
    policy_arn= aws.iam.ManagedPolicy.AWS_CODE_PIPELINE_FULL_ACCESS
)

