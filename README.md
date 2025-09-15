# 🍽️ KE-ROUMA - AI-Powered African Recipe Experience

**Transform your cooking with AI-driven African cuisine recommendations, interactive cooking guidance, and cultural storytelling.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-orange.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

## ✨ Features

### 🤖 AI-Powered Recipe Generation
- **Multi-Provider AI Support**: OpenAI GPT-4, Google Gemini, Hugging Face, Cohere
- **Mood-Based Recommendations**: Get recipes based on your current mood and energy level
- **Smart Ingredient Analysis**: Intelligent substitution suggestions and nutritional insights
- **Cultural Storytelling**: Learn about the history and traditions behind each dish
- **Real-time Generation**: Instant recipe creation with personalized adjustments

### 🏠 Interactive Cooking Experience
- **Step-by-Step AI Guidance**: Real-time cooking instructions with smart timers
- **Voice Commands**: Hands-free cooking with voice-activated assistance (Premium)
- **Smart Timer System**: Automated cooking timers with desktop notifications
- **Progress Visualization**: Visual cooking progress with completion estimates
- **Recipe Scaling**: Automatically adjust recipes for different serving sizes

### 💳 Premium Features
- **Unlimited AI Recipes**: Generate unlimited personalized recipes
- **Advanced Nutritional Analytics**: Detailed calorie counting and meal planning
- **M-Pesa Integration**: Seamless mobile payments with instant activation
- **Exclusive Recipe Collections**: Curated premium recipes from master chefs
- **Priority Support**: Direct access to our culinary experts

### 🎨 Beautiful User Experience
- **Custom Typography**: Premium Google Fonts (Inter, Playfair Display, Nunito)
- **Glassmorphism Design**: Modern frosted glass effects and animations
- **Interactive Microinstructions**: Helpful hints and contextual guidance
- **Responsive Animations**: Smooth transitions and hover effects
- **Dark Mode Support**: Automatic dark/light theme adaptation

### 📱 Responsive Design
- **Mobile-First Architecture**: Optimized for all screen sizes
- **Progressive Web App**: Installable on mobile devices with offline capabilities
- **Touch-Optimized**: Swipe gestures and touch-friendly interactions
- **Accessibility First**: WCAG 2.1 AA compliant with screen reader support
- **Cross-Browser**: Tested on Chrome, Firefox, Safari, and Edge

## 📁 Project Structure

```
ke-rouma/
├── app.py                 # Main FastAPI application with lifespan management
├── requirements.txt       # Python dependencies with version pinning
├── .env.example          # Environment variables template with examples
├── .gitignore            # Git ignore rules for security
│
├── config/               # Configuration management
│   └── config.py         # Pydantic settings with validation
│
├── models/               # Database models and Pydantic schemas
│   ├── database.py       # MongoDB connection and initialization
│   ├── schemas.py        # API request/response models
│   └── user.py           # User authentication models
│
├── routes/               # FastAPI route handlers
│   ├── auth.py           # JWT authentication endpoints
│   ├── chat.py           # AI chat assistant integration
│   ├── main.py           # Core application routes
│   ├── payments.py       # M-Pesa payment processing
│   ├── recipes.py        # Recipe generation and management
│   └── users.py          # User profile management
│
├── services/             # Business logic services
│   ├── ai_service.py     # Multi-provider AI integration
│   ├── intasend_service.py # M-Pesa payment gateway
│   ├── multi_ai_service.py # AI provider orchestration
│   └── recipe_service.py # Recipe processing and validation
│
├── static/               # Frontend assets
│   ├── css/
│   │   ├── auth-styles.css # Authentication modal styles
│   │   └── styles.css    # Main application styles
│   └── js/
│       └── modules.js    # Modular JavaScript application
│
├── templates/            # Jinja2 HTML templates
│   └── index.html        # Single-page application template
│
├── mobile-app/           # React Native mobile application
│   ├── src/              # Source code
│   ├── App.tsx           # Main application component
│   └── package.json      # Dependencies and scripts
│
├── tests/                # Test suite
│   └── test_integrations.py # Integration tests
│
├── scripts/              # Utility scripts
│   └── run.py            # Development server launcher
│
├── docs/                 # Comprehensive documentation
│   ├── API_DOCUMENTATION.md # REST API reference
│   ├── DEPLOYMENT_GUIDE.md  # Production deployment
│   ├── FRONTEND_ARCHITECTURE.md # Frontend architecture
│   └── README.md         # Additional documentation
│
├── examples/             # Example implementations
│   └── demo_ai_payments.py # Payment integration demo
│
└── utils/                # Utility functions
    ├── __init__.py
    └── security.py       # Security utilities
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **MongoDB Atlas** account (free tier available)
- **API Keys** for AI providers (OpenAI, Gemini, etc.)
- **IntaSend** account for M-Pesa payments

### Installation

1. **Clone and navigate:**
   ```bash
   git clone <repository-url>
   cd ke-rouma
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   - **Web App**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc

