from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import boto3
from boto3.dynamodb.conditions import Key
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Conference RSVP API", description="API for managing conference bookings")

# Updated CORS middleware with more explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,  # Changed to False to avoid credentials issues
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly list methods including OPTIONS
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length"],
    max_age=86400,  # Cache preflight requests for 1 day
)

# DynamoDB Configuration
region = 'us-east-2'  # Ohio region
table_name = 'booking'

# More explicit AWS configuration for App Runner environment
try:
    # Create a boto3 session with explicit region
    session = boto3.Session(region_name=region)
    
    # Create boto3 config
    boto3_config = boto3.session.Config(
        signature_version='v4',
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    
    # Initialize DynamoDB resource with the session and config
    dynamo_client = session.resource('dynamodb', config=boto3_config)
    booking_table = dynamo_client.Table(table_name)
    
    logger.info(f"Successfully initialized DynamoDB client for table: {table_name}")
except Exception as e:
    logger.error(f"Error initializing DynamoDB client: {str(e)}")
    raise

# Models
class BookingBase(BaseModel):
    Name: str
    Surname: str
    email: str
    category: str = "Summit"  # Fixed spelling

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    class Config:
        orm_mode = True

# API Endpoints
@app.post("/booking/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate):
    booking_item = {
        "email": booking.email,
        "category": booking.category,  # Fixed spelling
        "Name": booking.Name,
        "Surname": booking.Surname
    }
    
    try:
        booking_table.put_item(Item=booking_item)
        return booking_item
    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

@app.get("/booking/", response_model=List[Booking])
async def list_bookings():
    try:
        logger.info("Attempting to scan DynamoDB table for bookings")
        response = booking_table.scan()
        bookings = response.get('Items', [])
        logger.info(f"Successfully retrieved {len(bookings)} bookings")
        return bookings
    except Exception as e:
        import traceback
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Failed to retrieve bookings: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bookings: {str(e)}")

# Get booking by email and category
@app.get("/booking/{email}/{category}", response_model=Booking)  # Fixed spelling
async def get_booking(email: str, category: str):  # Fixed spelling
    try:
        response = booking_table.get_item(Key={"email": email, "category": category})  # Fixed spelling
        booking = response.get('Item')
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking with email {email} and category {category} not found")
        return booking
    except Exception as e:
        logger.error(f"Failed to retrieve booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve booking: {str(e)}")

# Update booking with both keys
@app.put("/booking/{email}/{category}", response_model=Booking)  # Fixed spelling
async def update_booking(email: str, category: str, booking: BookingBase):  # Fixed spelling
    try:
        # Check if booking exists
        response = booking_table.get_item(Key={"email": email, "category": category})  # Fixed spelling
        if not response.get('Item'):
            raise HTTPException(status_code=404, detail=f"Booking with email {email} and category {category} not found")
        
        # Update the booking
        booking_table.update_item(
            Key={"email": email, "category": category},  # Fixed spelling
            UpdateExpression="SET #name = :name, Surname = :surname",
            ExpressionAttributeNames={"#name": "Name"},  # 'Name' is a reserved word in DynamoDB
            ExpressionAttributeValues={
                ":name": booking.Name,
                ":surname": booking.Surname
            },
            ReturnValues="ALL_NEW"
        )
        
        # Get the updated item
        updated_booking = booking_table.get_item(Key={"email": email, "category": category})  # Fixed spelling
        return updated_booking['Item']
    
    except Exception as e:
        logger.error(f"Failed to update booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")

# Delete booking with both keys
@app.delete("/booking/{email}/{category}", status_code=status.HTTP_204_NO_CONTENT)  # Fixed spelling
async def delete_booking(email: str, category: str):  # Fixed spelling
    try:
        # Check if booking exists
        response = booking_table.get_item(Key={"email": email, "category": category})  # Fixed spelling
        if not response.get('Item'):
            raise HTTPException(status_code=404, detail=f"Booking with email {email} and category {category} not found")
        
        # Delete the booking
        booking_table.delete_item(Key={"email": email, "category": category})  # Fixed spelling
        return None
    except Exception as e:
        logger.error(f"Failed to delete booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete booking: {str(e)}")

# Get bookings by email
@app.get("/booking/email/{email}", response_model=List[Booking])
async def get_bookings_by_email(email: str):
    try:
        response = booking_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        bookings = response.get('Items', [])
        if not bookings:
            raise HTTPException(status_code=404, detail=f"No bookings found for email {email}")
        return bookings
    except Exception as e:
        logger.error(f"Failed to retrieve bookings by email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bookings: {str(e)}")

# Get bookings by category
@app.get("/booking/category/{category}", response_model=List[Booking])  # Fixed spelling
async def get_bookings_by_category(category: str):  # Fixed spelling
    try:
        # For Global Secondary Index, we'd use query. But for scan:
        response = booking_table.scan(
            FilterExpression=Key('category').eq(category)  # Fixed spelling
        )
        bookings = response.get('Items', [])
        if not bookings:
            raise HTTPException(status_code=404, detail=f"No bookings found for category {category}")
        return bookings
    except Exception as e:
        logger.error(f"Failed to retrieve bookings by category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bookings: {str(e)}")

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RSVP API"}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)