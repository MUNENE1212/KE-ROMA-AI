# KE-ROUMA - African Heritage Recipe App

A clean, modern web and mobile application for AI-powered African recipe recommendations.

## 📁 Project Structure

```
ke-rouma/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
│
├── config/               # Configuration files
│   └── config.py
│
├── models/               # Database models and schemas
│   ├── database.py
│   ├── schemas.py
│   └── user.py
│
├── routes/               # API route handlers
│   ├── auth.py
│   ├── chat.py
│   ├── main.py
│   ├── payments.py
│   ├── recipes.py
│   └── users.py
│
├── services/             # Business logic services
│   ├── ai_service.py
│   ├── intasend_service.py
│   ├── multi_ai_service.py
│   └── recipe_service.py
│
├── static/               # Frontend assets
│   ├── css/
│   │   ├── auth-styles.css
│   │   └── styles.css
│   └── js/
│       └── app.js
│
├── templates/            # HTML templates
│   └── index.html
│
├── mobile-app/           # React Native mobile app
│   ├── src/
│   ├── App.tsx
│   └── package.json
│
├── tests/                # Test files
│   └── test_integrations.py
│
├── scripts/              # Utility scripts
│   └── run.py
│
├── docs/                 # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── FRONTEND_ARCHITECTURE.md
│   └── README.md
│
├── examples/             # Example and demo files
│   └── demo_ai_payments.py
│
└── backup/               # Backup files
    ├── clean_app.html
    ├── app.js.backup
    └── app_broken.js
```

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   - Web: http://localhost:8000
   - API docs: http://localhost:8000/docs

## 🔧 Development

- **Backend**: FastAPI with Python 3.8+
- **Frontend**: Modern JavaScript with modular architecture
- **Mobile**: React Native with Expo
- **Database**: MongoDB Atlas
- **AI**: Multi-provider support (OpenAI, Gemini, Hugging Face, Cohere)
- **Payments**: M-Pesa via IntaSend

## 📚 Documentation

See the `docs/` directory for comprehensive documentation:
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## 🧪 Testing

```bash
python -m pytest tests/
```

## 📱 Mobile App

The React Native mobile app is in the `mobile-app/` directory:

```bash
cd mobile-app
npm install
expo start
```
