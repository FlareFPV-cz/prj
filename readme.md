# Soil Analysis and Crop Monitoring System

A comprehensive web application for soil analysis, crop health monitoring, and agricultural recommendations using machine learning and remote sensing data.

## Features

- **Soil Analysis**
  - Detailed soil composition analysis
  - Nutrient level assessment
  - pH and CEC analysis
  - Texture classification

- **Crop Health Monitoring**
  - Vegetation indices (NDVI, EVI, SAVI, ARVI)
  - Time-series analysis
  - Health status visualization

- **ML-Powered Recommendations**
  - Soil condition predictions
  - Crop recommendations
  - GPT-2 based detailed insights
  - Custom-trained models

## Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLite (Database)
- Machine Learning Models (scikit-learn)
- GPT-2 for soil analysis insights
- JWT Authentication

### Frontend
- Svelte + Vite
- Chart.js for data visualization
- Modern responsive UI

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm

### Setup

1. Clone the repository and install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Generate RSA keys for secure authentication:
```bash
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private.pem -out public.pem
openssl rsa -in private.pem -traditional -out private.pem
```

3. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

4. Install and run the frontend:
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive API documentation.

Key endpoints:
- `/soil-composition/*` - Soil analysis endpoints
- `/predict` - ML model predictions
- `/crop-health/*` - Crop health monitoring

## Authentication

The application uses JWT-based authentication with RSA encryption for password security. All API endpoints (except login/signup) require authentication.

## Machine Learning Models

- Soil classification model (RandomForest)
- Fine-tuned GPT-2 model for detailed soil analysis
- Custom models for crop yield prediction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Jan Kozeluh - jankozeluh.job@seznam.cz

## Acknowledgments

- ISRIC World Soil Database
- OpenAI GPT-2
- Remote sensing data providers