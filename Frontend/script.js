document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchBar = document.querySelector('.search-bar');
    const searchContainer = document.querySelector('.search-container');
    const faqSection = document.querySelector('.faq-section');
    const chatWindow = document.querySelector('.chat-window');
    const chatMessages = document.querySelector('.chat-messages');
    const themeToggle = document.querySelector('.theme-toggle');
    const voiceInput = document.querySelector('.voice-input');
    const clearChatBtn = document.querySelector('.chat-action-btn[aria-label="Clear chat"]');
    const downloadChatBtn = document.querySelector('.chat-action-btn[aria-label="Download chat"]');
    const faqCards = document.querySelectorAll('.faq-card');
    const feedbackPopup = document.querySelector('.feedback-popup');

    // State
    let darkMode = false;
    let isListening = false;

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        darkMode = !darkMode;
        document.body.classList.toggle('dark-mode');
        themeToggle.querySelector('i').classList.toggle('fa-moon');
        themeToggle.querySelector('i').classList.toggle('fa-sun');
    });

    // Voice Input
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;

        voiceInput.addEventListener('click', () => {
            if (!isListening) {
                recognition.start();
                voiceInput.querySelector('i').classList.remove('fa-microphone');
                voiceInput.querySelector('i').classList.add('fa-microphone-slash');
            } else {
                recognition.stop();
                voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
                voiceInput.querySelector('i').classList.add('fa-microphone');
            }
            isListening = !isListening;
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            searchBar.value = transcript;
            handleSearch({ key: 'Enter' });
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
            isListening = false;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isListening = false;
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
        };
    } else {
        voiceInput.style.display = 'none';
    }

    // Search and Chat Functions
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        messageDiv.textContent = message;

        // Add message actions
        const actionsDiv = document.createElement('div');
        actionsDiv.classList.add('message-actions');
        
        if (!isUser) {
            const copyBtn = document.createElement('button');
            copyBtn.classList.add('message-action');
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(message);
                showFeedbackPopup();
            };
            actionsDiv.appendChild(copyBtn);
        }

        messageDiv.appendChild(actionsDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('typing-indicator');
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            indicator.appendChild(dot);
        }
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicator;
    }

    function handleSearch(event) {
        if (event.key === 'Enter' && searchBar.value.trim()) {
            // Move search bar to bottom
            searchContainer.classList.add('bottom');
            faqSection.classList.add('hidden');
            chatWindow.classList.add('active');

            // Add user message
            const userQuestion = searchBar.value.trim();
            addMessage(userQuestion, true);

            // Show typing indicator
            const typingIndicator = showTypingIndicator();

            // Simulate bot response (replace with actual backend call)
            setTimeout(() => {
                typingIndicator.remove();
                // Example response - replace with actual AI response
                const response = `Here's the information about "${userQuestion}". This is a simulated response. In a real implementation, this would be connected to your backend API.`;
                addMessage(response);
            }, 1500);

            // Clear search bar
            searchBar.value = '';
        }
    }

    // Event Listeners
    searchBar.addEventListener('keypress', handleSearch);

    // FAQ Cards
    faqCards.forEach(card => {
        card.addEventListener('click', () => {
            const question = card.querySelector('h3').textContent;
            searchBar.value = question;
            handleSearch({ key: 'Enter' });
        });
    });

    // Clear Chat
    clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat?')) {
            chatMessages.innerHTML = '';
            searchContainer.classList.remove('bottom');
            faqSection.classList.remove('hidden');
            chatWindow.classList.remove('active');
        }
    });

    // Download Chat
    downloadChatBtn.addEventListener('click', () => {
        const messages = Array.from(chatMessages.querySelectorAll('.message'))
            .map(msg => `${msg.classList.contains('user-message') ? 'User' : 'Bot'}: ${msg.textContent}`)
            .join('\n\n');
        
        const blob = new Blob([messages], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'chat-history.txt';
        a.click();
        window.URL.revokeObjectURL(url);
    });

    // Feedback Popup
    function showFeedbackPopup() {
        feedbackPopup.style.display = 'block';
        setTimeout(() => {
            feedbackPopup.style.display = 'none';
        }, 3000);
    }

    // Handle feedback buttons
    document.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Here you would typically send the feedback to your backend
            feedbackPopup.style.display = 'none';
        });
    });

    // Search Suggestions
    const suggestions = document.querySelector('.suggestions');
    let debounceTimeout;

    searchBar.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            const query = searchBar.value.trim().toLowerCase();
            if (query.length >= 2) {
                // Simulate getting suggestions (replace with actual API call)
                const fakeSuggestions = Array.from(faqCards)
                    .map(card => card.querySelector('h3').textContent)
                    .filter(text => text.toLowerCase().includes(query));
                
                if (fakeSuggestions.length > 0) {
                    suggestions.innerHTML = '';
                    suggestions.style.display = 'block';
                    fakeSuggestions.forEach(suggestion => {
                        const div = document.createElement('div');
                        div.classList.add('suggestion-item');
                        div.textContent = suggestion;
                        div.addEventListener('click', () => {
                            searchBar.value = suggestion;
                            suggestions.style.display = 'none';
                            handleSearch({ key: 'Enter' });
                        });
                        suggestions.appendChild(div);
                    });
                } else {
                    suggestions.style.display = 'none';
                }
            } else {
                suggestions.style.display = 'none';
            }
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchBar.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.style.display = 'none';
        }
    });

    // Mobile responsiveness
    function handleResize() {
        if (window.innerWidth <= 768) {
            if (chatWindow.classList.contains('active')) {
                searchContainer.style.bottom = '70px';
            }
        } else {
            searchContainer.style.bottom = '20px';
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();
});