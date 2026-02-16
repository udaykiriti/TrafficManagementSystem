# Frontend Documentation

---

# Overview

The frontend application is built using **React.js** and serves as the primary user interface for the AI Traffic Management System.

It enables users to:

- Upload traffic video feeds
- Monitor real-time vehicle analytics
- View optimized signal timings
- Analyze historical system performance

The frontend communicates with the Flask backend via REST APIs.

---

# Directory Structure

```
frontend/
│
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Main application views
│   ├── api/            # API communication layer
│   ├── hooks/          # Custom React hooks
│   ├── context/        # Global state providers (if applicable)
│   └── App.js          # Root component
│
├── public/             # Static assets
└── package.json        # Dependencies and scripts
```

### Key Directories

| Path | Description |
|------|------------|
| `src/components/` | Reusable UI elements (buttons, cards, layout wrappers) |
| `src/pages/` | Core views (Home, Analytics, About, etc.) |
| `src/api/` | Backend API abstraction layer |
| `src/hooks/` | Custom React hooks for logic reuse |
| `public/` | Static assets and HTML template |

---

# Installation and Setup

## Prerequisites

- Node.js 16+ recommended
- npm 8+ recommended

> [!IMPORTANT]
> Ensure Node.js and npm are properly installed and available in your system PATH.

Verify installation:

```bash
node -v
npm -v
```

---

## Development Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm start
```

The application will run at:

```
http://localhost:3000
```

> [!NOTE]
> The development server includes hot reloading and is not optimized for production.

---

# Architecture

## Component Hierarchy

The application follows a standard React component tree:

- `App` acts as the root component
- Handles routing and global layout
- Pages render feature-specific components
- Shared components remain reusable and isolated

This structure promotes maintainability and scalability.

---

## State Management

State is handled using:

- React `useState`
- React `useReducer`
- React Context API (for global state)

API responses are fetched asynchronously and cached where necessary to reduce redundant network calls.

> [!IMPORTANT]
> Avoid excessive global state. Keep state localized when possible to maintain predictable component behavior.

---

## API Integration

All backend communication is abstracted inside:

```
src/api/
```

Responsibilities of the API layer:

- Centralized HTTP client configuration
- Base URL management
- Standardized error handling
- Request/response transformation

Environment-based API routing is supported via `.env` configuration.

---

# Configuration

Environment variables are defined in `.env` files.

Example:

```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
```

### Supported Variables

| Variable | Description |
|----------|------------|
| `REACT_APP_API_URL` | Base URL of the backend API |
| `REACT_APP_ENVIRONMENT` | Runtime environment (`development`, `production`) |

> [!IMPORTANT]
> All custom environment variables must be prefixed with `REACT_APP_` to be accessible in the application.

---

# Production Build

To generate a production-ready build:

```bash
npm run build
```

This creates an optimized output in:

```
build/
```

### Production Build Features

- Minified and optimized assets
- Hashed filenames for long-term caching
- Tree-shaking for reduced bundle size
- Static deployment ready

---

# Deployment

The generated `build/` directory can be deployed using:

- Nginx
- Apache
- Docker (with Nginx)
- Static hosting services

Example using a static server:

```bash
npx serve -s build
```

> [!IMPORTANT]
> Ensure `REACT_APP_API_URL` points to your production backend before building.

---

# Best Practices

- Keep components small and reusable
- Centralize API logic
- Avoid hardcoding API URLs
- Use environment variables for configuration
- Perform production builds before deployment
- Enable browser caching in production

---

# Future Improvements

- TypeScript migration
- Component-level testing (Jest + React Testing Library)
- WebSocket integration for live traffic updates
- Performance optimization using code splitting
