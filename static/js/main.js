document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const messageForm = document.getElementById('messageForm');
    const userMessageInput = document.getElementById('userMessage');
    const conversationContainer = document.getElementById('conversationContainer');
    const resetBtn = document.getElementById('resetBtn');
    const levelSelect = document.getElementById('levelSelect');
    const topicSelect = document.getElementById('topicSelect');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const audioPlayer = document.getElementById('audioPlayer');
    const playButton = document.getElementById('playButton');
    const progressBar = document.getElementById('progressBar');
    const audioTime = document.getElementById('audioTime');
    
    // Audio elements
    let audioElement = null;
    let audioPlaying = false;
    
    // Message submission handler
    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = userMessageInput.value.trim();
        if (!message) return;
        
        // Show user message in the conversation
        addMessage('user', message);
        
        // Clear the input field
        userMessageInput.value = '';
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        
        try {
            // Get the current level and topic
            const level = levelSelect.value;
            const topic = topicSelect.value;
            
            // Send the message to the server
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    level: level,
                    topic: topic
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
            
            // Add the AI response to the conversation
            if (data.message) {
                addMessage('assistant', data.message);
                
                // Set up audio player if we have audio data
                if (data.audio) {
                    setupAudioPlayer(data.audio);
                }
            } else if (data.error) {
                showErrorMessage(data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.classList.add('d-none');
            showErrorMessage('Failed to get a response. Please try again.');
        }
    });
    
    // Reset conversation button
    resetBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });
            
            if (response.ok) {
                // Clear the conversation container
                conversationContainer.innerHTML = '';
                
                // Add initial system message
                const systemMessage = document.createElement('div');
                systemMessage.className = 'message-system text-center';
                systemMessage.innerHTML = '<p>Start a conversation by sending a message below. You can write in English or Spanish.</p>';
                conversationContainer.appendChild(systemMessage);
                
                // Hide audio player
                audioPlayer.classList.add('d-none');
                if (audioElement) {
                    audioElement.pause();
                    audioElement = null;
                }
            }
        } catch (error) {
            console.error('Error resetting conversation:', error);
        }
    });
    
    // Function to add a message to the conversation
    function addMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${role}`;
        
        // Format the message with line breaks
        const formattedContent = content.replace(/\n/g, '<br>');
        messageElement.innerHTML = formattedContent;
        
        conversationContainer.appendChild(messageElement);
        
        // Scroll to the bottom of the conversation
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
    
    // Function to show an error message
    function showErrorMessage(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'message-system text-danger';
        errorElement.textContent = message;
        conversationContainer.appendChild(errorElement);
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
    
    // Function to set up the audio player
    function setupAudioPlayer(audioBase64) {
        // Create a new audio element
        if (audioElement) {
            audioElement.pause();
        }
        
        // Create audio from base64
        const audioSrc = `data:audio/mp3;base64,${audioBase64}`;
        audioElement = new Audio(audioSrc);
        
        // Show audio player
        audioPlayer.classList.remove('d-none');
        
        // Reset play button icon
        playButton.innerHTML = '<i data-feather="play"></i>';
        feather.replace();
        audioPlaying = false;
        
        // Update progress bar as audio plays
        audioElement.addEventListener('timeupdate', updateProgressBar);
        
        // Reset when audio ends
        audioElement.addEventListener('ended', function() {
            playButton.innerHTML = '<i data-feather="play"></i>';
            feather.replace();
            audioPlaying = false;
            progressBar.style.width = '0%';
            audioTime.textContent = '0:00';
        });
        
        // Play button click handler
        playButton.onclick = function() {
            if (audioPlaying) {
                audioElement.pause();
                playButton.innerHTML = '<i data-feather="play"></i>';
                feather.replace();
                audioPlaying = false;
            } else {
                audioElement.play();
                playButton.innerHTML = '<i data-feather="pause"></i>';
                feather.replace();
                audioPlaying = true;
            }
        };
        
        // Auto-play the audio
        audioElement.play().then(() => {
            playButton.innerHTML = '<i data-feather="pause"></i>';
            feather.replace();
            audioPlaying = true;
        }).catch(error => {
            console.error('Auto-play failed:', error);
            // Just update the UI, user will need to click play manually
            playButton.innerHTML = '<i data-feather="play"></i>';
            feather.replace();
        });
    }
    
    // Update progress bar and time display for audio
    function updateProgressBar() {
        if (!audioElement) return;
        
        const percentage = (audioElement.currentTime / audioElement.duration) * 100;
        progressBar.style.width = `${percentage}%`;
        
        // Format current time
        const minutes = Math.floor(audioElement.currentTime / 60);
        const seconds = Math.floor(audioElement.currentTime % 60);
        const formattedTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        audioTime.textContent = formattedTime;
    }
});
