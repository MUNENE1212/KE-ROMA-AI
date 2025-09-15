// KE-ROUMA Core Application - Streamlined Version
// ================================================

// Global Variables
let chatOpen = false;

// Application State
const AppState = {
    currentPage: 'home',
    selectedIngredients: [],
    selectedMood: null,
    currentUser: null,
    
    init() {
        const userData = localStorage.getItem('ke_rouma_user');
        if (userData) {
            try {
                this.currentUser = JSON.parse(userData);
            } catch (error) {
                localStorage.removeItem('ke_rouma_user');
            }
        }
    },
    
    setUser(user) {
        this.currentUser = user;
        localStorage.setItem('ke_rouma_user', JSON.stringify(user));
    },
    
    clearUser() {
        this.currentUser = null;
        localStorage.removeItem('ke_rouma_user');
    }
};

// API Configuration
const API_BASE = window.location.origin;
const API_ENDPOINTS = {
    auth: {
        login: '/api/auth/login',
        register: '/api/auth/register'
    },
    recipes: {
        generate: '/api/recipes/generate'
    },
    chat: {
        send: '/api/chat/send'
    },
    payments: {
        initiate: '/api/payments/initiate',
        status: '/api/payments/status'
    }
};

// API Helper
async function apiCall(endpoint, options = {}) {
    try {
        const token = localStorage.getItem('access_token') || AppState.currentUser?.token;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && {
                    'Authorization': `Bearer ${token}`
                })
            },
            ...options
        };
        
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        const response = await fetch(API_BASE + endpoint, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Navigation Management
const Navigation = {
    init() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.showPage(page);
            });
        });
    },
    
    showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page-module').forEach(page => {
            page.classList.remove('active');
        });
        
        // Update nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Show selected page
        const targetPage = document.getElementById(pageId);
        const targetLink = document.querySelector(`[data-page="${pageId}"]`);
        
        if (targetPage && targetLink) {
            targetPage.classList.add('active');
            targetLink.classList.add('active');
            AppState.currentPage = pageId;
            
            // Initialize page-specific functionality
            if (pageId === 'generate') {
                RecipeGenerator.init();
            } else if (pageId === 'saved') {
                loadSavedRecipes();
            }
        }
    }
};

// Global navigation function for HTML onclick
window.showPage = (pageId) => Navigation.showPage(pageId);

