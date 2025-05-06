# Conference RSVP Application Documentation

## Project Overview
The Conference RSVP Application is a full-stack web application designed to manage event bookings for conferences, summits, and workshops. It provides a RESTful API for creating, retrieving, updating, and deleting bookings, paired with a user-friendly frontend for attendees to interact with the system. The application is deployed on AWS, leveraging serverless and managed services for scalability and ease of maintenance, with a static frontend hosted on an EC2 instance.

- **Purpose**: Enable users to register for events, view bookings by email or category, and manage bookings, with a demo mode for local testing without a backend.
- **Use Case**: Streamline RSVP management for event organizers and provide an accessible interface for attendees.
- **Problems Solved**: Offers a scalable backend with minimal operational overhead, reliable data storage, and a simple web interface for end-users.
- **Components**:
  - **Backend**: FastAPI (Python) application, containerized with Docker, deployed on AWS App Runner.
  - **Database**: AWS DynamoDB for storing booking data.
  - **Container Registry**: Amazon ECR for storing Docker images.
  - **Frontend**: Single-page HTML/CSS/JavaScript application, hosted on an AWS EC2 instance with Apache.
- **Cloud Provider**: AWS (Region: us-east-2).

## Architecture
- **Backend**: FastAPI application running in a Docker container on AWS App Runner (`conference-rsvp-api`, 1 vCPU, 2 GB).
- **Database**: DynamoDB table (`booking`, partition key `email`, sort key `category`, on-demand billing mode).
- **Container Registry**: Private ECR repository (`conference-rsvp-api`).
- **Frontend**: Single `index.html` file served by Apache on an EC2 instance (`t2.micro`, `/var/www/html`), accessible via the instance’s public IP (e.g., `http://<public-ip>`).

**Architecture Diagram** (Click the preview below to see the full cloud architecture diagram):


[![Cloud Architecture](/Conference_RSVP_Application_Architecture.drawio%20(1).png)](/Conference_RSVP_Application_Architecture.drawio%20(2).pdf)

