# Frontend Architecture Documentation

## Overview

KE-ROUMA's frontend is built with a modern modular JavaScript architecture that emphasizes clean separation of concerns, maintainability, and scalability. The application uses vanilla JavaScript with ES6+ modules, custom CSS with modern design patterns, and a responsive mobile-first approach.

## Architecture Principles

### 1. Modular Design
- **Separation of Concerns**: Each module handles a specific domain of functionality
- **Single Responsibility**: Modules have one clear purpose and responsibility
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together

### 2. State Management
- **Centralized State**: `AppState` module manages global application state
- **Persistent Storage**: Important state persisted to localStorage
- **Event-Driven Updates**: State changes trigger UI updates through events

### 3. Error Handling
- **Graceful Degradation**: Features fail gracefully with user feedback
- **Consistent Error UI**: Standardized error notifications and handling
- **Recovery Mechanisms**: Users can retry failed operations

## Module Structure

### Core Modules

#### AppState
**Purpose**: Centralized state management and persistence
```javascript
const AppState = {
    user: null,
    authToken: null,
    selectedIngredients: [],
    selectedMood: null,
    // ... other state properties
}
```

**Responsibilities**:
- Manage global application state
- Handle localStorage persistence
- Provide state access methods
- Trigger state change events

#### NavigationManager
**Purpose**: Page routing and navigation
```javascript
const NavigationManager = {
    currentPage: 'home',
    showPage(pageId) { /* ... */ },
    init() { /* ... */ }
}
```

**Responsibilities**:
- Handle page transitions
- Manage navigation state
- Initialize page-specific modules
- Handle keyboard shortcuts

#### UIManager
**Purpose**: User interface interactions and feedback
```javascript
const UIManager = {
    showNotification(message, type) { /* ... */ },
    showLoading(show) { /* ... */ },
    updateAuthUI() { /* ... */ }
}
```

**Responsibilities**:
- Display notifications and alerts
- Manage loading states
- Handle UI state updates
- Provide user feedback

#### ModalManager
**Purpose**: Modal dialog management
```javascript
const ModalManager = {
    openModal(modalId) { /* ... */ },
    closeModal(modalId) { /* ... */ },
    init() { /* ... */ }
}
```

**Responsibilities**:
- Open and close modals
- Handle modal events
- Manage modal state
- Handle overlay interactions

### Feature Modules

#### AuthManager
**Purpose**: User authentication and authorization
```javascript
const AuthManager = {
    async login() { /* ... */ },
    async register() { /* ... */ },
    logout() { /* ... */ }
}
```

**Features**:
- User login and registration
- Token management
- Authentication state updates
- Error handling for auth failures

#### RecipeManager
**Purpose**: Recipe generation, display, and management
```javascript
const RecipeManager = {
    currentRecipes: [],
    async generateRecipe() { /* ... */ },
    displayRecipes(recipes) { /* ... */ },
    createRecipeCard(recipe, index) { /* ... */ }
}
```

**Features**:
- AI recipe generation with progress tracking
- Enhanced recipe card display with ratings and nutrition
- Recipe saving and sharing
- Recipe detail modal with cooking mode integration

#### GenerateModule
**Purpose**: Recipe generation interface and ingredient management
```javascript
const GenerateModule = {
    addIngredient() { /* ... */ },
    removeIngredient(ingredient) { /* ... */ },
    selectMood(mood) { /* ... */ }
}
```

**Features**:
- Ingredient input and management
- Mood selection interface
- Category-based ingredient selection
- Camera integration for ingredient recognition

#### KitchenModule
**Purpose**: Cooking mode and step-by-step guidance
```javascript
const KitchenModule = {
    currentRecipe: null,
    currentStep: 0,
    startCookingMode(recipe) { /* ... */ },
    nextStep() { /* ... */ }
}
```

**Features**:
- Step-by-step cooking guidance
- Progress tracking
- Timer integration
- Cooking interface with navigation

#### ChatManager
**Purpose**: AI chat functionality
```javascript
const ChatManager = {
    toggle() { /* ... */ },
    sendMessage() { /* ... */ },
    displayMessage(message, isUser) { /* ... */ }
}
```

**Features**:
- Real-time chat interface
- Message history
- Typing indicators
- AI response handling

#### VoiceManager
**Purpose**: Voice recognition and control
```javascript
const VoiceManager = {
    isListening: false,
    startListening() { /* ... */ },
    stopListening() { /* ... */ }
}
```

**Features**:
- Speech recognition
- Voice commands processing
- Audio feedback
- Microphone access management

