// script.js

let chatHistoryData = [];

// Function to convert Markdown-like syntax to sanitized HTML
function formatAnswer(answer) {
    let md = window.markdownit();
    let dirty = md.render(answer);
    let clean = DOMPurify.sanitize(dirty);
    return clean;
}

// Add message to chat history with timestamp
function addMessageToHistory(sender, message, quickReplies = []) {
    let chatHistory = $('#chat-history');
    let time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Determine if the message is from the user or bot
    let senderClass = sender === 'user' ? 'user' : 'bot';

    // Format the message content
    let messageContent = sender === 'bot' ? formatAnswer(message) : message;

    // Construct the message HTML
    let messageHtml = `
    <div class="chat-message ${senderClass}">
        <div class="chat-bubble ${senderClass}-bubble" role="dialog" aria-label="${senderClass === 'user' ? 'User' : 'Bot'} message at ${time}">
            <div class="message">${messageContent}</div>
            <div class="metadata">${time}</div>
        </div>
    </div>`;

    // Append the message to the chat history
    chatHistory.append(messageHtml);
    chatHistory.scrollTop(chatHistory[0].scrollHeight);

    // Add the message to chatHistoryData
    chatHistoryData.push({ sender: sender, message: message });

    // Add quick replies if available (only for bot messages)
    if (sender === 'bot' && quickReplies.length > 0) {
        addQuickReplies(quickReplies);
    }
}


// Function to add quick reply buttons
function addQuickReplies(quickReplies) {
    let chatHistory = $('#chat-history');
    let quickReplyContainer = $('<div class="quick-replies" role="group" aria-label="Quick reply options"></div>');

    quickReplies.forEach(reply => {
        let button = $('<button class="quick-reply-btn"></button>').text(reply);
        button.on('click', function() {
            // Simulate user sending the selected quick reply
            addMessageToHistory('user', reply);
            $('#question').val('');  // Clear the textarea

            // Remove quick replies after selection
            $('.quick-replies').remove();

            // Send the quick reply back to the backend
            sendMessage(reply);
        });
        quickReplyContainer.append(button);
    });

    chatHistory.append(quickReplyContainer);
    chatHistory.scrollTop(chatHistory[0].scrollHeight);
}

// Function to show typing indicator
function showTypingIndicator() {
    let typingIndicator = `
    <div class="chat-bubble bot-bubble typing" id="typing-indicator" aria-label="Bot is typing">
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    </div>`;
    $('#chat-history').append(typingIndicator);
    $('#chat-history').scrollTop($('#chat-history')[0].scrollHeight);
}

// Function to hide typing indicator
function hideTypingIndicator() {
    $('#typing-indicator').remove();
}

// Function to send message to backend
function sendMessage(message) {
    // Remove any existing quick replies
    $('.quick-replies').remove();

    // Show typing indicator immediately
    showTypingIndicator();

    // Prepare data to send
    let dataToSend = {
        question: message,
        chat_history: chatHistoryData
    };

    // Send the user's message to the backend
    $.ajax({
        type: 'POST',
        url: '/query',
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function(response) {
            // Hide typing indicator
            hideTypingIndicator();

            if (response.error) {
                addMessageToHistory('bot', response.error);
            } else {
                // Add the bot's answer to the chat history
                addMessageToHistory('bot', response.answer, response.quickReplies || []);
            }
        },
        error: function(xhr, status, error) {
            // Hide typing indicator
            hideTypingIndicator();
            let errorMessage = "Something went wrong. Please try again.";
            if (xhr.status === 400) {
                let errorResponse = JSON.parse(xhr.responseText);
                errorMessage = errorResponse.error || errorMessage;
            }
            addMessageToHistory('bot', errorMessage);
        }
    });
}

// Initial welcome message
function displayWelcomeMessage() {
    let welcomeMessage = "Hi there! 👋 I'm your Flight Policy Assistant. How can I help you today?";
    addMessageToHistory('bot', welcomeMessage);
}

// Handle sending messages
$('#send-button').on('click', function(e) {
    e.preventDefault();
    let question = $('#question').val().trim();
    if (question === '') return;

    // Add the user's message to the chat history
    addMessageToHistory('user', question);
    $('#question').val('');  // Clear the textarea

    // Send the message
    sendMessage(question);
});

// Submit on Enter key (without shift for new line)
$('#question').on('keypress', function(e) {
    if (e.which === 13 && !e.shiftKey) {
        e.preventDefault();
        $('#send-button').click();
    }
});

// Dynamically adjust the height of the input box
$('#question').on('input', function() {
    this.style.height = '45px';  // Reset the height
    this.style.height = (this.scrollHeight) + 'px';  // Adjust the height to fit content
});

// Call the welcome message when the page loads
$(document).ready(function() {
    displayWelcomeMessage();
});