<!-- To visualize the architecture, create a diagram in draw.io (https://app.diagrams.net/) or a similar tool using the following components, connections, and layout: -->

**Components**:
1. **Client (Browser)**: Rectangle labeled “Client (Browser)” (end-user accessing the frontend).
2. **EC2 (t2.micro, Apache)**: Rectangle labeled “EC2 (t2.micro, Apache)” (hosts `index.html`).
3. **App Runner (FastAPI)**: Rectangle labeled “App Runner (FastAPI)” (runs the backend API).
4. **DynamoDB (booking)**: Rectangle labeled “DynamoDB (booking)” (stores booking data).
5. **ECR (Docker Image)**: Rectangle labeled “ECR (Docker Image)” (stores FastAPI Docker image).

<!-- **Connections**:
1. **Client ↔ EC2**: Bidirectional arrow labeled “HTTP (index.html)”. The browser retrieves `index.html` from EC2.
2. **EC2 ↔ App Runner**: Bidirectional arrow labeled “HTTPS (API Calls)”. The frontend makes POST/GET/DELETE API calls to App Runner.
3. **App Runner ↔ DynamoDB**: Bidirectional arrow labeled “CRUD Operations”. App Runner performs create/read/update/delete operations on DynamoDB.
4. **App Runner → ECR**: Unidirectional arrow labeled “Pull Docker Image”. App Runner pulls the Docker image from ECR during deployment. -->

<!-- **Layout**:
- Place **Client** on the left.
- Position **EC2** to the right of **Client**.
- Place **App Runner** to the right of **EC2**.
- Position **DynamoDB** and **ECR** below **App Runner**, side-by-side at the same vertical level to show equal dependency:
  - **DynamoDB**: Left or top below App Runner.
  - **ECR**: Right or bottom, aligned with DynamoDB.
- Use distinct colors (e.g., blue for Client, green for EC2, orange for App Runner, purple for DynamoDB, gray for ECR).
- Add a title: “Conference RSVP Application Architecture (AWS, us-east-2)”. -->

<!-- **Draw.io Steps**:
1. Open draw.io and create a blank diagram.
2. Add rectangles for Client, EC2, App Runner, DynamoDB, and ECR.
3. Arrange components: Client → EC2 → App Runner, with DynamoDB and ECR below App Runner at the same level.
4. Draw arrows with labels as described.
5. Style components (colors, font) and adjust labels.
6. Save as PNG, SVG, or draw.io file. -->

**Flow**:
- Client accesses frontend (`index.html`) on EC2 via HTTP.
- Frontend makes API calls (POST/GET/DELETE) to App Runner via HTTPS.
- App Runner performs CRUD operations on DynamoDB.
- App Runner pulls the Docker image from ECR during deployment or updates.

## Setup Instructions

### Backend Setup
1. **Create ECR Repository**:
   ```bash
   aws ecr create-repository --repository-name conference-rsvp-api --region us-east-2
   ```
   - Output: Repository URI (e.g., `<account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api`).
   - Note: Replace `<account-id>` with your AWS account ID.

2. **Build and Push Docker Image**:
   - **Dockerfile**:
     ```dockerfile
     FROM python:3.9-slim
     WORKDIR /app
     COPY requirements.txt .
     RUN pip install --no-cache-dir -r requirements.txt
     COPY . .
     EXPOSE 8000
     CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
     ```
   - **requirements.txt**:
     ```
     fastapi==0.95.1
     uvicorn==0.22.0
     boto3==1.26.135
     pydantic==1.10.7
     ```
   - **main.py** (FastAPI):
     ```python
     from fastapi import FastAPI, HTTPException
     from fastapi.middleware.cors import CORSMiddleware
     from pydantic import BaseModel
     import boto3
     from boto3.dynamodb.conditions import Key
     from typing import List

     app = FastAPI()

     app.add_middleware(
         CORSMiddleware,
         allow_origins=["*"],
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )

     dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
     table = dynamodb.Table('booking')

     class Booking(BaseModel):
         Name: str
         Surname: str
         email: str
         category: str

     @app.post("/booking/", response_model=Booking)
     async def create_booking(booking: Booking):
         try:
             table.put_item(Item=booking.dict())
             return booking
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

     @app.get("/booking/", response_model=List[Booking])
     async def get_bookings():
         try:
             response = table.scan()
             return response.get('Items', [])
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

     @app.get("/booking/email/{email}", response_model=List[Booking])
     async def get_bookings_by_email(email: str):
         try:
             response = table.query(KeyConditionExpression=Key('email').eq(email))
             return response.get('Items', [])
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

     @app.get("/booking/category/{category}", response_model=List[Booking])
     async def get_bookings_by_category(category: str):
         try:
             response = table.scan(FilterExpression=Key('category').eq(category))
             return response.get('Items', [])
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

     @app.delete("/booking/{email}/{category}")
     async def delete_booking(email: str, category: str):
         try:
             response = table.delete_item(
                 Key={'email': email, 'category': category},
                 ConditionExpression="attribute_exists(email) AND attribute_exists(category)"
             )
             return {"message": "Booking deleted"}
         except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
             raise HTTPException(status_code=404, detail="Booking not found")
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

     @app.get("/health")
     async def health_check():
         return {"status": "healthy"}
     ```
   - Build and push:
     ```bash
     aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com
     docker build -t conference-rsvp-api .
     docker tag conference-rsvp-api:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api:latest
     docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api:latest
     ```

3. **Create IAM Role**:
   - **trust-policy.json**:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Principal": {
             "Service": "tasks.apprunner.amazonaws.com"
           },
           "Action": "sts:AssumeRole"
         }
       ]
     }
     ```
   - **dynamodb-policy.json**:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": [
             "dynamodb:PutItem",
             "dynamodb:GetItem",
             "dynamodb:UpdateItem",
             "dynamodb:DeleteItem",
             "dynamodb:Scan",
             "dynamodb:Query"
           ],
           "Resource": "arn:aws:dynamodb:us-east-2:<account-id>:table/booking"
         }
       ]
     }
     ```
   - Create role:
     ```bash
     aws iam create-role --role-name AppRunnerDynamoDBRole --assume-role-policy-document file://trust-policy.json
     aws iam put-role-policy --role-name AppRunnerDynamoDBRole --policy-name DynamoDBAccess --policy-document file://dynamodb-policy.json
     aws iam attach-role-policy --role-name AppRunnerDynamoDBRole --policy-arn arn:aws:iam::aws:policy/AWSAppRunnerServicePolicyForECRAccess
     ```

