# AWS App Runner RSVP Workshop - Module Two

## Containerized Frontend & Email Notifications

This module builds upon the foundation established in Module One by enhancing our RSVP system with a containerized Next.js frontend, email confirmations via AWS Lambda and SES, and a separate admin interface for event management.

## Architecture Overview

The enhanced system will include:

- **Main App (example.co.za)**: A containerized Next.js frontend application that connects to our FastAPI backend
- **Admin App (admin.example.co.za)**: A separate interface for administrators to manage events and registrations
- **Client App (client.example.co.za)**: A user portal for viewing booking information
- **Email Notifications**: Automated email confirmations sent when users register for events using AWS Lambda and SES
- **Multi-Container Deployment**: Proper configuration for deploying multiple containers across subdomains

## Workshop Sections

### 1. Setting up Next.js Frontend
- Creating a Next.js application to replace the simple HTML frontend
- Dockerizing the Next.js app for containerized deployment
- Connecting the Next.js frontend to the FastAPI backend

### 2. Creating the Email Confirmation System
- Setting up AWS Simple Email Service (SES) for transactional emails
- Creating a Lambda function triggered by new bookings
- Configuring necessary IAM permissions for Lambda and SES
- Integrating the email system with the booking flow

### 3. Building the Admin Interface
- Setting up a separate admin application with enhanced capabilities
- Creating admin-specific functionality (event management, registration metrics)
- Configuring proper routing between main app and admin app

### 4. Deployment
- Configuring multi-container deployment with AWS App Runner
- Setting up domain and subdomain routing for the different applications
- Testing the integrated system end-to-end

## Prerequisites

Before starting Module Two, ensure you have:
- Completed Module One of this workshop
- Basic understanding of React and Next.js
- AWS account with permissions for Lambda, SES, and App Runner
- Docker installed on your development machine
- Node.js and npm installed for Next.js development

## Learning Objectives

By completing this module, you will:
- Understand how to containerize a Next.js application
- Learn how to set up serverless email notifications using AWS Lambda and SES
- Gain experience with multi-container deployments in AWS App Runner
- Implement subdomain routing for different application components
- Design and build an admin interface separate from the main application

## Getting Started

Begin with Section 1 to set up the Next.js frontend. Each section builds upon the previous one, so it's recommended to complete them in order.

Navigate to the `1_nextjs_frontend` directory to begin.