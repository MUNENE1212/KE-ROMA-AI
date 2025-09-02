# KE-ROUMA - African Heritage Recipe Recommendation App

🍽️ **KE-ROUMA** (formerly AfyaBite) is a modern web and mobile application that celebrates African culinary heritage while promoting healthy eating through AI-powered recipe recommendations.

## 🌟 Features

### Core Features
- **AI Recipe Generation**: Get authentic African recipes in 30 seconds based on your pantry ingredients
- **Interactive Web Interface**: Modern, responsive web application with modular architecture
- **Smart Camera Integration**: AI-powered ingredient recognition through camera
- **Voice Control**: Generate recipes and control app through voice commands
- **Mood-Based Recipes**: Personalized recipes based on your current mood and health goals
- **Real-Time Recipe Streaming**: Watch AI generate recipes step-by-step with live progress
- **Cooking Mode**: Step-by-step guided cooking with timers and progress tracking
- **Premium Subscriptions**: Enhanced features with M-Pesa payment integration

### Advanced Features
- **Predictive Suggestions**: Context-aware recipe recommendations based on time and ingredients
- **Smart Ingredient Management**: Autocomplete and categorized ingredient selection
- **Recipe Rating System**: Community-driven recipe ratings and reviews
- **Nutrition Visualization**: Detailed nutritional information with health optimization
- **Recipe Sharing**: Share recipes via social media or copy to clipboard
- **Offline Functionality**: Access your saved recipes without internet connection

### Premium Features
- Unlimited recipe generations
- Advanced nutrition analysis and health insights
- Cultural context and traditional cooking techniques
- Meal planning calendar and shopping lists
- Priority customer support
- Enhanced AI features and faster generation

## 🏗️ Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.8+
- **Database**: MongoDB Atlas (NoSQL document storage)
- **AI Integration**: OpenAI GPT-4 API
- **Payment Processing**: IntaSend M-Pesa API
- **Deployment**: Google Cloud Run / Heroku

### Frontend (Modern Web App)
- **Architecture**: Modular JavaScript with ES6+ modules
- **UI Framework**: Vanilla JavaScript with custom CSS
- **Styling**: CSS3 with custom properties and modern layouts
- **State Management**: Centralized AppState with localStorage persistence
- **API Integration**: Fetch API with async/await
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox

### Mobile App (React Native)
- **Framework**: React Native with Expo SDK 53
- **Navigation**: React Navigation
- **Offline Storage**: WatermelonDB
- **State Management**: React Hooks
- **API Client**: Axios

## 🚀 Quick Start

### Backend Setup

1. **Clone and navigate to project**:
   ```bash
   cd /home/munen/PLP/hack2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

4. **Start the FastAPI server**:
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`
   - Web Interface: `http://localhost:8000`
   - Interactive API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Mobile App Setup

1. **Navigate to mobile app directory**:
   ```bash
   cd mobile-app
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start Expo development server**:
   ```bash
   npm start
   ```

4. **Run on device**:
   - Install Expo Go app on your phone
   - Scan QR code from terminal
   - Or use `npm run android` / `npm run ios`

## 📁 Project Structure

```
hack2/
├── app.py                 # FastAPI main application
├── run.py                 # Application runner
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── config/
│   └── config.py         # Application configuration
├── models/
│   ├── database.py       # MongoDB connection and setup
│   ├── schemas.py        # Pydantic data models
│   └── user.py          # User service layer
├── routes/
│   ├── main.py          # Health check and info endpoints
│   ├── auth.py          # Authentication endpoints
│   ├── chat.py          # AI chat functionality
│   ├── payments.py      # M-Pesa payment processing
│   └── users.py         # User management
├── services/
│   ├── ai_service.py    # OpenAI integration
│   ├── multi_ai_service.py # Multi-provider AI service
│   ├── recipe_service.py # Recipe database operations
│   └── intasend_service.py # Payment processing
├── static/              # Frontend assets
│   ├── css/
│   │   ├── styles.css   # Main stylesheet with modular design
│   │   └── auth-styles.css # Authentication styles
│   └── js/
│       └── app.js       # Modular JavaScript application
├── templates/
│   └── index.html       # Modern web interface
└── mobile-app/          # React Native mobile application
    ├── App.tsx          # Main app component
    ├── package.json     # Node.js dependencies
    └── src/
        ├── screens/     # App screens
        ├── services/    # API integration
        ├── types/       # TypeScript interfaces
        └── components/  # Reusable components
