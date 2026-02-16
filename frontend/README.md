# Getting Started

This frontend application was bootstrapped using Create React App.

---

## Requirements

- Node.js 16+ recommended
- npm 8+ recommended

> [!IMPORTANT]
> Ensure Node.js and npm are installed and available in your system PATH before running the project.

To verify installation:

```bash
node -v
npm -v
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd <project-folder>
npm install
```

> [!NOTE]
> The `npm install` command installs all dependencies listed in `package.json`.

---

## Running the Application

### `npm start`

Starts the development server.

```bash
npm start
```

- Runs the app in development mode
- Opens http://localhost:3000 in your browser
- Automatically reloads when changes are saved
- Displays lint errors in the console

> [!IMPORTANT]
> The development server is not optimized for production use.

---

## Testing

### `npm test`

Runs the test suite in interactive watch mode.

```bash
npm test
```

- Executes unit tests
- Re-runs tests when related files change

> [!NOTE]
> Press `q` to quit the test runner.

---

## Production Build

### `npm run build`

Creates an optimized production build.

```bash
npm run build
```

- Output directory: `build/`
- Optimized and minified static files
- Generates hashed filenames for caching
- Ready for deployment

> [!IMPORTANT]
> Always generate a production build before deploying.

---

## Advanced Configuration

### `npm run eject`

Exposes all underlying configuration files (Webpack, Babel, ESLint, etc.).

```bash
npm run eject
```

- Copies configuration files into your project
- Provides full control over the build setup

> [!WARNING]
> This action is irreversible.
> Once ejected, you cannot revert to the default Create React App configuration.
> Only use this if deep customization is required.