#### PaymentManager
**Purpose**: M-Pesa payment processing
```javascript
const PaymentManager = {
    initialize() { /* ... */ },
    processPayment() { /* ... */ },
    checkPaymentStatus(checkoutId) { /* ... */ }
}
```

**Features**:
- Payment initialization
- M-Pesa integration
- Payment status tracking
- Error handling for payment failures

### Page Modules

#### HomeModule
**Purpose**: Home page functionality
- Quick actions and shortcuts
- Health tips display
- Recent activity
- Navigation to other sections

#### DiscoverModule
**Purpose**: Recipe discovery and browsing
- Featured recipes
- Recipe categories
- Search functionality
- Trending recipes

#### SavedModule
**Purpose**: Saved recipes management
- User's saved recipes
- Recipe organization
- Favorites management
- Recipe collections

#### PremiumModule
**Purpose**: Premium features and subscription
- Premium feature showcase
- Subscription management
- Payment integration
- Feature comparisons

## CSS Architecture

### Design System

#### Custom Properties (CSS Variables)
```css
:root {
    /* Colors */
    --primary-color: #2e7d32;
    --secondary-color: #ff9800;
    --accent-color: #4caf50;
    
    /* Typography */
    --font-primary: 'Inter', sans-serif;
    --font-heading: 'Poppins', sans-serif;
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    
    /* Shadows */
    --shadow-small: 0 2px 4px rgba(0,0,0,0.1);
    --shadow-medium: 0 4px 12px rgba(0,0,0,0.15);
}
```

#### Component-Based Styling
- **Modular CSS**: Each component has its own CSS section
- **BEM Methodology**: Block-Element-Modifier naming convention
- **Responsive Design**: Mobile-first approach with breakpoints
- **Accessibility**: WCAG 2.1 AA compliance

### Layout System

#### CSS Grid and Flexbox
- **Grid**: Used for main layout structure and recipe cards
- **Flexbox**: Used for component-level layouts and alignment
- **Responsive**: Adaptive layouts for different screen sizes

#### Component Patterns
```css
/* Card Pattern */
.card {
    background: var(--card-background);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-medium);
    padding: var(--spacing-lg);
}

/* Button Pattern */
.btn {
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--border-radius);
    font-weight: 600;
    transition: all 0.3s ease;
}
```

## API Integration

### Fetch API Usage
```javascript
// Standardized API calls with error handling
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AppState.authToken}`,
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        UIManager.showNotification('Network error. Please try again.', 'error');
        throw error;
    }
}
```

### Error Handling Strategy
1. **Network Errors**: Graceful degradation with retry options
2. **Authentication Errors**: Automatic token refresh or re-login
3. **Validation Errors**: User-friendly error messages
4. **Server Errors**: Fallback to cached data when possible

## Performance Optimizations

### Code Splitting
- **Lazy Loading**: Modules loaded only when needed
- **Dynamic Imports**: Features loaded on demand
- **Resource Optimization**: Images and assets optimized for web

### Caching Strategy
- **LocalStorage**: User preferences and recent data
- **Service Worker**: Offline functionality (planned)
- **Browser Cache**: Static assets with proper cache headers

### Memory Management
- **Event Cleanup**: Proper event listener removal
- **DOM Cleanup**: Efficient DOM manipulation
- **State Cleanup**: Proper state reset on navigation

## Development Guidelines

### Code Standards
- **ES6+ Features**: Modern JavaScript syntax and features
- **Async/Await**: Promise-based asynchronous programming
- **Error Boundaries**: Comprehensive error handling
- **Type Safety**: JSDoc comments for type hints

### Testing Strategy
- **Unit Tests**: Individual module testing
- **Integration Tests**: Module interaction testing
- **E2E Tests**: Full user journey testing
- **Performance Tests**: Load and stress testing

### Accessibility
- **Semantic HTML**: Proper HTML5 semantic elements
- **ARIA Labels**: Screen reader compatibility
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG AA compliance

## Future Enhancements

### Planned Improvements
1. **TypeScript Migration**: Gradual migration to TypeScript
2. **Service Workers**: Offline functionality and caching
3. **Web Components**: Custom element creation
4. **Progressive Web App**: PWA features and installation
5. **Performance Monitoring**: Real-time performance tracking

### Scalability Considerations
- **Module Federation**: Micro-frontend architecture
- **State Management**: Consider Redux or Zustand for complex state
- **Build Tools**: Webpack or Vite for advanced bundling
- **Testing Framework**: Jest and Testing Library integration

## Conclusion

The KE-ROUMA frontend architecture provides a solid foundation for a modern, maintainable, and scalable web application. The modular design allows for easy feature additions and modifications while maintaining code quality and user experience standards.
