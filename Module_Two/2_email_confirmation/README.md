# Section 2: Creating the Email Confirmation System

In this section, we'll implement an automated email confirmation system for the RSVP application using AWS Lambda and Simple Email Service (SES). When a user registers for an event, they will receive a confirmation email.

## Objectives

- Set up AWS SES for sending transactional emails
- Create a Lambda function that sends confirmation emails
- Configure necessary IAM permissions
- Connect the Lambda function to the booking flow using DynamoDB Streams

## Prerequisites

- AWS account with permissions for Lambda, SES, and IAM
- AWS CLI configured locally
- Basic knowledge of serverless architecture
- Completed Section 1 of Module Two

## Steps

### 1. Set Up Amazon SES

First, we need to set up Amazon SES and verify email domains or addresses:

1. Open the AWS Management Console and navigate to SES
2. Verify the email domain you'll use to send emails:
   - Go to "Verified identities" → "Create identity"
   - Choose "Domain" and enter your domain
   - Follow the DNS verification steps
3. If you're in a sandbox environment, also verify recipient email addresses

### 2. Create a Lambda Function

Create a Lambda function that will send confirmation emails when triggered:

```bash
# Create a deployment package
cd lambda
zip -r email_handler.zip email_handler.py

# Create the Lambda function
aws lambda create-function \
  --function-name booking-confirmation-email \
  --runtime python3.9 \
  --handler email_handler.lambda_handler \
  --zip-file fileb://email_handler.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-ses-role \
  --environment "Variables={SENDER_EMAIL=noreply@yourdomain.com,AWS_REGION=eu-west-2}"
```

### 3. Configure IAM Permissions

Create an IAM role with the necessary permissions for the Lambda function:

1. Create a trust policy for Lambda (trust-policy.json):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "lambda.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

2. Create the IAM role:
   ```bash
   aws iam create-role \
     --role-name lambda-ses-role \
     --assume-role-policy-document file://trust-policy.json
   ```

3. Attach the policy for SES and DynamoDB access:
   ```bash
   aws iam put-role-policy \
     --role-name lambda-ses-role \
     --policy-name lambda-ses-policy \
     --policy-document file://infrastructure/lambda-policy.json
   ```

### 4. Configure DynamoDB Streams

Enable DynamoDB Streams on your booking table to trigger the Lambda function:

1. Enable streams on the DynamoDB table:
   ```bash
   aws dynamodb update-table \
     --table-name booking \
     --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE
   ```

2. Create an event source mapping to trigger Lambda:
   ```bash
   aws lambda create-event-source-mapping \
     --function-name booking-confirmation-email \
     --event-source arn:aws:dynamodb:eu-west-2:YOUR_ACCOUNT_ID:table/booking/stream/TIMESTAMP \
     --starting-position LATEST \
     --batch-size 1
   ```

### 5. Test the Email System

Test the email confirmation system:

1. Create a new booking through the RSVP application
2. Check the Lambda logs in CloudWatch to verify the function was triggered
3. Check your email inbox for the confirmation message

## Customizing the Email Template

The Lambda function in `email_handler.py` contains a basic email template. You can customize this template to match your branding and provide more specific information about the events.

## Next Steps

After setting up the email confirmation system, proceed to Section 3 to build the admin interface for managing bookings and events.