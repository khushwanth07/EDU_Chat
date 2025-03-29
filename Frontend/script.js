window.togglePrivacyPolicy = function() {
    const policyBox = document.getElementById("privacyContainer");
    const consentPopup = document.getElementById("privacy-consent-popup");
    
    // Always ensure proper z-index when opening
    if (policyBox.style.display === "none" || policyBox.style.display === "") {
        // Force the policy box to have the maximum z-index
        policyBox.style.display = "block";
        policyBox.style.zIndex = "10000";
        
        // Dim the consent popup if it's visible
        if (consentPopup && getComputedStyle(consentPopup).display !== "none") {
            consentPopup.classList.add('privacy-consent-dimmed');
        }
    } else {
        policyBox.style.display = "none";
        
        // Remove dimming when closing
        if (consentPopup) {
            consentPopup.classList.remove('privacy-consent-dimmed');
        }
    }
};

window.closePrivacyPolicy = function() {
    const policyBox = document.getElementById("privacyContainer");
    const consentPopup = document.getElementById("privacy-consent-popup");
    
    policyBox.style.display = "none";
    
    // Remove dimming when closing
    if (consentPopup) {
        consentPopup.classList.remove('privacy-consent-dimmed');
    }
};


  // Team Page
  function toggleTeamPage() {
    const teamContainer = document.getElementById("teamContainer");

   
    if (teamContainer.style.display === "none" || teamContainer.style.display === "") {
        teamContainer.style.display = "block";
    } else {
        teamContainer.style.display = "none"; // 否则，隐藏它
    }
}

// close Team Page 
function closeTeamPage() {
    document.getElementById("teamContainer").style.display = "none";
}