```

## 🔧 Configuration

### Required Environment Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=kerouma

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# IntaSend Payment Gateway
INTASEND_PUBLISHABLE_KEY=your_intasend_publishable_key
INTASEND_SECRET_KEY=your_intasend_secret_key
INTASEND_BASE_URL=https://sandbox.intasend.com/api/v1

# App Settings
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
PREMIUM_PRICE=100
```

## 📱 API Endpoints

### Recipe Endpoints
- `POST /api/recipes/generate` - Generate AI recipes
- `GET /api/recipes/saved/{user_id}` - Get saved recipes
- `POST /api/recipes/save/{recipe_id}` - Save a recipe
- `DELETE /api/recipes/saved/{recipe_id}` - Remove saved recipe
- `GET /api/recipes/search` - Search recipes

### User Endpoints
- `POST /api/users/` - Create user
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/phone/{phone_number}` - Get user by phone
- `PUT /api/users/{user_id}` - Update user
- `GET /api/users/{user_id}/premium-status` - Check premium status

### Payment Endpoints
- `POST /api/payments/initiate` - Initiate M-Pesa payment
- `GET /api/payments/status/{checkout_id}` - Check payment status
- `GET /api/payments/history/{user_id}` - Get payment history

## 🎯 Development Roadmap

### Phase 1: MVP (Completed ✅)
- ✅ FastAPI backend with MongoDB
- ✅ AI recipe generation with OpenAI GPT-4
- ✅ Modern modular web interface
- ✅ React Native mobile app
- ✅ M-Pesa payment integration
- ✅ User management and authentication
- ✅ Smart camera integration for ingredient recognition
- ✅ Voice control and commands
- ✅ Mood-based recipe generation
- ✅ Real-time recipe streaming
- ✅ Step-by-step cooking mode
- ✅ Recipe rating and sharing system
- ✅ Nutrition visualization

### Phase 2: Enhancement (In Progress)
- ✅ Recipe sharing and community features
- ✅ Advanced UI/UX with responsive design
- [ ] WatermelonDB offline storage
- [ ] Push notifications
- [ ] Advanced search and filtering
- [ ] Meal planning calendar
- [ ] Recipe collections and favorites

### Phase 3: Scale (Planned)
- [ ] WhatsApp bot integration (Twilio)
- [ ] Multi-language support (Swahili, French, Arabic)
- [ ] Regional cuisine variations
- [ ] Nutritionist partnerships
- [ ] Grocery delivery integration
- [ ] Social features and recipe communities

## 🧪 Testing

### Backend Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test recipe generation (requires OpenAI API key)
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"pantry_ingredients": ["rice", "beans", "tomatoes"]}'
```

### Mobile App Testing
- Use Expo Go for quick testing
- Test on both iOS and Android devices
- Verify offline functionality
- Test payment flow (sandbox mode)

## 🌍 Deployment

### Backend Deployment (Google Cloud Run)
```bash
# Build and deploy
gcloud run deploy kerouma-api \
  --source . \
  --platform managed \
  --region africa-south1 \
  --allow-unauthenticated
```

### Mobile App Deployment
```bash
# Build for production
expo build:android
expo build:ios

# Submit to app stores
expo submit:android
expo submit:ios
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@kerouma.com or join our community Discord.

---

**KE-ROUMA** - Celebrating African culinary heritage through technology 🌍
