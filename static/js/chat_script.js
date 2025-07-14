document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');

    // Function to add a message to the chat display
    function addMessage(sender, text, isUser = false, avatarSrc = null) {
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('d-flex', 'mb-2');

        if (isUser) {
            messageContainer.classList.add('justify-content-end');
        } else {
            messageContainer.classList.add('justify-content-start');
        }

        if (avatarSrc && !isUser) {
            const avatarImg = document.createElement('img');
            avatarImg.src = avatarSrc;
            avatarImg.classList.add('chat-avatar', 'me-2');
            messageContainer.appendChild(avatarImg);
        }

        const msgBubble = document.createElement('div');
        msgBubble.classList.add('msg-bubble', 'new');

        if (isUser) {
            msgBubble.classList.add('user-bubble');
        } else {
            msgBubble.classList.add('bot-bubble');
        }
        msgBubble.textContent = text;
        messageContainer.appendChild(msgBubble);
        chatMessages.appendChild(messageContainer); // Append the entire container

        setTimeout(() => msgBubble.classList.remove('new'), 300);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // CRITICAL CHANGE: Return the entire messageContainer (the outermost div)
        return messageContainer;
    }

    // Event listener for sending messages
    sendButton.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (query === '') return;

        addMessage('You', query, true);
        userInput.value = '';

        // Store a reference to the ENTIRE "Thinking..." message container
        const thinkingMessageContainer = addMessage('AI', 'Thinking...', false, '/static/images/doctor1.png');

        try {
            const response = await fetch('/get', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ response: 'Unknown error from server.' }));
                throw new Error(`HTTP error! Status: ${response.status}. Message: ${errorData.response || 'No specific error message.'}`);
            }

            const data = await response.json();
            const botAnswer = data.response;

            // --- CORRECTED HANDLING ---
            // 1. Remove the ENTIRE "Thinking..." message container
            if (thinkingMessageContainer && thinkingMessageContainer.parentNode) {
                thinkingMessageContainer.parentNode.removeChild(thinkingMessageContainer);
            }

            // 2. Add the final bot message once (no duplicate lines!)
            addMessage('AI', botAnswer, false, '/static/images/doctor1.png');
            // --- END CORRECTED HANDLING ---

        } catch (error) {
            console.error('Error fetching RAG response:', error);
            // Handle error: remove thinking bubble and add error message
            if (thinkingMessageContainer && thinkingMessageContainer.parentNode) {
                thinkingMessageContainer.parentNode.removeChild(thinkingMessageContainer);
            }
            addMessage('AI', `Error: ${error.message || 'Could not get an answer. Please try again.'}`, false, '/static/images/doctor1.png');
        } finally {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });

    // Allow sending messages with the Enter key
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
});


// ---- old version ----//
// document.addEventListener('DOMContentLoaded', function() {
//     const userInput = document.getElementById('user-input');
//     const sendButton = document.getElementById('send-button');
//     const chatMessages = document.getElementById('chat-messages'); // Ensure this ID matches your HTML chat box

//     // Function to add a message to the chat display
//     function addMessage(sender, text, isUser = false, avatarSrc = null) {
//         const messageContainer = document.createElement('div');
//         messageContainer.classList.add('d-flex', 'mb-2');

//         if (isUser) {
//             messageContainer.classList.add('justify-content-end');
//         } else {
//             messageContainer.classList.add('justify-content-start');
//         }

//         if (avatarSrc && !isUser) {
//             const avatarImg = document.createElement('img');
//             avatarImg.src = avatarSrc;
//             avatarImg.classList.add('chat-avatar', 'me-2');
//             messageContainer.appendChild(avatarImg);
//         }

//         const msgBubble = document.createElement('div');
//         msgBubble.classList.add('msg-bubble', 'new');

//         if (isUser) {
//             msgBubble.classList.add('user-bubble');
//         } else {
//             msgBubble.classList.add('bot-bubble');
//         }
//         msgBubble.textContent = text;
//         messageContainer.appendChild(msgBubble);
//         chatMessages.appendChild(messageContainer);

//         setTimeout(() => msgBubble.classList.remove('new'), 300);
//         chatMessages.scrollTop = chatMessages.scrollHeight;

//         return msgBubble; // Return the created message bubble element
//     }

//     // Event listener for sending messages
//     sendButton.addEventListener('click', async () => {
//         const query = userInput.value.trim();
//         if (query === '') return;

//         addMessage('You', query, true);
//         userInput.value = '';

//         const thinkingBubble = addMessage('AI', 'Thinking...', false, '/static/images/doctor1.png');

//         try {
//             const response = await fetch('/get', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify({ query: query })
//             });

//             if (!response.ok) {
//                 // Try to parse error message from Flask if available
//                 const errorData = await response.json().catch(() => ({ response: 'Unknown error from server.' }));
//                 throw new Error(`HTTP error! Status: ${response.status}. Message: ${errorData.response || 'No specific error message.'}`);
//             }

//             const data = await response.json();
//             const botAnswer = data.response; // <<< CRITICAL FIX: Use data.response, not data.answer

//             // --- FIX START ---
//             // 1. Remove the "Thinking..." bubble from its parent
           
//             // 2. Add the actual bot message using the addMessage function
//             addMessage('AI', botAnswer, false, '/static/images/doctor1.png'); // Add new message with image

//             // 2. Add the actual bot message using the addMessage function
//             addMessage('AI', botAnswer, false, '/static/images/doctor1.png');
//             // --- FIX END ---

//         } catch (error) {
//             console.error('Error fetching RAG response:', error);
//             // Update the thinking bubble with an error message, or add a new error message
//             if (thinkingBubble && thinkingBubble.parentNode) {
//                 thinkingBubble.parentNode.removeChild(thinkingBubble); // Remove thinking bubble
//             }
//             addMessage('AI', `Error: ${error.message || 'Could not get an answer. Please try again.'}`, false, '/static/images/doctor1.png');
//         } finally {
//             // Always scroll to bottom after an update or final answer
//             chatMessages.scrollTop = chatMessages.scrollHeight;
//         }
//     });

//     // Allow sending messages with the Enter key
//     userInput.addEventListener('keypress', function(e) {
//         if (e.key === 'Enter') {
//             sendButton.click();
//         }
//     });
// });