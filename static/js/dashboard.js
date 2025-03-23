// Handle query form submission
document.getElementById('queryForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const queryInput = document.getElementById('queryInput').value.trim();
    const aiResponseElement = document.getElementById('aiResponse');
    
    // Clear the AI response area and show loading indicator
    aiResponseElement.value = "Generating response...";
    
    if (queryInput === '') {
        alert('Please enter a valid query.');
        aiResponseElement.value = "";
        return;
    }
    
    try {
        // Get patient ID from localStorage (set during login)
        const patientId = localStorage.getItem('patientId');
        const chatId = localStorage.getItem('currentChatId'); // Optional, can be null for new chat
        
        // Send the query to the backend for AI processing
        const response = await fetch('/api/ai_query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query_text: queryInput,
                patient_id: patientId,
                chat_id: chatId
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display the AI response
            aiResponseElement.value = data.response;
            
            // Store the chat ID for future queries in the same conversation
            if (data.chat_id) {
                localStorage.setItem('currentChatId', data.chat_id);
            }
            
            // Update the query list
            displayQueries(patientId);
        } else {
            aiResponseElement.value = "Error: " + data.message;
            console.error("Error from server:", data.message);
        }
    } catch (error) {
        aiResponseElement.value = "Error connecting to the server. Please try again.";
        console.error('Error submitting query:', error);
    }
});

// Updated displayQueries function to work with our backend
async function displayQueries(patientId) {
    const queryList = document.getElementById('queryList');
    queryList.innerHTML = '<p>Loading query history...</p>'; // Loading indicator
    
    try {
        // Fetch queries from our backend
        const response = await fetch(`/api/queries?patientId=${patientId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const queries = await response.json();
        queryList.innerHTML = ''; // Clear loading message
        
        if (queries.length === 0) {
            queryList.innerHTML = '<p>No previous queries found.</p>';
            return;
        }
        
        queries.forEach(query => {
            const queryItem = document.createElement('div');
            queryItem.classList.add('query-item');
            
            // Add a class based on verification status
            if (query.status === 'Verified' || query.status === 'Completed') {
                queryItem.classList.add('verified');
            } else {
                queryItem.classList.add('unverified');
            }
            
            queryItem.innerHTML = `
                <h3>${query.query_text}</h3>
                <p><strong>Status:</strong> <span class="status">${query.status}</span></p>
                ${query.response ? `<p><strong>Response:</strong> ${query.response}</p>` : ''}
                <p class="query-date">Asked on: ${new Date(query.created_at).toLocaleString()}</p>
            `;
            
            queryList.appendChild(queryItem);
        });
    } catch (error) {
        console.error('Error fetching queries:', error);
        queryList.innerHTML = '<p>Error loading queries. Please try again later.</p>';
    }
}