## ⚙️ Configuration

### Required Environment Variables

```bash
# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database
DATABASE_NAME=your_database_name

# AI Provider API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key
HUGGINGFACE_API_KEY=hf-your-huggingface-key
COHERE_API_KEY=your-cohere-key

# Payment Gateway (for premium features)
INTASEND_PUBLISHABLE_KEY=ISPubKey_test_your_key
INTASEND_SECRET_KEY=ISSecretKey_test_your_key
INTASEND_BASE_URL=https://sandbox.intasend.com/api/v1

# Security
JWT_SECRET_KEY=your-256-bit-secret-key
DEBUG=true
```

### Optional Configuration

```bash
# Application Settings
PREMIUM_PRICE=299  # Price in KES
DEBUG=true
```

## 🔧 Development

### Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Backend** | FastAPI | 0.115+ | High-performance REST API framework |
| **Database** | MongoDB Atlas | Latest | Cloud NoSQL database with auto-scaling |
| **AI Integration** | Multi-provider | Latest | OpenAI GPT-4, Google Gemini, Cohere |
| **Payments** | IntaSend | Latest | M-Pesa payment gateway integration |
| **Frontend** | Vanilla ES6+ | Modern | Single-page application with modules |
| **Styling** | CSS3 + Animations | Latest | Glassmorphism design with custom fonts |
| **Typography** | Google Fonts | Latest | Inter, Playfair Display, Nunito |
| **Icons** | Font Awesome | 6.5+ | Consistent iconography |
| **Mobile** | React Native | Latest | Cross-platform mobile application |

### Interactive Features

#### 🎯 Microinstructions System
- **Contextual Hints**: Smart tooltips that appear when users need guidance
- **Progressive Disclosure**: Information revealed gradually to avoid overwhelming users
- **Action Anticipation**: UI elements that predict and suggest next actions
- **Visual Feedback**: Immediate response to user interactions with animations

#### 🎨 Animation System
- **Hover Effects**: Smooth transitions on interactive elements
- **Loading States**: Skeleton screens and progress indicators
- **Page Transitions**: Smooth navigation between sections
- **Micro-interactions**: Subtle animations that enhance user experience

#### 📱 Responsive Interactions
- **Touch Gestures**: Swipe and tap interactions on mobile devices
- **Keyboard Navigation**: Full keyboard accessibility support
- **Voice Commands**: Speech recognition for hands-free operation
- **Gesture Recognition**: Advanced touch interactions

### Development Commands

```bash
# Run with auto-reload
python app.py

# Run tests
python -m pytest tests/ -v

# Format code
black . --line-length 88
isort .

# Type checking
mypy app.py routes/ models/

# API documentation
python -c "from app import app; print(app.openapi())"
```

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/recipes/generate` | POST | Generate AI recipes | Optional |
| `/api/auth/login` | POST | User authentication | No |
| `/api/auth/register` | POST | User registration | No |
| `/api/chat/send` | POST | AI chat interaction | Optional |
| `/api/payments/initiate` | POST | Start M-Pesa payment | Yes |
| `/api/recipes/saved` | GET/POST | Manage saved recipes | Yes |

### Example API Usage

```python
import requests

# Generate recipes
response = requests.post('http://localhost:8000/api/recipes/generate', json={
    'ingredients': ['chicken', 'rice', 'onions'],
    'mood': 'comfort',
    'cuisine_type': 'African',
    'serving_size': 4
})

