import time
import json
import boto3
import os
from datetime import datetime
from botocore.client import Config
from botocore.errorfactory import ClientError

ses_client = boto3.client('ses')
s3_client = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
dynamodb_client = boto3.client('dynamodb')

error_response = {
    "statusCode": 500,
    "headers": {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Credentials': True,
    },
    "body": "An error occurred. Please contact the Administrator."
}

def send_email(preSignedURL, senderEmailAddress, requesterEmailAddress, fileName,requesterName):

    send_email_response = ses_client.send_email(
        Destination={
            'BccAddresses': [
                senderEmailAddress,
            ],
            'CcAddresses': [
            ],
            'ToAddresses': [
                requesterEmailAddress,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': 'Hello '+requesterName+'!<br><br> Thanks for your interest in our Whitepaper '+fileName+'!<br><br>Please click <a class="ulink" href="'+preSignedURL+'" target="_blank">here</a> to download the whitepaper in the next 24 hours.<br><br>If you have any questions, feel free to contact us.<br><br>Kind regards<br>'+senderEmailAddress,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Whitepaper Download - '+fileName,
            },
        },
        ReplyToAddresses=[
            senderEmailAddress
        ],
        ReturnPath=senderEmailAddress,
        Source=senderEmailAddress
    )

    print('Message send with ID '+send_email_response['MessageId'])

def storeDynamoDB(requesterEmailAddress, fileName,requesterName,dynamoDbTable):
    timestamp = datetime.utcnow().strftime("%s")
    put_item_response = dynamodb_client.put_item(
        Item={
            'timestamp': {
                'S': str(timestamp),
            },
            'requesterEmailAddress': {
                'S': requesterEmailAddress,
            },
            'fileName': {
                'S': fileName,
            },
            'requesterName': {
                'S': requesterName,
            },
        },
        ReturnConsumedCapacity='TOTAL',
        TableName=dynamoDbTable,
    )
    print('Data is stored in DynamoDB')

def checkIfFileExists(s3BucketName,fileName):
    try:
        head_object_response = s3_client.head_object(Bucket=s3BucketName, Key=fileName)
        return True
    except ClientError:
        return False
    return False

def generate_presigned_url(s3BucketName,fileName,urlExpirationTimeInMS):
    generate_presigned_url_response = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': s3BucketName,
            'Key': fileName
        },
        ExpiresIn=urlExpirationTimeInMS
    )
    print('PreSigned url is generated ' + generate_presigned_url_response)
    return generate_presigned_url_response

def whitepaperhandler(event, context):
    try:
        requesterEmailAddress = event['multiValueQueryStringParameters']['email'][0]
        fileName = event['multiValueQueryStringParameters']['fileName'][0]
        requesterName = event['multiValueQueryStringParameters']['name'][0]
    except:
        print("ERROR: The parameter name, email or filename was not provided. Provided parameters: " + str(event['multiValueQueryStringParameters']))
        return error_response
    print('Request data is the following: ' + requesterEmailAddress + ', ' + requesterName + ', ' + fileName)

    try:
        s3BucketName = os.environ['s3BucketName']
        senderEmailAddress = os.environ['senderEmailAddress']
        urlExpirationTimeInMS = os.environ['UrlExpirationTimeInMS']
        cloudwatchTopic = os.environ['cloudwatchTopic']
        dynamoDbTable = os.environ['dynamoDbTable']
    except:
        print('ERROR: One of the environmet variable s3BucketName, senderEmailAddress, UrlExpirationTimeInMS, cloudwatchTopic or dynamoDbTable is missing')
        return error_response

    try:
        storeDynamoDB(requesterEmailAddress, fileName,requesterName,dynamoDbTable)
    except:
        print('ERROR: Could not store in DynamoDB')
        return error_response
    if not checkIfFileExists(s3BucketName,fileName):
        print('ERROR: '+fileName+' does not exists in S3 bucket')
        return error_response
    try:
        presigned_url = generate_presigned_url(s3BucketName,fileName,urlExpirationTimeInMS)
    except:
        print('ERROR: Could not generate pre signed url')
        return error_response
    try:
        send_email(presigned_url,senderEmailAddress,requesterEmailAddress, fileName,requesterName)
    except:
        print('ERROR: Could not send email')
        return error_response

    response = {
        "statusCode": 200,
        "headers": {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Credentials': True,
        },
        "body": "Please see your mailbox for a message with the download link."
    }
    print('Success response will be send')
    return response
