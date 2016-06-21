# cundo-dynamic-dynamodb
configurations and scripts for Dynamic DynamoDB

##GitHub Repo
https://github.com/sebdah/dynamic-dynamodb

##Documentation
http://dynamic-dynamodb.readthedocs.org/en/latest/

##Deployment
Deploy by launching CloudFormation stack:
<ol>
<li>Login to https://<account_id>.signin.aws.amazon.com/console</li>
<li>Go to CloudFormation dashboard: https://console.aws.amazon.com/cloudformation/home?region=us-east-1</li>
<li>Click <Create Stack> button</li>
<li>Create stack using the dynamic-dynamodb.template file with the default parameters. This will launch an EC2 instance into the PROD VPC and use the dynamic-dynamodb.conf file from the S3 bucket: S3://<bucket>/dynamic-dynamodb/</li>
</ol>

When the instance launches, it will pull the conf file automatically and start the dynamic-dynamodb daemon.

##Troubleshooting steps:
<ol>
<li>ssh -i <key> ec2-user@<hostname></li>
<li>The configurations are in `/etc/dynamic-dynamodb/dynamic-dynamodb.conf`</li>
<li>Check the status of the daemon: service dynamic-dynamodb status</li>
<li>Start the service: service dynamic-dynamodb start</li>
</ol>
