Whitepaper Handler
----

Do you have a website based on a framework which is not capable to provide a whitepaper functionality or just look for a solution which handles whitepaper? This could be a way to solve your problem.

:exclamation: This solution will create several resources which will be billed by AWS.

## Base architecture

![alt text](/images/whitepaperhandler_architecture.png "Whitepaper Handler architecture")

All whitepapers are stored in a private AWS Simple Storage Service (S3) bucket. A Javascript form can be embedded in every website. This form must contain three parameters - email, name and whitepaper name. This form calls the AWS API gateway and a lambda function behind it stores the data in the DynamoDB and generates a preSigned S3 url on the whitepaper which is stored in an S3 bucket. An email is generated with the S3 preSigned url and send via Simple Email Service (SES) to the website user.

Roundtrip time from "form send" to "email is sent" is around 200ms if the function is warm. Consumed memory is under 50MB.

### Used AWS Services

* AWS Simple E-mail Service (SES)
* AWS Simple Storage Service (S3)
* AWS Lambda
* AWS DynamoDB
* AWS X-AWS
* AWS Cloudwatch

## Implementation guide

Please follow all the steps below to deploy the solution. Please pay attention that the solution only can be deployed in a region where all mentioned services above are available. (possible is for example eu-west-1 - but not eu-central-1)

### Requirements

* Java 8 (tested with version 1.8.0_181)
* Gradle (tested with version 4.10.2)
* Node.js (tested with version 8.12.0)
* Serverless (tested with version 1.36.0)
* Serverless Plugins
  * AWS Pseudo Parameters (install via ```npm install serverless-pseudo-parameters```)
  * serverless plugin tracing (install via ```npm install serverless-plugin-tracing```)
  * serverless-api-gateway-xray plugin (install via ```npm install serverless-api-gateway-xray```)

### SES configuration

As mentioned above the solution uses AWS Simple Email Service (SES) to send an email with a download link to the users. There are some manual configuration steps necessary which cannot be coded with IaaC.

#### Verify Email domain
In the screenshot you can see how your domain should look like before you can proceed to the next steps:

![alt text](/images/SES_domain_verified.png "AWS SES domain verification")

The domain must be verified in the AWS region where the solution will be deployed. For help see the official documentation in the [Amazon Developer Guide SES](https://docs.aws.amazon.com/de_de/ses/latest/DeveloperGuide/verify-domains.html "Amazon Developer Guide SES").

#### Request SES Limit increase

By default, AWS SES limits the possible recipients to manually verified email addresses. To be moved out of this "sandbox", you have to request a sending limit increase. Otherwise, you are not able to send emails to your users.

![alt text](/images/SES_limit_increase.png "AWS SES limit increase")


### Download the solution

1. Clone this repository

### Deploy AWS resources

1. Switch to folder "AWS_resources"
2. Edit the parameters in the serverless.yml
  * senderEmailAddress: The sender email address for emails to the Whitepaper requester
  * s3BucketName: The AWS S3 bucket where the Whitepapers are stored
3. run ```sls deploy``` to deploy the solution
4. Note the values for "WhitepaperHandlerKey" and "endpoints" from the console output

### Upload Whitepapers to S3

1. Log into the AWS Console and switch to the service S3.
2. Look for the S3 bucket with the name you defined under "s3BucketName" before
3. Upload your Whitepaper to this S3 bucket over the AWS Console

### Deploy Website example

The website example is just a example. It can be deployed in an [AWS S3 website bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html "AWS S3 website bucket")

1. Switch to the folder "Website_example"
2. Edit the file "main.js"
  * Edit the variable url with the correct API gateway endpoint
  * Edit the variable xapiKey with the correct API key
  * Edit the variable fileName with the file name of the file you stored in the S3 bucket (s3BucketName)
3. Upload the index.html and main.js to the S3 bucket created to hosting the website (not the S3 bucket for storing the whitepaper!)

### Undeploy the solution

Before the solution can be removed with the serverless framework, some things must be done by hand:

* The S3 bucket must be empty before it can be deleted

Just follow the next steps to undeploy the solution:

1. Switch to folder "AWS_resources"
2. run ```sls remove``` to remove the solution

## ToDo list

### Code

There are surely ways to improve. Just send a pull request. :wink:

### Functionality / Architecture

Priority from high to low:

* LogGroup expiration for Lambda
* Encryption at rest for S3 and DynamoDB with KMS
* Administrator Website (upload Whitepapers to S3, see data (name, email) of Whitepaper requester)
