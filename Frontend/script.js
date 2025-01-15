document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.querySelector('.search-input');
    const voiceInput = document.querySelector('.voice-input');
    const chatWindow = document.querySelector('.chat-window');
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input input');
    const sendButton = document.querySelector('.send-button');
    const faqItems = document.querySelectorAll('.faq-item');

    // Chat Functions
    function showChatWindow() {
        chatWindow.classList.add('active');
        chatInput.focus();
    }

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

    function handleSearch(question) {
        showChatWindow();
        addMessage(question, true);
        
        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        // Simulate response (replace with actual API call)
        setTimeout(() => {
            typingIndicator.remove();
            addMessage(`Here's what I found about "${question}". This is a simulated response that would be replaced with actual backend integration.`);
        }, 1500);
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

    // Event Listeners
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            handleSearch(searchInput.value.trim());
            searchInput.value = '';
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim()) {
            handleSearch(chatInput.value.trim());
            chatInput.value = '';
        }
    });

    sendButton.addEventListener('click', () => {
        if (chatInput.value.trim()) {
            handleSearch(chatInput.value.trim());
            chatInput.value = '';
        }
    });

    // FAQ Items Click Handlers
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const question = item.querySelector('h3').textContent;
            handleSearch(question);
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
            searchInput.value = transcript;
            handleSearch(transcript);
            
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

    // Responsive Design Handler
    function handleResize() {
        if (window.innerWidth <= 768) {
            chatWindow.style.height = `${window.innerHeight}px`;
        } else {
            chatWindow.style.height = '500px';
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    // Message Styling
    const messageStyles = {
        user: {
            backgroundColor: '#3070B3',
            color: '#FFFFFF',
            borderRadius: '1rem 1rem 0 1rem'
        },
        bot: {
            backgroundColor: '#E8ECEF',
            color: '#14191A',
            borderRadius: '1rem 1rem 1rem 0'
        }
    };

    // Apply styles to messages
    function styleMessages() {
        const messages = document.querySelectorAll('.message');
        messages.forEach(message => {
            const isUser = message.classList.contains('user-message');
            const styles = isUser ? messageStyles.user : messageStyles.bot;
            Object.assign(message.style, styles);
            message.style.padding = '1rem';
            message.style.marginBottom = '1rem';
            message.style.maxWidth = '80%';
            message.style.alignSelf = isUser ? 'flex-end' : 'flex-start';
        });
    }

    // Observer for dynamic message styling
    const observer = new MutationObserver(() => {
        styleMessages();
    });

    observer.observe(chatMessages, {
        childList: true,
        subtree: true
    });
});