# Chat with AI assistant
response = requests.post('http://localhost:8000/api/chat/send', json={
    'message': 'How do I make ugali?'
})
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_integrations.py -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Test configuration and fixtures
├── test_auth.py          # Authentication tests
├── test_recipes.py       # Recipe generation tests
├── test_payments.py      # Payment integration tests
└── test_integrations.py  # End-to-end integration tests
```

## 📱 Mobile App

### Setup

```bash
cd mobile-app
npm install
npx expo install
```

### Development

```bash
# Start development server
npx expo start

# Run on specific platform
npx expo start --ios
npx expo start --android

# Build for production
npx expo build:android
npx expo build:ios
```

### Mobile Features

- **Offline Recipe Access**: Download recipes for offline viewing
- **Voice Cooking Assistant**: Hands-free cooking instructions
- **Smart Shopping Lists**: Auto-generated shopping lists
- **Recipe Sharing**: Share recipes via social media
- **Push Notifications**: Cooking timers and recipe recommendations

## 🚀 Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t ke-rouma .

# Run with Docker Compose
docker-compose up -d

# Scale the application
docker-compose up -d --scale app=3
```

### Production Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Use production MongoDB cluster
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Set up CI/CD pipeline

## 🌐 Browser Compatibility

### Supported Browsers
- **Chrome**: 90+ (recommended)
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile Safari**: iOS 14+
- **Chrome Mobile**: Android 90+

### Required Browser Features
- **ES6 Modules**: Modern JavaScript support
- **CSS Grid & Flexbox**: Responsive layout support
- **Web Animations API**: Smooth animations
- **Fetch API**: Modern HTTP requests
- **Local Storage**: User preferences and session data
- **Notification API**: Cooking timer notifications

## ⚡ Performance Optimization

### Frontend Performance
- **Lazy Loading**: Components load on demand
- **Image Optimization**: Compressed assets and WebP format
- **CSS Optimization**: Minified styles with critical CSS inlining
- **JavaScript Bundling**: Modular loading with code splitting
- **Caching Strategy**: Service worker for offline functionality

### Backend Performance
- **Async Operations**: Non-blocking I/O with FastAPI
- **Database Indexing**: Optimized MongoDB queries
- **Caching Layer**: Redis for frequently accessed data
- **Rate Limiting**: API protection and fair usage
- **Connection Pooling**: Efficient database connections

## 🐛 Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep fastapi

# Check environment variables
python -c "import os; print(os.getenv('MONGODB_URL'))"
```

**Frontend not loading:**
```bash
# Check browser console for JavaScript errors
# Verify static files are being served
curl http://localhost:8000/static/css/styles.css

# Clear browser cache and cookies
# Try incognito/private browsing mode
```

**Database connection fails:**
```bash
# Test MongoDB connection
python -c "from models.database import init_db; init_db()"

# Check network connectivity to MongoDB Atlas
ping cluster0.xxxxx.mongodb.net
```

**AI services not working:**
```bash
# Check API keys
python -c "import os; print('OPENAI_KEY:', bool(os.getenv('OPENAI_API_KEY')))"

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Payment integration issues:**
```bash
# Verify IntaSend configuration
python -c "from services.intasend_service import IntaSendService; print('Config valid')"

# Check M-Pesa test credentials
curl -X GET https://sandbox.intasend.com/api/v1/wallets/ -H "Authorization: Bearer $INTASEND_SECRET_KEY"
```

**Chat assistant not responding:**
```bash
# Check browser console for JavaScript errors
# Verify AI service API keys are configured
# Check network connectivity to AI providers
```

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python app.py
```

### Performance Troubleshooting

**Slow page loads:**
- Check browser developer tools network tab
- Verify CDN connectivity for external resources
- Check server response times
- Monitor database query performance

**High memory usage:**
- Monitor browser task manager
- Check for memory leaks in JavaScript
- Verify image optimization
- Clear browser cache periodically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure mobile compatibility for frontend changes
- Test payment flows thoroughly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **African Culinary Heritage**: Celebrating the rich diversity of African cuisine
- **AI Innovation**: Leveraging cutting-edge AI for culinary creativity
- **Open Source Community**: Building upon the shoulders of giants
- **Cultural Preservation**: Documenting and sharing traditional recipes

---

**Made with ❤️ for African cuisine lovers worldwide**