// Recipe Generator Module
const RecipeGenerator = {
    ingredientDatabase: {
        vegetables: ['Tomatoes', 'Onions', 'Carrots', 'Spinach', 'Kale', 'Sukuma Wiki', 'Cabbage', 'Bell Peppers'],
        proteins: ['Chicken', 'Beef', 'Fish', 'Beans', 'Lentils', 'Eggs'],
        grains: ['Rice', 'Maize', 'Wheat', 'Millet', 'Sorghum'],
        spices: ['Ginger', 'Garlic', 'Cumin', 'Coriander', 'Turmeric']
    },
    
    init() {
        this.setupMoodSelector();
        this.setupIngredientSelection();
        this.updateIngredientDisplay();
        
        // Initialize ingredients display on page load
        setTimeout(() => {
            this.showIngredientCategory('vegetables');
        }, 100);
    },
    
    setupMoodSelector() {
        const moodOptions = document.querySelectorAll('.mood-option');
        moodOptions.forEach(option => {
            option.addEventListener('click', () => {
                const mood = option.getAttribute('data-mood');
                this.setMood(mood);
            });
        });
    },
    
    setMood(mood) {
        document.querySelectorAll('.mood-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelector(`[data-mood="${mood}"]`)?.classList.add('selected');
        AppState.selectedMood = mood;
        
        const feedback = document.getElementById('moodFeedback');
        if (feedback) {
            const messages = {
                energetic: "Great! I'll suggest vibrant, energizing recipes.",
                comfort: "Perfect! Let's find some hearty, soul-warming dishes.",
                adventurous: "Exciting! I'll recommend bold flavors and unique combinations.",
                healthy: "Excellent choice! Focusing on nutritious, balanced meals.",
                quick: "Got it! Quick and easy recipes coming up."
            };
            feedback.textContent = messages[mood] || '';
            feedback.style.display = 'block';
        }
    },
    
    setupIngredientSelection() {
        this.showIngredientCategory('vegetables');
        
        const tabs = document.querySelectorAll('.category-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const category = tab.getAttribute('data-category');
                this.showIngredientCategory(category);
            });
        });
    },
    
    showIngredientCategory(category) {
        document.querySelectorAll('.category-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelector(`[data-category="${category}"]`)?.classList.add('active');
        
        const container = document.getElementById('ingredientOptions');
        if (container && this.ingredientDatabase[category]) {
            container.innerHTML = this.ingredientDatabase[category].map(ingredient => {
                const isSelected = AppState.selectedIngredients.includes(ingredient);
                return `<div class="ingredient-option ${isSelected ? 'selected' : ''}" onclick="RecipeGenerator.toggleIngredient('${ingredient}')">${ingredient}</div>`;
            }).join('');
        }
    },
    
    toggleIngredient(ingredient) {
        const index = AppState.selectedIngredients.indexOf(ingredient);
        if (index > -1) {
            AppState.selectedIngredients.splice(index, 1);
            showNotification(`Removed ${ingredient}`, 'info');
        } else {
            AppState.selectedIngredients.push(ingredient);
            showNotification(`Added ${ingredient}`, 'success');
        }
        this.updateIngredientDisplay();
        this.showIngredientCategory(document.querySelector('.category-tab.active')?.getAttribute('data-category') || 'vegetables');
    },
    
    updateIngredientDisplay() {
        const container = document.getElementById('ingredientTags');
        if (container) {
            if (AppState.selectedIngredients.length === 0) {
                container.innerHTML = '<p class="empty-state">No ingredients selected yet.</p>';
            } else {
                container.innerHTML = AppState.selectedIngredients.map(ingredient => 
                    `<span class="ingredient-tag">${ingredient}<button onclick="RecipeGenerator.toggleIngredient('${ingredient}')" class="remove-tag">×</button></span>`
                ).join('');
            }
        }
    },
    
    async generateRecipes() {
        if (AppState.selectedIngredients.length === 0) {
            showNotification('Please select at least one ingredient', 'warning');
            return;
        }

        const generateBtn = document.querySelector('button[onclick="generateRecipes()"]');
        if (generateBtn) {
            generateBtn.classList.add('loading');
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        }

        try {
            const requestData = {
                ingredients: AppState.selectedIngredients,
                dietary_restrictions: AppState.selectedMood ? [AppState.selectedMood] : [],
                user_id: AppState.currentUser?.id || null,
                mood: AppState.selectedMood,
                cuisine_type: 'African',
                serving_size: 4
            };

            const response = await apiCall(API_ENDPOINTS.recipes.generate, {
                method: 'POST',
                body: requestData
            });

            if (response.recipes && response.recipes.length > 0) {
                // For guest users, only show 1 recipe with login prompt
                const recipesToShow = AppState.currentUser ? response.recipes : response.recipes.slice(0, 1);
                this.displayRecipes(recipesToShow, !AppState.currentUser);
                
                const count = AppState.currentUser ? response.recipes.length : 1;
                showNotification(`Generated ${count} recipe${count > 1 ? 's' : ''}!`, 'success');
                
                if (!AppState.currentUser && response.recipes.length > 1) {
                    setTimeout(() => {
                        showNotification(`${response.recipes.length - 1} more recipes available! Login to view all.`, 'info');
                    }, 2000);
                }
            } else {
                throw new Error('No recipes generated');
            }

        } catch (error) {
            console.error('Recipe generation failed:', error);
            console.error('Error details:', error.message);
            console.error('Selected ingredients:', AppState.selectedIngredients);
            console.error('Request data that was sent:', requestData);
            
            // Check if ingredients array is empty
            if (!AppState.selectedIngredients || AppState.selectedIngredients.length === 0) {
                showNotification('Please select ingredients first before generating recipes', 'warning');
            } else {
                showNotification(`Failed to generate recipes: ${error.message}. Please try again.`, 'error');
            }
        } finally {
            if (generateBtn) {
                generateBtn.classList.remove('loading');
                generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Recipes';
            }
        }
    },
    
    displayRecipes(recipes, isGuest = false) {
        const container = document.querySelector('#generate .module-card');
        if (!container) return;
        
        let resultsHtml = '<div class="recipe-results"><h3><i class="fas fa-magic"></i> Your AI-Generated Recipes</h3>';
        
        if (isGuest && recipes.length === 1) {
            resultsHtml += '<div class="guest-notice"><p><i class="fas fa-info-circle"></i> Guest preview - Login to generate unlimited recipes!</p></div>';
        }
        
        resultsHtml += '<div class="recipe-grid">';
        
        recipes.forEach((recipe, index) => {
            resultsHtml += `
                <div class="recipe-card">
                    <div class="recipe-card-content">
                        <div class="recipe-header">
                            <h4>${recipe.name}</h4>
                            <span class="recipe-origin">${recipe.cuisine || 'African'}</span>
                        </div>
                        <div class="recipe-meta">
                            <span><i class="fas fa-clock"></i> ${recipe.prep_time || '30'} mins</span>
                            <span><i class="fas fa-users"></i> ${recipe.servings || '4'} servings</span>
                        </div>
                        <p>${recipe.description || 'A delicious AI-generated recipe tailored to your preferences.'}</p>
                        <div class="recipe-actions">
                            <button class="btn-primary" onclick="viewRecipe(${index})">
                                <i class="fas fa-eye"></i> View Recipe
                            </button>
                            ${AppState.currentUser ? `<button class="btn-outline" onclick="saveRecipe(${index})"><i class="fas fa-bookmark"></i> Save</button>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (isGuest) {
            resultsHtml += `
                <div class="recipe-card login-prompt">
                    <div class="recipe-card-content">
                        <div class="login-prompt-content">
                            <h4><i class="fas fa-lock"></i> More Recipes Available</h4>
                            <p>Login or register to generate unlimited AI recipes and save your favorites!</p>
                            <div class="recipe-actions">
                                <button class="btn-primary" onclick="Auth.showLoginModal()">
                                    <i class="fas fa-sign-in-alt"></i> Login
                                </button>
                                <button class="btn-outline" onclick="Auth.showRegisterModal()">
                                    <i class="fas fa-user-plus"></i> Register
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        resultsHtml += '</div></div>';
        container.insertAdjacentHTML('beforeend', resultsHtml);
        
        // Store recipes globally for viewing
        window.currentRecipes = recipes;
    }
};

// Authentication Module
const Auth = {
    showLoginModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <div class="auth-form">
                    <h2>Login to KE-ROUMA</h2>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="loginPhone">Phone Number:</label>
                            <input type="tel" id="loginPhone" placeholder="254799954672" required>
                        </div>
                        <div class="form-group">
                            <label for="loginPassword">Password:</label>
                            <input type="password" id="loginPassword" required>
                        </div>
                        <button type="submit" class="btn-primary">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </button>
                    </form>
                    <p>Don't have an account? <a href="#" onclick="this.parentElement.parentElement.parentElement.remove(); Auth.showRegisterModal();">Register here</a></p>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.querySelector('#loginForm').addEventListener('submit', Auth.handleLogin.bind(Auth));
    },

    showRegisterModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                <div class="auth-form">
                    <h2>Join KE-ROUMA</h2>
                    <form id="registerForm">
                        <div class="form-group">
                            <label for="registerUsername">Username:</label>
                            <input type="text" id="registerUsername" required>
                        </div>
                        <div class="form-group">
                            <label for="registerPhone">Phone Number:</label>
                            <input type="tel" id="registerPhone" placeholder="254799954672" required>
                        </div>
                        <div class="form-group">
                            <label for="registerPassword">Password:</label>
                            <input type="password" id="registerPassword" required>
                        </div>
                        <button type="submit" class="btn-primary">
                            <i class="fas fa-user-plus"></i> Register
                        </button>
                    </form>
                    <p>Already have an account? <a href="#" onclick="this.parentElement.parentElement.parentElement.remove(); Auth.showLoginModal();">Login here</a></p>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.querySelector('#registerForm').addEventListener('submit', Auth.handleRegister.bind(Auth));
    },

    async handleLogin(event) {
        event.preventDefault();
        const phone_number = document.getElementById('loginPhone').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const response = await apiCall(API_ENDPOINTS.auth.login, {
                method: 'POST',
                body: { phone_number, password }
            });
            
            AppState.setUser(response.user);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
            updateAuthUI();
            showNotification('Login successful!', 'success');
            document.querySelector('.modal').remove();
            
        } catch (error) {
            showNotification(`Login failed: ${error.message}`, 'error');
        }
    },

    async handleRegister(event) {
        event.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const phone_number = document.getElementById('registerPhone').value;
        const password = document.getElementById('registerPassword').value;
        
        try {
            const response = await apiCall(API_ENDPOINTS.auth.register, {
                method: 'POST',
                body: { username, phone_number, password }
            });
            
            AppState.setUser(response.user);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
            updateAuthUI();
            showNotification('Registration successful!', 'success');
            document.querySelector('.modal').remove();
            
        } catch (error) {
            showNotification(`Registration failed: ${error.message}`, 'error');
        }
    },

    logout() {
        AppState.clearUser();
        updateAuthUI();
        showNotification('Logged out successfully', 'info');
    }
};

// Floating Icons Animation
function createFloatingIcons() {
    const floatingContainer = document.querySelector('.floating-icons');
    if (!floatingContainer) return;
    
    const icons = ['🍽️', '🥘', '🍲', '🥗', '🍛', '🥙', '🌶️', '🧄', '🧅', '🥕'];
    
    for (let i = 0; i < 15; i++) {
        const icon = document.createElement('div');
        icon.className = 'floating-icon';
        icon.textContent = icons[Math.floor(Math.random() * icons.length)];
        
        // Random positioning
        icon.style.left = Math.random() * 100 + '%';
        icon.style.top = Math.random() * 100 + '%';
        icon.style.animationDelay = Math.random() * 20 + 's';
        icon.style.animationDuration = (15 + Math.random() * 10) + 's';
        
        floatingContainer.appendChild(icon);
    }
}

// Chat Functions
// function toggleChat() {
  //  const chatWindow = document.querySelector('.chat-window');
  //  if (chatWindow) {
   //     const isVisible = chatWindow.style.display === 'flex';
  //      chatWindow.style.display = isVisible ? 'none' : 'flex';
 //   }
// }
 // Enhanced chat functionality
 function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatOpen = !chatOpen;
    
    if (chatOpen) {
        chatWindow.style.display = 'flex';
        document.getElementById('chatInput').focus();
    } else {
        chatWindow.style.display = 'none';
    }
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.querySelector('.chat-messages');
    
    if (!chatInput || !chatMessages) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'chat-message user';
    userMessage.textContent = message;
    chatMessages.appendChild(userMessage);
    
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message ai typing';
    typingIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI is thinking...';
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        const response = await apiCall(API_ENDPOINTS.chat.send, {
            method: 'POST',
            body: { message }
        });
        
        typingIndicator.remove();
        
        const aiMessage = document.createElement('div');
        aiMessage.className = 'chat-message ai';
        aiMessage.textContent = response.response || 'Sorry, I could not process your request.';
        chatMessages.appendChild(aiMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
    } catch (error) {
        typingIndicator.remove();
        const errorMessage = document.createElement('div');
        errorMessage.className = 'chat-message ai error';
        errorMessage.textContent = 'Sorry, I encountered an error. Please try again.';
        chatMessages.appendChild(errorMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${icons[type] || icons.info}"></i>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 8px;
        color: white;
        z-index: 10000;
        max-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateAuthUI() {
    const authButtons = document.querySelector('.auth-buttons');
    if (authButtons) {
        if (AppState.currentUser) {
            authButtons.innerHTML = `
                <span style="color: white; margin-right: 1rem;">
                    <i class="fas fa-user"></i> Welcome, ${AppState.currentUser.username}!
                </span>
                <button class="btn-outline" onclick="Auth.logout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </button>
            `;
        } else {
            authButtons.innerHTML = `
                <button class="btn-outline" onclick="Auth.showLoginModal()">
                    <i class="fas fa-sign-in-alt"></i> Login
                </button>
                <button class="btn-primary" onclick="Auth.showRegisterModal()">
                    <i class="fas fa-user-plus"></i> Register
                </button>
            `;
        }
    }
}

// Recipe Viewing
function viewRecipe(index) {
    const recipe = window.currentRecipes?.[index];
    if (!recipe) {
        showNotification('Recipe not found', 'error');
        return;
    }
    
    const modal = document.getElementById('recipeModal');
    const detail = document.getElementById('recipeDetail');
    
    if (modal && detail) {
        // Clean recipe name (remove markdown formatting)
        const cleanName = recipe.name.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '');
        
        // Clean ingredients (filter out markdown and empty items)
        const cleanIngredients = recipe.ingredients
            .filter(ingredient => ingredient && ingredient.trim() !== '**' && ingredient.trim() !== '')
            .map(ingredient => ingredient.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '').replace(/^\*\s*/, ''));
        
        // Clean instructions (filter out markdown and empty items)
        const cleanInstructions = recipe.instructions
            .filter(instruction => instruction && instruction.trim() !== '**' && instruction.trim() !== '')
            .map(instruction => instruction.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, ''));
        
        // Clean health benefits
        const cleanHealthBenefits = recipe.health_benefits?.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '') || '';
        
        // Clean cultural context
        const cleanCulturalContext = recipe.cultural_context?.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '') || '';
        
        detail.innerHTML = `
            <div class="recipe-detail-content">
                <div class="recipe-header">
                    <h2>${cleanName}</h2>
                    <div class="recipe-meta">
                        <span><i class="fas fa-clock"></i> ${recipe.cooking_time || '30 mins'}</span>
                        <span><i class="fas fa-users"></i> ${recipe.servings || 4} servings</span>
                        <span><i class="fas fa-globe"></i> ${recipe.origin || 'African'}</span>
                    </div>
                </div>
                
                <div class="recipe-sections">
                    <div class="ingredients-section">
                        <h3><i class="fas fa-list"></i> Ingredients</h3>
                        <ul class="ingredients-list">
                            ${cleanIngredients.length > 0 ? cleanIngredients.map(ingredient => `<li>${ingredient}</li>`).join('') : '<li>No ingredients listed</li>'}
                        </ul>
                    </div>
                    
                    <div class="instructions-section">
                        <h3><i class="fas fa-tasks"></i> Instructions</h3>
                        <ol class="instructions-list">
                            ${cleanInstructions.length > 0 ? cleanInstructions.map(instruction => `<li>${instruction}</li>`).join('') : '<li>No instructions available</li>'}
                        </ol>
                    </div>
                    
                    ${cleanHealthBenefits ? `
                        <div class="health-benefits-section">
                            <h3><i class="fas fa-heart"></i> Health Benefits</h3>
                            <p>${cleanHealthBenefits}</p>
                        </div>
                    ` : ''}
                    
                    ${cleanCulturalContext ? `
                        <div class="cultural-context-section">
                            <h3><i class="fas fa-info-circle"></i> Cultural Context</h3>
                            <p>${cleanCulturalContext}</p>
                        </div>
                    ` : ''}
                </div>
                
                ${AppState.currentUser ? `
                    <div class="recipe-actions-modal">
                        <button class="btn-primary" onclick="saveRecipe(${index})">
                            <i class="fas fa-bookmark"></i> Save Recipe
                        </button>
                        <button class="btn-outline" onclick="shareRecipe(${index})">
                            <i class="fas fa-share"></i> Share
                        </button>
                    </div>
                ` : `
                    <div class="recipe-actions-modal">
                        <p style="text-align: center; margin: 1rem 0; color: var(--text-light);">
                            <i class="fas fa-info-circle"></i> Login to save and share recipes
                        </p>
                        <button class="btn-primary" onclick="Auth.showLoginModal(); closeRecipeModal();">
                            <i class="fas fa-sign-in-alt"></i> Login to Save
                        </button>
                    </div>
                `}
            </div>
        `;
        modal.style.display = 'block';
    } else {
        showNotification('Recipe modal not found', 'error');
    }
}

function closeRecipeModal() {
    const modal = document.getElementById('recipeModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Recipe Actions
async function saveRecipe(index) {
    if (!AppState.currentUser) {
        showNotification('Please login to save recipes', 'error');
        return;
    }
    
    const recipe = window.currentRecipes?.[index];
    if (!recipe) {
        showNotification('Recipe not found', 'error');
        return;
    }
    
    try {
        const recipeId = recipe._id || recipe.id;
        const response = await apiCall(`/api/recipes/save/${recipeId}?user_id=${AppState.currentUser.id}`, {
            method: 'POST'
        });
        
        showNotification('Recipe saved successfully!', 'success');
        
    } catch (error) {
        console.error('Save recipe failed:', error);
        showNotification('Failed to save recipe', 'error');
    }
}

function shareRecipe(index) {
    const recipe = window.currentRecipes?.[index];
    if (!recipe) {
        showNotification('Recipe not found', 'error');
        return;
    }
    
    const cleanName = recipe.name.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '');
    const shareText = `Check out this amazing ${cleanName} recipe from KE-ROUMA! 🍽️✨`;
    
    if (navigator.share) {
        navigator.share({
            title: `${cleanName} - KE-ROUMA`,
            text: shareText,
            url: window.location.href
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Recipe link copied to clipboard!', 'success');
        }).catch(() => {
            showNotification('Unable to share recipe', 'error');
        });
    }
}

// Saved Recipes Management
async function loadSavedRecipes() {
    if (!AppState.currentUser) {
        showNotification('Please login to view saved recipes', 'error');
        Navigation.showPage('home');
        return;
    }
    
    const loadingDiv = document.getElementById('savedRecipesLoading');
    const listDiv = document.getElementById('savedRecipesList');
    const noRecipesDiv = document.getElementById('noSavedRecipes');
    
    // Show loading state
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (listDiv) listDiv.style.display = 'none';
    if (noRecipesDiv) noRecipesDiv.style.display = 'none';
    
    try {
        const response = await apiCall(`/api/recipes/saved/${AppState.currentUser.id}`);
        const savedRecipes = response;
        
        // Hide loading
        if (loadingDiv) loadingDiv.style.display = 'none';
        
        if (savedRecipes && savedRecipes.length > 0) {
            displaySavedRecipes(savedRecipes);
            if (listDiv) listDiv.style.display = 'grid';
        } else {
            if (noRecipesDiv) noRecipesDiv.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Failed to load saved recipes:', error);
        if (loadingDiv) loadingDiv.style.display = 'none';
        if (noRecipesDiv) noRecipesDiv.style.display = 'block';
        showNotification('Failed to load saved recipes', 'error');
    }
}

function displaySavedRecipes(recipes) {
    const container = document.getElementById('savedRecipesList');
    if (!container) return;
    
    container.innerHTML = recipes.map((recipe, index) => {
        const cleanName = recipe.name.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '');
        const cleanOrigin = recipe.origin?.replace(/^\*\s*/, '').replace(/\s*\*$/, '') || 'African';
        
        return `
            <div class="recipe-card saved-recipe-card">
                <div class="recipe-card-header">
                    <h3>${cleanName}</h3>
                    <div class="recipe-meta-small">
                        <span><i class="fas fa-clock"></i> ${recipe.cooking_time || '30 mins'}</span>
                        <span><i class="fas fa-globe"></i> ${cleanOrigin}</span>
                    </div>
                </div>
                
                <div class="recipe-card-content">
                    <div class="recipe-ingredients-preview">
                        <strong>Key Ingredients:</strong>
                        <p>${recipe.ingredients?.slice(0, 3).map(ing => ing.replace(/^\*\s*/, '').replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '')).filter(ing => ing.trim()).join(', ')}...</p>
                    </div>
                    
                    ${recipe.health_benefits ? `
                        <div class="recipe-health-preview">
                            <strong>Health Benefits:</strong>
                            <p>${recipe.health_benefits.replace(/^\*\s*/, '').replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '').substring(0, 100)}...</p>
                        </div>
                    ` : ''}
                </div>
                
                <div class="recipe-card-actions">
                    <button class="btn-primary" onclick="viewSavedRecipe(${index})">
                        <i class="fas fa-eye"></i> View Recipe
                    </button>
                    <button class="btn-outline" onclick="removeSavedRecipe('${recipe.id || recipe._id}', ${index})">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Store recipes globally for viewing
    window.savedRecipes = recipes;
}

function viewSavedRecipe(index) {
    const recipe = window.savedRecipes?.[index];
    if (!recipe) {
        showNotification('Recipe not found', 'error');
        return;
    }
    
    // Use the existing viewRecipe modal but with saved recipe data
    window.currentRecipes = window.savedRecipes;
    viewRecipe(index);
}

async function removeSavedRecipe(recipeId, index) {
    if (!AppState.currentUser) {
        showNotification('Please login to manage saved recipes', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to remove this recipe from your saved collection?')) {
        return;
    }
    
    try {
        await apiCall(`/api/recipes/saved/${recipeId}?user_id=${AppState.currentUser.id}`, {
            method: 'DELETE'
        });
        
        showNotification('Recipe removed from saved collection', 'success');
        
        // Reload saved recipes
        loadSavedRecipes();
        
    } catch (error) {
        console.error('Remove saved recipe failed:', error);
        showNotification('Failed to remove recipe', 'error');
    }
}

// Payment Management
function openPaymentModal() {
    if (!AppState.currentUser) {
        showNotification('Please login to upgrade to premium', 'error');
        Auth.showLoginModal();
        return;
    }
    
    const modal = document.getElementById('paymentModal');
    const paymentPhone = document.getElementById('paymentPhone');
    
    // Pre-fill phone number if available
    if (paymentPhone && AppState.currentUser.phone_number) {
        paymentPhone.value = AppState.currentUser.phone_number;
    }
    
    if (modal) {
        modal.style.display = 'block';
    }
}

function closePaymentModal() {
    const modal = document.getElementById('paymentModal');
    const paymentContent = document.getElementById('paymentContent');
    const paymentStatus = document.getElementById('paymentStatus');
    
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Reset modal content
    if (paymentContent) paymentContent.style.display = 'block';
    if (paymentStatus) paymentStatus.style.display = 'none';
    
    // Clear any payment status intervals
    if (window.paymentStatusInterval) {
        clearInterval(window.paymentStatusInterval);
        window.paymentStatusInterval = null;
    }
    
    // Reset any global payment state
    window.currentCheckoutId = null;
}

async function initiatePayment() {
    const phoneInput = document.getElementById('paymentPhone');
    const paymentButton = document.getElementById('paymentButton');
    
    if (!phoneInput || !phoneInput.value.trim()) {
        showNotification('Please enter your M-Pesa phone number', 'error');
        return;
    }
    
    const phoneNumber = phoneInput.value.trim();
    
    // Validate phone number format
    if (!/^254\d{9}$/.test(phoneNumber)) {
        showNotification('Please enter a valid M-Pesa number (254XXXXXXXXX)', 'error');
        return;
    }
    
    // Disable button and show loading
    if (paymentButton) {
        paymentButton.disabled = true;
        paymentButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    }
    
    try {
        const response = await apiCall('/api/payments/subscription/purchase', {
            method: 'POST',
            body: {
                plan: 'premium',
                phone_number: phoneNumber
            }
        });
        
        showNotification('Payment initiated! Check your phone for M-Pesa prompt', 'success');
        
        // Show payment status screen
        showPaymentStatus(response.checkout_id, response.is_demo);
        
    } catch (error) {
        console.error('Payment initiation failed:', error);
        showNotification('Payment initiation failed. Please try again.', 'error');
        
        // Re-enable button
        if (paymentButton) {
            paymentButton.disabled = false;
            paymentButton.innerHTML = '<i class="fas fa-mobile-alt"></i> Pay with M-Pesa';
        }
    }
}

function showPaymentStatus(checkoutId, isDemo = false) {
    const paymentContent = document.getElementById('paymentContent');
    const paymentStatus = document.getElementById('paymentStatus');
    
    if (paymentContent) paymentContent.style.display = 'none';
    if (paymentStatus) {
        paymentStatus.style.display = 'block';
        paymentStatus.innerHTML = `
            <div class="payment-status-content">
                <div class="payment-status-header">
                    <i class="fas fa-mobile-alt" style="font-size: 3rem; color: var(--primary-solid); margin-bottom: 1rem;"></i>
                    <h2>Payment ${isDemo ? 'Demo' : 'Initiated'}</h2>
                    <p>${isDemo ? 'Demo mode - Payment will auto-complete in 10 seconds' : 'Check your phone for the M-Pesa payment prompt'}</p>
                </div>
                
                <div class="payment-status-info">
                    <div class="status-item">
                        <span>Checkout ID:</span>
                        <code>${checkoutId}</code>
                    </div>
                    <div class="status-item">
                        <span>Amount:</span>
                        <strong>KES 299</strong>
                    </div>
                    <div class="status-item">
                        <span>Status:</span>
                        <span id="currentPaymentStatus" class="status-pending">
                            <i class="fas fa-clock"></i> Waiting for payment...
                        </span>
                    </div>
                </div>
                
                <div class="payment-actions">
                    <button class="btn-outline" onclick="closePaymentModal()" id="cancelPaymentButton">Cancel</button>
                    <button class="btn-primary" onclick="checkPaymentStatus('${checkoutId}')" id="checkStatusButton">
                        <i class="fas fa-sync"></i> Check Status
                    </button>
                </div>
            </div>
        `;
        
        
        // Start periodic status checking
        window.paymentStatusInterval = setInterval(() => {
            checkPaymentStatus(checkoutId);
        }, 5000);
    }
}

async function checkPaymentStatus(checkoutId) {
    try {
        const response = await apiCall(`/api/payments/status/${checkoutId}`);
        const statusElement = document.getElementById('currentPaymentStatus');
        const checkButton = document.getElementById('checkStatusButton');
        
        // Update button state during check
        if (checkButton) {
            checkButton.disabled = true;
            checkButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
        }
        
        if (statusElement) {
            if (response.status === 'completed') {
                statusElement.innerHTML = '<i class="fas fa-check-circle" style="color: var(--success);"></i> Payment Successful!';
                statusElement.className = 'status-success';
                
                // Update button to show completion
                if (checkButton) {
                    checkButton.innerHTML = '<i class="fas fa-check"></i> Completed';
                    checkButton.disabled = true;
                    checkButton.className = 'btn-success';
                }
                
                // Clear interval
                if (window.paymentStatusInterval) {
                    clearInterval(window.paymentStatusInterval);
                }
                
                showNotification('Premium activated successfully!', 'success');
                
                // Update user status
                AppState.currentUser.is_premium = true;
                updateAuthUI();
                
                // Close modal after delay
                setTimeout(() => {
                    closePaymentModal();
                }, 3000);
                
            } else if (response.status === 'failed') {
                statusElement.innerHTML = '<i class="fas fa-times-circle" style="color: var(--error);"></i> Payment Failed';
                statusElement.className = 'status-failed';
                
                // Update button to show retry option
                if (checkButton) {
                    checkButton.innerHTML = '<i class="fas fa-redo"></i> Retry Payment';
                    checkButton.disabled = false;
                    checkButton.className = 'btn-outline';
                    checkButton.onclick = () => {
                        closePaymentModal();
                        setTimeout(() => openPaymentModal(), 500);
                    };
                }
                
                if (window.paymentStatusInterval) {
                    clearInterval(window.paymentStatusInterval);
                }
                
                showNotification('Payment failed. Please try again.', 'error');
            } else {
                // Payment still pending
                statusElement.innerHTML = '<i class="fas fa-clock" style="color: var(--warning);"></i> Payment in progress...';
                statusElement.className = 'status-pending';
                
                // Reset button to normal check state
                if (checkButton) {
                    checkButton.disabled = false;
                    checkButton.innerHTML = '<i class="fas fa-sync"></i> Check Status';
                    checkButton.className = 'btn-primary';
                }
            }
        }
        
    } catch (error) {
        console.error('Payment status check failed:', error);
        
        // Update UI to show error state
        const statusElement = document.getElementById('currentPaymentStatus');
        const checkButton = document.getElementById('checkStatusButton');
        
        if (statusElement) {
            statusElement.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: var(--error);"></i> Status check failed';
            statusElement.className = 'status-error';
        }
        
        if (checkButton) {
            checkButton.disabled = false;
            checkButton.innerHTML = '<i class="fas fa-sync"></i> Retry Check';
            checkButton.className = 'btn-outline';
        }
        
        showNotification('Unable to check payment status. Please try again.', 'error');
    }
}


// Quick Actions
function quickAction(type) {
    switch(type) {
        case 'mood':
            Navigation.showPage('generate');
            break;
        case 'pantry':
            Navigation.showPage('generate');
            setTimeout(() => showNotification('Camera feature coming soon!', 'info'), 500);
            break;
        case 'surprise':
            AppState.selectedIngredients = ['Rice', 'Tomatoes', 'Onions'];
            AppState.selectedMood = 'adventurous';
            Navigation.showPage('generate');
            setTimeout(() => RecipeGenerator.generateRecipes(), 500);
            break;
        case 'healthy':
            AppState.selectedMood = 'healthy';
            Navigation.showPage('generate');
            break;
    }
}

// Global function bindings for HTML onclick compatibility
window.showLoginModal = function() { Auth.showLoginModal(); };
window.showRegisterModal = function() { Auth.showRegisterModal(); };
window.generateRecipes = () => RecipeGenerator.generateRecipes();
window.setMood = (mood) => RecipeGenerator.setMood(mood);
window.showIngredientCategory = (category) => RecipeGenerator.showIngredientCategory(category);
window.toggleIngredient = (ingredient) => RecipeGenerator.toggleIngredient(ingredient);
window.viewRecipe = viewRecipe;
window.closeRecipeModal = closeRecipeModal;
window.saveRecipe = saveRecipe;
window.shareRecipe = shareRecipe;
window.loadSavedRecipes = loadSavedRecipes;
window.viewSavedRecipe = viewSavedRecipe;
window.removeSavedRecipe = removeSavedRecipe;
window.openPaymentModal = openPaymentModal;
window.closePaymentModal = closePaymentModal;
window.initiatePayment = initiatePayment;
window.checkPaymentStatus = checkPaymentStatus;
window.toggleChat = toggleChat;
window.sendChatMessage = sendChatMessage;
window.quickAction = quickAction;

// Highlight Recipes Management
const HighlightRecipes = {
    async loadHighlights() {
        try {
            const response = await apiCall('/api/highlights');
            if (response.success && response.recipes) {
                this.displayHighlights(response.recipes);
            } else {
                // Generate new highlights if none exist
                await this.generateHighlights();
            }
        } catch (error) {
            console.error('Failed to load highlights:', error);
            // Show fallback highlights
            this.showFallbackHighlights();
        }
    },

    async generateHighlights() {
        try {
            showNotification('Generating fresh highlight recipes...', 'info');
            const response = await apiCall('/api/highlights/generate', {
                method: 'POST'
            });
            
            if (response.success) {
                this.displayHighlights(response.recipes);
                showNotification('New highlight recipes generated!', 'success');
            }
        } catch (error) {
            console.error('Failed to generate highlights:', error);
            showNotification('Failed to generate highlights', 'error');
        }
    },

    displayHighlights(recipes) {
        const container = document.querySelector('#discover .recipe-grid');
        if (!container || !recipes.length) return;

        container.innerHTML = recipes.slice(0, 6).map((recipe, index) => {
            const cleanName = recipe.name?.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '') || 'Delicious Recipe';
            const rating = recipe.rating || (4.2 + Math.random() * 0.8);
            
            return `
                <div class="recipe-card" data-recipe-index="${index}">
                    <div class="recipe-card-content">
                        <div class="recipe-header">
                            <h3>${cleanName}</h3>
                            <span class="recipe-origin">${recipe.cuisine || 'African'}</span>
                        </div>
                        <div class="recipe-meta">
                            <span><i class="fas fa-clock"></i> ${recipe.cooking_time || '30 mins'}</span>
                            <span><i class="fas fa-users"></i> ${recipe.servings || 4} servings</span>
                            <span><i class="fas fa-star"></i> ${rating.toFixed(1)}</span>
                        </div>
                        <p>${recipe.description || 'A wonderful traditional dish with authentic flavors.'}</p>
                        <div class="recipe-actions">
                            <button class="btn-primary" onclick="viewHighlightRecipe(${index})">
                                <i class="fas fa-eye"></i> View Recipe
                            </button>
                            <button class="btn-outline" onclick="startCookingMode(${index})">
                                <i class="fas fa-play"></i> Start Cooking
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Store recipes globally
        window.highlightRecipes = recipes;
    },

    showFallbackHighlights() {
        const fallbackRecipes = [
            {
                name: "Ugali with Sukuma Wiki",
                cuisine: "Kenyan",
                cooking_time: "25 mins",
                servings: 4,
                rating: 4.8,
                description: "A traditional Kenyan staple with nutritious greens",
                ingredients: ["Maize flour", "Sukuma wiki", "Onions", "Tomatoes"],
                instructions: ["Boil water", "Add maize flour gradually", "Prepare sukuma wiki"]
            },
            {
                name: "Jollof Rice",
                cuisine: "Nigerian",
                cooking_time: "45 mins",
                servings: 6,
                rating: 4.9,
                description: "Flavorful one-pot rice dish with spices and vegetables",
                ingredients: ["Rice", "Tomatoes", "Onions", "Spices"],
                instructions: ["Prepare tomato base", "Add rice", "Simmer until tender"]
            }
        ];
        
        this.displayHighlights(fallbackRecipes);
    }
};

// Kitchen Widget for Realtime Guidance
const KitchenWidget = {
    currentSession: null,
    currentStep: 0,
    timers: [],

    async startCooking(recipeData) {
        try {
            const response = await apiCall('/api/kitchen/start-cooking', {
                method: 'POST',
                body: {
                    recipe_data: recipeData
                }
            });

            if (response.success) {
                this.currentSession = response.session;
                this.showCookingInterface();
                showNotification('Cooking mode activated! Follow the step-by-step guidance.', 'success');
            }
        } catch (error) {
            console.error('Failed to start cooking:', error);
            showNotification('Failed to start cooking mode', 'error');
        }
    },

    showCookingInterface() {
        const modal = document.createElement('div');
        modal.className = 'modal cooking-modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content cooking-interface">
                <span class="close" onclick="KitchenWidget.closeCookingMode()">&times;</span>
                <div class="cooking-header">
                    <h2><i class="fas fa-utensils"></i> Cooking: ${this.currentSession.recipe.name}</h2>
                    <div class="cooking-progress">
                        <span>Step ${this.currentStep + 1} of ${this.currentSession.total_steps}</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(this.currentStep / this.currentSession.total_steps) * 100}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="cooking-content">
                    <div class="current-step" id="currentStep">
                        <h3>Current Step</h3>
                        <p id="stepInstruction">${this.currentSession.enhanced_steps[0]?.instruction || 'Getting ready...'}</p>
                        <div class="step-meta">
                            <span><i class="fas fa-clock"></i> ${this.currentSession.enhanced_steps[0]?.estimated_time || '5 mins'}</span>
                            <span><i class="fas fa-thermometer-half"></i> ${this.currentSession.enhanced_steps[0]?.temperature || 'Medium heat'}</span>
                        </div>
                        <div class="cooking-tip">
                            <i class="fas fa-lightbulb"></i>
                            <span id="cookingTip">${this.currentSession.enhanced_steps[0]?.tips || 'Take your time and enjoy the process!'}</span>
                        </div>
                    </div>
                    
                    <div class="cooking-controls">
                        <button class="btn-outline" onclick="KitchenWidget.setTimer()">
                            <i class="fas fa-stopwatch"></i> Set Timer
                        </button>
                        <button class="btn-primary" onclick="KitchenWidget.nextStep()">
                            <i class="fas fa-arrow-right"></i> Next Step
                        </button>
                        <button class="btn-outline" onclick="KitchenWidget.voiceCommand()">
                            <i class="fas fa-microphone"></i> Voice Help
                        </button>
                    </div>
                    
                    <div class="active-timers" id="activeTimers"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    },

    async nextStep() {
        if (this.currentStep >= this.currentSession.total_steps - 1) {
            this.completeCooking();
            return;
        }

        this.currentStep++;
        
        try {
            const response = await apiCall('/api/kitchen/next-step', {
                method: 'POST',
                body: {
                    session_id: this.currentSession.session_id,
                    current_step: this.currentStep
                }
            });

            if (response.success) {
                this.updateStepDisplay();
                showNotification(response.next_step.tip, 'info');
            }
        } catch (error) {
            console.error('Failed to get next step:', error);
            this.updateStepDisplay(); // Continue with local data
        }
    },

    updateStepDisplay() {
        const stepInstruction = document.getElementById('stepInstruction');
        const cookingTip = document.getElementById('cookingTip');
        const progressFill = document.querySelector('.progress-fill');
        
        if (stepInstruction && this.currentSession.enhanced_steps[this.currentStep]) {
            const step = this.currentSession.enhanced_steps[this.currentStep];
            stepInstruction.textContent = step.instruction;
            if (cookingTip) cookingTip.textContent = step.tips;
        }
        
        if (progressFill) {
            progressFill.style.width = `${(this.currentStep / this.currentSession.total_steps) * 100}%`;
        }
        
        // Update step counter
        const stepCounter = document.querySelector('.cooking-progress span');
        if (stepCounter) {
            stepCounter.textContent = `Step ${this.currentStep + 1} of ${this.currentSession.total_steps}`;
        }
    },

    async setTimer() {
        const duration = prompt('Set timer for how many minutes?', '5');
        if (!duration || isNaN(duration)) return;

        try {
            const response = await apiCall('/api/kitchen/set-timer', {
                method: 'POST',
                body: {
                    duration: parseInt(duration),
                    label: `Step ${this.currentStep + 1} Timer`
                }
            });

            if (response.success) {
                this.addTimer(response.timer);
                showNotification(`Timer set for ${duration} minutes`, 'success');
            }
        } catch (error) {
            console.error('Failed to set timer:', error);
            // Fallback local timer
            this.addLocalTimer(parseInt(duration));
        }
    },

    addTimer(timer) {
        this.timers.push(timer);
        this.updateTimersDisplay();
        
        // Start countdown
        const timerInterval = setInterval(() => {
            const timeLeft = new Date(timer.ends_at) - new Date();
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                this.timerComplete(timer);
            }
        }, 1000);
    },

    addLocalTimer(minutes) {
        const timer = {
            id: `local_${Date.now()}`,
            label: `Step ${this.currentStep + 1} Timer`,
            duration: minutes,
            started_at: new Date().toISOString(),
            ends_at: new Date(Date.now() + minutes * 60000).toISOString()
        };
        
        this.addTimer(timer);
        showNotification(`Timer set for ${minutes} minutes`, 'success');
    },

    updateTimersDisplay() {
        const container = document.getElementById('activeTimers');
        if (!container) return;
        
        container.innerHTML = this.timers.map(timer => `
            <div class="timer-item" data-timer-id="${timer.id}">
                <span class="timer-label">${timer.label}</span>
                <span class="timer-countdown" id="countdown-${timer.id}">--:--</span>
            </div>
        `).join('');
    },

    timerComplete(timer) {
        showNotification(`⏰ Timer complete: ${timer.label}`, 'warning');
        
        // Play notification sound (if available)
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('KE-ROUMA Timer', {
                body: `${timer.label} is complete!`,
                icon: '/static/favicon.ico'
            });
        }
        
        // Remove from active timers
        this.timers = this.timers.filter(t => t.id !== timer.id);
        this.updateTimersDisplay();
    },

    async voiceCommand() {
        if (!('webkitSpeechRecognition' in window)) {
            showNotification('Voice commands not supported in this browser', 'error');
            return;
        }

        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            showNotification('Listening... Say your command', 'info');
        };

        recognition.onresult = async (event) => {
            const command = event.results[0][0].transcript.toLowerCase();
            
            try {
                const response = await apiCall('/api/kitchen/voice-command', {
                    method: 'POST',
                    body: { command }
                });
                
                if (response.success) {
                    showNotification(response.response, 'info');
                    
                    // Handle specific commands
                    if (command.includes('next step')) {
                        this.nextStep();
                    } else if (command.includes('set timer')) {
                        this.setTimer();
                    }
                }
            } catch (error) {
                showNotification('Voice command failed', 'error');
            }
        };

        recognition.onerror = () => {
            showNotification('Voice recognition error', 'error');
        };

        recognition.start();
    },

    completeCooking() {
        showNotification('🎉 Cooking complete! Enjoy your meal!', 'success');
        this.closeCookingMode();
    },

    closeCookingMode() {
        const modal = document.querySelector('.cooking-modal');
        if (modal) modal.remove();
        
        this.currentSession = null;
        this.currentStep = 0;
        this.timers = [];
    }
};

// Global functions for HTML onclick compatibility
window.viewHighlightRecipe = (index) => {
    const recipe = window.highlightRecipes?.[index];
    if (recipe) {
        window.currentRecipes = [recipe];
        viewRecipe(0);
    }
};

window.startCookingMode = (index) => {
    const recipe = window.highlightRecipes?.[index];
    if (recipe) {
        KitchenWidget.startCooking(recipe);
    }
};

window.refreshHighlights = () => {
    HighlightRecipes.generateHighlights();
};

// Load real recipes for home page
async function loadHomePageRecipes() {
    try {
        const response = await apiCall('/api/highlights');
        if (response.success && response.recipes && response.recipes.length > 0) {
            displayHomePageRecipes(response.recipes.slice(0, 3)); // Show first 3 recipes
        } else {
            // Generate new highlights if none exist
            const generateResponse = await apiCall('/api/highlights/generate', {
                method: 'POST'
            });
            if (generateResponse.success && generateResponse.recipes) {
                displayHomePageRecipes(generateResponse.recipes.slice(0, 3));
            }
        }
    } catch (error) {
        console.error('Failed to load home page recipes:', error);
        // Keep static recipes as fallback
    }
}

function displayHomePageRecipes(recipes) {
    const container = document.querySelector('#home .recipe-grid');
    if (!container || !recipes.length) return;

    container.innerHTML = recipes.map((recipe, index) => {
        const cleanName = recipe.name?.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '') || 'Delicious Recipe';
        const rating = recipe.rating || (4.2 + Math.random() * 0.8);
        
        return `
            <div class="recipe-card">
                <div class="recipe-card-content">
                    <div class="recipe-header">
                        <h3>${cleanName}</h3>
                        <span class="recipe-origin">${recipe.cuisine || 'African'}</span>
                    </div>
                    <div class="recipe-meta">
                        <span><i class="fas fa-clock"></i> ${recipe.cooking_time || '30 mins'}</span>
                        <span><i class="fas fa-users"></i> ${recipe.servings || 4} servings</span>
                        <span><i class="fas fa-star"></i> ${rating.toFixed(1)}</span>
                    </div>
                    <p>${recipe.description || 'A wonderful traditional dish with authentic flavors.'}</p>
                    <button class="btn-primary" onclick="viewHomeRecipe(${index})">
                        <i class="fas fa-eye"></i> View Recipe
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    // Store recipes globally for viewing
    window.homeRecipes = recipes;
}

// View recipe from home page
window.viewHomeRecipe = (index) => {
    const recipe = window.homeRecipes?.[index];
    if (recipe) {
        window.currentRecipes = [recipe];
        viewRecipe(0);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    AppState.init();
    Navigation.init();
    updateAuthUI();
    
    // Load real highlight recipes for home page
    loadHomePageRecipes();
    
    // Load real highlight recipes for discover page
    HighlightRecipes.loadHighlights();
    
    // Set up chat input handler
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Set up chat toggle
    const chatToggle = document.querySelector('.chat-toggle');
    if (chatToggle) {
        chatToggle.addEventListener('click', toggleChat);
    }
    
    // Initialize floating background icons
    createFloatingIcons();
    
    // Request notification permission for timers
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    console.log('KE-ROUMA app initialized!');
});

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};