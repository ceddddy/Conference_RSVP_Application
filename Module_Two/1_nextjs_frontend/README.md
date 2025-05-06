# Section 1: Setting up Next.js Frontend

In this section, we'll create a modern, containerized frontend for our RSVP system using Next.js. This will replace the simple HTML frontend from Module One with a more robust and feature-rich application.

## Objectives

- Create a Next.js application with proper project structure
- Design responsive UI components for the RSVP system
- Connect the Next.js frontend to our FastAPI backend
- Containerize the Next.js application for deployment

## Prerequisites

- Node.js (version 14.x or higher)
- npm or yarn package manager
- Basic understanding of React and Next.js
- Docker installed on your development machine

## Steps

### 1. Create a Next.js Application

First, we'll use the Create Next App tool to generate a new Next.js project:

```bash
npx create-next-app@latest frontend
cd frontend
```

### 2. Project Structure

Our Next.js application will have the following structure:

```
frontend/
├── components/         # Reusable UI components
│   ├── BookingForm.js  # Form for creating bookings
│   ├── BookingList.js  # Display list of bookings
│   └── Layout.js       # Layout wrapper
├── pages/              # Application pages
│   ├── index.js        # Home page
│   ├── bookings.js     # Bookings management page
│   └── api/            # API routes
├── styles/             # CSS styles
├── utils/              # Utility functions
│   └── api.js          # API client
├── Dockerfile          # Docker configuration
├── .dockerignore       # Docker ignore file
└── next.config.js      # Next.js configuration
```

### 3. Connect to the Backend

We'll create an API client utility to connect to our FastAPI backend:

```javascript
// utils/api.js
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchBookings() {
  const response = await fetch(`${API_URL}/booking/`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch bookings');
  }
  
  return response.json();
}

export async function createBooking(bookingData) {
  const response = await fetch(`${API_URL}/booking/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(bookingData),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create booking');
  }
  
  return response.json();
}
```

### 4. Containerize the Application

Create a Dockerfile to containerize the Next.js application:

```dockerfile
# See Dockerfile in this directory
```

And a .dockerignore file:

```
node_modules
.next
.git
```

### 5. Configure for App Runner

Create an App Runner configuration file for deploying the containerized Next.js application.

## Testing Locally

To test the Next.js application locally:

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Build and run the Docker container:
   ```bash
   docker build -t rsvp-frontend .
   docker run -p 3000:3000 rsvp-frontend
   ```

## Next Steps

After completing this section, you'll have a containerized Next.js frontend ready for deployment. Proceed to Section 2 to set up the email confirmation system.