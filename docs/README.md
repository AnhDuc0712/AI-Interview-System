# AI Interview System

Welcome to the AI Interview System project! This documentation provides an overview of the project structure, setup instructions, and usage guidelines.

## Project Structure

The project is organized into several directories:

- **frontend/**: Contains the client-side application built with React.
  - **public/**: Static assets such as images and icons.
  - **src/**: Source code for the React application.
    - **components/**: Reusable React components.
    - **pages/**: Main pages of the application.
    - **App.tsx**: Main component that sets up routing and layout.
  - **package.json**: Configuration file for the frontend application.
  - **tsconfig.json**: TypeScript configuration for the frontend.

- **backend/**: Contains the server-side application built with Node.js and Express.
  - **src/**: Source code for the backend application.
    - **controllers/**: Business logic for different routes.
    - **routes/**: Route definitions mapping HTTP requests to controllers.
    - **server.ts**: Entry point for the backend application.
  - **package.json**: Configuration file for the backend application.
  - **tsconfig.json**: TypeScript configuration for the backend.

- **ai-services/**: Contains AI-related services and functionalities.
  - **src/**: Source code for AI services.
    - **clients/**: Implementations for interacting with external APIs.
    - **models/**: Data models used in AI services.
    - **index.ts**: Entry point for the AI services module.
  - **package.json**: Configuration file for the AI services application.
  - **tsconfig.json**: TypeScript configuration for the AI services.

- **docs/**: Documentation for the project.
- **docker/**: Docker configuration files for containerization.
- **docker-compose.yml**: Defines services, networks, and volumes for Docker containers.
- **README.md**: Main documentation for the AI Interview System project.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd AI-Interview-System
   ```

2. **Install dependencies**:
   - For the frontend:
     ```
     cd frontend
     npm install
     ```
   - For the backend:
     ```
     cd backend
     npm install
     ```
   - For AI services:
     ```
     cd ai-services
     npm install
     ```

3. **Run the applications**:
   - Start the backend server:
     ```
     cd backend
     npm start
     ```
   - Start the frontend application:
     ```
     cd frontend
     npm start
     ```

4. **Docker Setup** (optional):
   - Build and run the Docker containers using:
     ```
     docker-compose up --build
     ```

## Usage Guidelines

- Access the frontend application at `http://localhost:3000`.
- The backend API can be accessed at `http://localhost:5000/api`.
- Refer to the individual service documentation for specific usage instructions.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.