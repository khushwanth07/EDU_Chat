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

    // Chat Window Management Functions
    function showChatWindow() {
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
                    chatWindow.scrollIntoView({ behavior: 'smooth' });
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
        textSpan.textContent = message;
        messageDiv.appendChild(textSpan);

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

    // Function to handle user input
    function handleInput(inputText) {
        if (!inputText.trim()) return;

        // Display user message
        addMessage(inputText, true);

        // Show chat window
        showChatWindow();

        // Display typing indicator
        const typingIndicator = showTypingIndicator();

        // Fetch response from backend
        fetch('http://127.0.0.1:5000/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: inputText })
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                typingIndicator.remove();
                addMessage(data.response, false);
            })
            .catch((error) => {
                typingIndicator.remove();
                console.error('Error fetching response:', error);
                addMessage('Sorry, something went wrong. Please try again.', false);
            });
    }

    // Event Listeners
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            handleInput(searchInput.value.trim());
            searchInput.value = '';
        }
    });

    // Clear chat functionality
    clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            chatMessages.innerHTML = '';
            collapseChatWindow();
            // Optional: Add a system message
            setTimeout(() => {
                addMessage('Chat history has been cleared. How can I help you?', false);
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
    });

    // Voice Input Setup
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
            } else {
                recognition.stop();
                voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
                voiceInput.querySelector('i').classList.add('fa-microphone');
            }
            isListening = !isListening;
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            handleInput(transcript);
            
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
            isListening = false;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceInput.querySelector('i').classList.remove('fa-microphone-slash');
            voiceInput.querySelector('i').classList.add('fa-microphone');
            isListening = false;
        };
    } else {
        voiceInput.style.display = 'none';
    }

    // Add keyboard shortcut to collapse chat (Escape key)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && chatWindow.classList.contains('active')) {
            collapseChatWindow();
        }
    });
});