document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.querySelector('.search-input');
    const voiceInput = document.querySelector('.voice-input');
    const chatWindow = document.querySelector('.chat-window');
    const chatMessages = document.querySelector('.chat-messages');
    const clearChatBtn = document.querySelector('.clear-chat');
    const downloadChatBtn = document.querySelector('.download-chat');
    const faqItems = document.querySelectorAll('.faq-item');
    const heroSection = document.querySelector('.hero');
    const privacyConsentPopup = document.getElementById('privacy-consent-popup');
    const acceptButton = document.getElementById('accept-privacy');
    const declineButton = document.getElementById('decline-privacy');

    // Check if user has already consented
    const hasConsented = localStorage.getItem('privacyConsent');

    if (!hasConsented) {
        // Show the popup if user hasn't consented yet
        privacyConsentPopup.style.display = 'flex';
        // Prevent scrolling of the body when popup is visible
        document.body.style.overflow = 'hidden';
    } else {
        // If already consented, hide the popup
        privacyConsentPopup.style.display = 'none';
    }
    
    // Accept button event listener
    acceptButton.addEventListener('click', () => {
        // Store consent in localStorage
        localStorage.setItem('privacyConsent', 'true');
        // Hide the popup
        privacyConsentPopup.style.display = 'none';
        // Re-enable scrolling
        document.body.style.overflow = 'auto';
    });
    
    // Decline button event listener
    declineButton.addEventListener('click', () => {
        // Show a message that they need to accept to use the site
        alert('You must accept the Privacy Policy to use this website. If you decline, you may not be able to use all features of the site.');
    });

    // Add welcome message when page loads
    function addWelcomeMessage() {
        const welcomeMessage = "Hello! I'm Nia, your AI assistant for the AI & Society course at TUM. How can I help you today? You can ask me about admissions, curriculum, or click on any FAQ below.";
        setTimeout(() => {
            addMessage(welcomeMessage, false);
            showChatWindow();
        }, 500);
    }

    // Chat Window Management Functions
    function showChatWindow() {
        heroSection.classList.add('expanded');
        chatWindow.classList.add('active');
        
        // Ensure messages fit
        const chatHeader = chatWindow.querySelector('.chat-header');
        const headerHeight = chatHeader.offsetHeight;
        chatMessages.style.maxHeight = `calc(100% - ${headerHeight}px)`;
        
        if (!chatWindow.classList.contains('active')) {
            // Expand hero section first
            heroSection.classList.add('expanded');
            
            // Show chat window with animation
            setTimeout(() => {
                chatWindow.classList.add('active');
            }, 300);
    
            // Smooth scroll to chat window on mobile
            if (window.innerWidth <= 768) {
                setTimeout(() => {
                    const chatSectionTop = document.getElementById('chat-section').offsetTop;
                    window.scrollTo({ top: chatSectionTop, behavior: 'smooth' });
                }, 100);
            }
        }
    }

    function collapseChatWindow() {
        chatWindow.classList.remove('active');
        heroSection.classList.remove('expanded');
        // Clear search input when collapsing
        searchInput.value = '';
    }

    // Message Management Functions
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const textSpan = document.createElement('span');
        // Use textContent for security, but handle line breaks
        const formattedMessage = message.replace(/\n/g, '<br>');
        textSpan.innerHTML = formattedMessage;
        messageDiv.appendChild(textSpan);

        // Add role attributes for accessibility
        messageDiv.setAttribute('role', 'listitem');
        messageDiv.setAttribute('aria-label', `${isUser ? 'You' : 'Assistant'}: ${message}`);

        chatMessages.appendChild(messageDiv);
        
        // Ensure proper scroll after adding message
        requestAnimationFrame(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        });
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('typing-indicator');
        indicator.setAttribute('aria-label', 'Assistant is typing');
        indicator.setAttribute('role', 'status');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            indicator.appendChild(dot);
        }
        
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicator;
    }



        // Convert links in text into clickable hyperlinks
        function makeLinksClickable(text) {
            const urlPattern = /(https?:\/\/[^\s]+)/g;
            return text.replace(urlPattern, (url) => {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
            });
        }
        


    // Function to handle user input
    function handleInput(inputText) {
        if (!inputText.trim()) return;

        // Display user message
        addMessage(inputText, true);

        // Show chat window
        showChatWindow();

        // Display typing indicator
        const typingIndicator = showTypingIndicator();

        // Fetch response from backend with error handling
        fetch('http://127.0.0.1:5000/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: inputText })
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Network response error: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                typingIndicator.remove();
                const formattedResponse = makeLinksClickable(data.response);
                addMessage(data.response, false);
            })
            .catch((error) => {
                typingIndicator.remove();
                console.error('Error fetching response:', error);
                
                // Simple user-friendly error message without retry option
                addMessage(`I'm having trouble connecting to our knowledge base. This could be due to a temporary network issue. Please try again in a moment or refresh the page.`, false);
                
                // Ensure scroll is at the bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
    }

    // Event Listeners
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            handleInput(searchInput.value.trim());
            searchInput.value = '';
        }
    });
    
    // Also handle clicks on the search bar to show the chat window
    searchInput.addEventListener('focus', () => {
        if (!chatWindow.classList.contains('active')) {
            showChatWindow();
        }
    });

    // Clear chat functionality with confirmation
    clearChatBtn.addEventListener('click', () => {
        if (chatMessages.children.length === 0) {
            return; // Nothing to clear
        }
        
        if (confirm('Are you sure you want to clear the chat history?')) {
            chatMessages.innerHTML = '';
            collapseChatWindow();
            // Add a system message
            setTimeout(() => {
                addWelcomeMessage();
            }, 300);
        }
    });

    // Download chat functionality
    downloadChatBtn.addEventListener('click', () => {
        const messages = Array.from(chatMessages.children)
            .filter(msg => msg.classList.contains('message'))
            .map(msg => {
                const isUser = msg.classList.contains('user-message');
                const text = msg.querySelector('span').textContent;
                return `${isUser ? 'You' : 'Assistant'}: ${text}`;
            })
            .join('\n\n');

        if (messages.length === 0) {
            alert('No messages to download yet.');
            return;
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const blob = new Blob([messages], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${timestamp}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // FAQ Items Click Handlers
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const question = item.querySelector('h3').textContent;
            handleInput(question);
        });
        
        // Add keyboard support for accessibility
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const question = item.querySelector('h3').textContent;
                handleInput(question);
            }
        });
    });

    // Voice Input Setup with better feedback
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        let isListening = false;

        voiceInput.addEventListener('click', () => {
            if (!isListening) {
                recognition.start();
                voiceInput.querySelector('i').classList.remove('fa-microphone');
                voiceInput.querySelector('i').classList.add('fa-microphone-slash');
                voiceInput.setAttribute('aria-label', 'Listening... Click to stop');
                
                // Add visual feedback
                searchInput.placeholder = "Listening...";
                voiceInput.classList.add('listening');
            } else {
                recognition.stop();
                voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
                voiceInput.querySelector('i').classList.add('fa-microphone');
                voiceInput.setAttribute('aria-label', 'Use voice input');
                
                // Reset feedback
                searchInput.placeholder = "Hello! I'm Nia, your AI assistant for the AI & Society course at TUM. How can I help you today?";
                voiceInput.classList.remove('listening');
            }
            isListening = !isListening;
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            handleInput(transcript);
            
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
            voiceInput.setAttribute('aria-label', 'Use voice input');
            searchInput.placeholder = "What's on your mind?";
            voiceInput.classList.remove('listening');
            isListening = false;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
            voiceInput.setAttribute('aria-label', 'Use voice input');
            searchInput.placeholder = "What's on your mind?";
            voiceInput.classList.remove('listening');
            isListening = false;
            
            // Show error feedback to user
            if (event.error === 'no-speech') {
                addMessage("I couldn't hear anything. Please try speaking again or type your question.", false);
            } else if (event.error === 'not-allowed' || event.error === 'permission-denied') {
                addMessage("Microphone access was denied. Please check your browser permissions.", false);
            } else {
                addMessage("Voice recognition had an error. You can type your question instead.", false);
            }
        };
    } else {
        voiceInput.style.display = 'none';
        // Expand the input field when voice input is not available
        searchInput.style.width = '100%';
    }

    // Add keyboard shortcut to collapse chat (Escape key)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && chatWindow.classList.contains('active')) {
            collapseChatWindow();
        }
    });

    // Privacy Policy and Contact Info modal fixes
    window.togglePrivacyPolicy = function() {
        const policyBox = document.getElementById("privacyContainer");
        if (policyBox.style.display === "none" || policyBox.style.display === "") {
            policyBox.style.display = "block"; 
        } else {
            policyBox.style.display = "none"; 
        }
    };
    
    window.closePrivacyPolicy = function() {
        document.getElementById("privacyContainer").style.display = "none";
    };
    
    window.toggleContactInfo = function() {
        const contactBox = document.getElementById("contactContainer");
        if (contactBox.style.display === "none" || contactBox.style.display === "") {
            contactBox.style.display = "block"; 
        } else {
            contactBox.style.display = "none"; 
        }
    };
    
    window.closeContactInfo = function() {
        document.getElementById("contactContainer").style.display = "none";
    };

    // Welcome message will be shown only after user interaction
    // Chat will not auto-open until user interacts with it
});
