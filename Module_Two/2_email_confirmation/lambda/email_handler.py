import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SES client
ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'eu-west-2'))

# Email configuration
SENDER = os.environ.get('SENDER_EMAIL', 'noreply@example.co.za')
CHARSET = 'UTF-8'

def lambda_handler(event, context):
    """
    Lambda function to send confirmation emails for RSVP bookings.
    
    Expected event format:
    {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@example.com",
        "category": "Summit"
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # For DynamoDB stream events, the actual booking data is in Records[0].dynamodb.NewImage
        if 'Records' in event and len(event['Records']) > 0 and 'dynamodb' in event['Records'][0]:
            record = event['Records'][0]['dynamodb']['NewImage']
            booking = {
                'name': record.get('Name', {}).get('S', ''),
                'surname': record.get('Surname', {}).get('S', ''),
                'email': record.get('email', {}).get('S', ''),
                'category': record.get('category', {}).get('S', '')
            }
        else:
            # Direct invocation with booking data
            booking = event
        
        # Validate required fields
        required_fields = ['name', 'surname', 'email', 'category']
        for field in required_fields:
            if not booking.get(field):
                error_msg = f"Missing required field: {field}"
                logger.error(error_msg)
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': error_msg})
                }
        
        # Prepare email content
        subject = f"Registration Confirmation: {booking['category']}"
        
        # HTML body with some styling
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Registration Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear {booking['name']} {booking['surname']},</p>
                    <p>Thank you for registering for our <strong>{booking['category']}</strong> event!</p>
                    <p>Your registration has been confirmed and we look forward to seeing you there.</p>
                    <p>Event details will be sent to you in a separate email closer to the date.</p>
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>Best regards,<br>The Event Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text alternative
        text_body = f"""
        Dear {booking['name']} {booking['surname']},
        
        Thank you for registering for our {booking['category']} event!
        
        Your registration has been confirmed and we look forward to seeing you there.
        
        Event details will be sent to you in a separate email closer to the date.
        
        If you have any questions, please don't hesitate to contact us.
        
        Best regards,
        The Event Team
        
        This is an automated message, please do not reply to this email.
        """
        
        # Send email
        response = ses_client.send_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [booking['email']]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': CHARSET
                },
                'Body': {
                    'Text': {
                        'Data': text_body,
                        'Charset': CHARSET
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': CHARSET
                    }
                }
            }
        )
        
        logger.info(f"Email sent successfully to {booking['email']}. MessageId: {response['MessageId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Email sent successfully',
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        logger.error(error_msg)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_msg})
        }