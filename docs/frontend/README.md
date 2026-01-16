# Frontend Documentation

## Overview

The frontend application is built using React.js and serves as the primary interface for the Traffic Management System. It allows users to upload video data, view real-time traffic analytics, and monitor system performance.

## Directory Structure

- **src/components/**: Reusable UI components (buttons, layout wrappers, etc.).
- **src/pages/**: Main application views (Home, Analytics, About).
- **src/api/**: API client utilities for communicating with the Flask backend.
- **src/hooks/**: Custom React hooks for state management and side effects.
- **public/**: Static assets (images, icons).

## Installation and Setup

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)

### Development Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
   The application will run at http://localhost:3000.

## Architecture

### Component Hierarchy
The application follows a standard React component tree structure. The root `App` component manages routing and global layout.

### State Management
State is primarily managed using React Context and standard `useState`/`useReducer` hooks. API data is fetched asynchronously and cached where appropriate.

### API Integration
Communication with the backend is handled via the `src/api` module. It abstracts HTTP requests (using `axios` or `fetch`) and handles error responses uniformly.

## Configuration

Environment variables are defined in `.env` files:
- `REACT_APP_API_URL`: The base URL for the backend API (default: `http://localhost:5000`).
- `REACT_APP_ENVIRONMENT`: Current runtime environment (`development`, `production`).

## Building for Production

To create a production-ready build:
```bash
npm run build
```
This generates optimized static files in the `build/` directory, which can be served by Nginx or any static file server.