4. **Create DynamoDB Table**:
   ```bash
   aws dynamodb create-table \
     --table-name booking \
     --attribute-definitions AttributeName=email,AttributeType=S AttributeName=category,AttributeType=S \
     --key-schema AttributeName=email,KeyType=HASH AttributeName=category,KeyType=RANGE \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-2
   ```
   - Schema: Partition key `email` (string), sort key `category` (string), on-demand billing.

5. **Deploy App Runner Service**:
   - **apprunner-config.json**:
     ```json
     {
       "SourceConfiguration": {
         "ImageRepository": {
           "ImageIdentifier": "<account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api:latest",
           "ImageConfiguration": {
             "Port": "8000"
           },
           "ImageRepositoryType": "ECR"
         },
         "AuthenticationConfiguration": {
           "AccessRoleArn": "arn:aws:iam::<account-id>:role/AppRunnerDynamoDBRole"
         },
         "AutoDeploymentsEnabled": true
       },
       "InstanceConfiguration": {
         "Cpu": "1 vCPU",
         "Memory": "2 GB",
         "InstanceRoleArn": "arn:aws:iam::<account-id>:role/AppRunnerDynamoDBRole"
       },
       "NetworkConfiguration": {
         "EgressConfiguration": {
           "EgressType": "DEFAULT"
         }
       }
     }
     ```
   - Deploy:
     ```bash
     aws apprunner create-service \
       --service-name conference-rsvp-api \
       --cli-input-json file://apprunner-config.json \
       --region us-east-2
     ```

### Frontend Setup
1. **Create Security Group**:
   ```bash
   aws ec2 create-security-group --group-name WebServerSG --description "Security group for web server" --region us-east-2
   aws ec2 authorize-security-group-ingress --group-id <security-group-id> --protocol tcp --port 80 --cidr 0.0.0.0/0 --region us-east-2
   aws ec2 authorize-security-group-ingress --group-id <security-group-id> --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-2
   ```

2. **Launch EC2 Instance**:
   ```bash
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1f0 \
     --instance-type t2.micro \
     --key-name <your-key-pair> \
     --security-group-ids <security-group-id> \
     --region us-east-2 \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=RSVP-Web-Server}]'
   ```

3. **Install Apache and Deploy Frontend**:
   - SSH:
     ```bash
     ssh -i <your-key-pair>.pem ec2-user@<public-ip>
     ```
   - Install Apache:
     ```bash
     sudo yum update -y
     sudo yum install httpd -y
     sudo systemctl start httpd
     sudo systemctl enable httpd
     ```
   - Deploy `index.html`:
     ```bash
     scp -i <your-key-pair>.pem index.html ec2-user@<public-ip>:/home/ec2-user/index.html
     sudo mv /home/ec2-user/index.html /var/www/html/index.html
     sudo chown apache:apache /var/www/html/index.html
     sudo chmod 644 /var/www/html/index.html
     ```

4. **Test Frontend**:
   - Access: `http://<public-ip>`
   - Operations:
     - Create bookings (POST `/booking/`).
     - List bookings (GET `/booking/`).
     - Delete bookings (DELETE `/booking/{email}/{category}`).
     - Demo mode (local storage via `useLocalAPI` checkbox).
   - Status: All operations confirmed working (May 6, 2025).

### Code Details
- **main.py** (Backend):
  - **Framework**: FastAPI.
  - **Endpoints**:
    - `POST /booking/`: Create a booking.
    - `GET /booking/`: List all bookings.
    - `GET /booking/email/{email}`: List bookings by email.
    - `GET /booking/category/{category}`: List bookings by category.
    - `DELETE /booking/{email}/{category}`: Delete a booking.
    - `GET /health`: Health check.
  - **Database**: DynamoDB (`booking` table).
  - **CORS**: Enabled (`allow_origins=["*"]`).
