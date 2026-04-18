# Society App - Frontend

React PWA for the Society App community platform.

## Tech Stack

- React 18+
- Redux Toolkit
- Material-UI
- React Router
- Axios

## Quick Start

See [../docs/developer-guide.md](../docs/developer-guide.md) for detailed setup instructions.

```bash
# Install dependencies
npm install

# Configure
cp .env.example .env

# Start development server
npm start

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── manifest.json             # PWA manifest
│   └── service-worker.js         # PWA service worker
├── src/
│   ├── components/
│   │   ├── common/               # Shared components
│   │   ├── Digest/              # Digest viewer
│   │   ├── DemandSupply/        # Marketplace
│   │   └── Auth/                # Auth pages
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Digests.jsx
│   │   ├── Marketplace.jsx
│   │   └── Profile.jsx
│   ├── services/
│   │   └── api.js               # API client
│   ├── store/                   # Redux store
│   ├── App.jsx
│   └── index.js
├── package.json
├── .env.example
├── .eslintrc.json
├── .prettierrc
└── Dockerfile
```

## Available Scripts

```bash
# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Eject configuration (one-way operation)
npm run eject

# Lint code
npm run lint

# Format code
npm run format
```

## Environment Variables

See `.env.example` for all available variables.

Key variables:
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_LOG_LEVEL`: Logging level

## Testing

```bash
# Run all tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

## PWA Features

- Installable on mobile and desktop
- Offline support
- Fast load times
- Native-like experience

## Documentation

- [Architecture](../docs/architecture.md)
- [User Guide](../docs/user-guide.md)
- [Developer Guide](../docs/developer-guide.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)