- **index.html** (Frontend):
  - **Structure**: HTML form for creating bookings (Name, Surname, Email, Category dropdown), table for listing bookings, delete buttons, demo mode toggle.
  - **CSS**: Embedded, responsive design (flexbox, 800px max-width, styled form/table/buttons).
  - **JavaScript**:
    - Hardcoded API URL: `https://sn.us-east-2.awsapprunner.com`.
    - Uses `fetch` for API requests (POST, GET, DELETE).
    - Local storage for demo mode (`localBookings`).
    - Functions: `makeRequest`, `handleLocalRequest`, `getBookings`, `displayBookings`, `deleteBooking`, `showMessage`.
  - **Features**:
    - Create/list/delete bookings.
    - Demo mode with local storage.
    - Success/error messages (auto-hide after 5 seconds).

### Troubleshooting
- **App Runner Configuration**:
  - **Issue**: Initial `apprunner-config.json` had `InstanceConfiguration` and `NetworkConfiguration` nested under `SourceConfiguration`.
  - **Fix**: Moved to top-level, used `--cli-input-json`:
    ```bash
    aws apprunner create-service --service-name conference-rsvp-api --cli-input-json file://apprunner-config.json --region us-east-2
    ```
- **EC2 Issues**:
  - **Page Not Loading**: Check Apache status (`sudo systemctl status httpd`), security group (port 80), file permissions (`ls -l /var/www/html`).
  - **API Connectivity**: Verify App Runner URL, CORS settings, browser console errors.
- **DynamoDB Errors**: Ensure `AppRunnerDynamoDBRole` has correct permissions (`dynamodb-policy.json`).
- **Frontend Errors**: Check browser console for `fetch` errors, confirm API URL.

### Maintenance
- **Monitoring**:
  - **App Runner**: Enable CloudWatch logs:
    ```bash
    aws apprunner update-service --service-arn <service-arn> --region us-east-2
    ```
  - **EC2**: Monitor CPU/memory via CloudWatch, check Apache logs (`/var/log/httpd`).
  - **DynamoDB**: Track read/write operations and storage in AWS Console.
- **Scaling**:
  - **App Runner**: Auto-scales based on traffic; adjust CPU/memory if needed (`aws apprunner update-service`).
  - **DynamoDB**: On-demand mode auto-scales read/write capacity.
  - **EC2**: Upgrade to larger instance (e.g., `t2.small`) or add Application Load Balancer for high traffic.
- **Updates**:
  - **Backend**: Push new Docker image to ECR; App Runner auto-deploys (`AutoDeploymentsEnabled: true`).
    ```bash
    docker build -t conference-rsvp-api .
    docker tag conference-rsvp-api:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api:latest
    docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/conference-rsvp-api:latest
    ```
  - **Frontend**: Update `index.html`:
    ```bash
    scp -i <your-key-pair>.pem index.html ec2-user@<public-ip>:/home/ec2-user/index.html
    sudo mv /home/ec2-user/index.html /var/www/html/index.html
    sudo chown apache:apache /var/www/html/index.html
    sudo chmod 644 /var/www/html/index.html
    sudo systemctl restart httpd
    ```
<!-- - **CI/CD**: -->
  <!-- - Backend: Use GitHub Actions to automate Docker builds/pushes to ECR. -->
  <!-- - Frontend: Automate `index.html` updates to EC2 via GitHub Actions or AWS CodePipeline. -->
- **Security**:
  - Restrict EC2 SSH access: Update security group to your IP (`--cidr <your-ip>/32` for port 22).
  - Consider HTTPS for EC2 (e.g., Let’s Encrypt or ALB with ACM).
  - Rotate IAM role credentials if needed.

### Notes
- **App Runner URL**: `https://sn.us-east-2.awsapprunner.com` (confirmed May 6, 2025).
- **Frontend Status**: Fully operational (create, list, delete bookings; demo mode).
- **TCO**: To be calculated separately (pending usage metrics: Docker image size, API requests, bookings, read/write operations, frontend users).
- **Future Enhancements** (Optional):
  - Add HTTPS to EC2 (ALB).
  - Implement monitoring (CloudWatch for EC2/App Runner, DynamoDB metrics).
  - Add CI/CD pipelines (GitHub Actions).
  - Enhance frontend (e.g., update booking form, filtering, authentication).
  - Configure custom domain for EC2 or App Runner.