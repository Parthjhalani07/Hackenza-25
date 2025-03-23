document.addEventListener('DOMContentLoaded', () => {
    const pendingQueryList = document.getElementById('pendingQueryList');
    const verifiedQueryList = document.getElementById('verifiedQueryList');
    const selectedQueryText = document.getElementById('selectedQueryText');

    // Mock data for testing
    const mockData = {
        pending: [
            { id: 1, text: 'What should I do if I miss a dose of Metformin?' },
            { id: 2, text: 'Can I take Lisinopril with food?' }
        ],
        verified: [
            { id: 3, text: 'How often should I check my blood pressure?' }
        ]
    };

    // Load pending queries
    function loadPendingQueries() {
        pendingQueryList.innerHTML = '';
        mockData.pending.forEach(query => {
            const queryItem = document.createElement('div');
            queryItem.classList.add('query-item');
            queryItem.innerHTML = `
                <p>${query.text}</p>
                <div class="actions">
                    <button class="btn-grad" onclick="selectQuery(${query.id}, '${query.text}')">Select</button>
                </div>
            `;
            pendingQueryList.appendChild(queryItem);
        });
    }

    // Load verified queries
    function loadVerifiedQueries() {
        verifiedQueryList.innerHTML = '';
        mockData.verified.forEach(query => {
            const queryItem = document.createElement('div');
            queryItem.classList.add('query-item');
            queryItem.innerHTML = `
                <p>${query.text}</p>
            `;
            verifiedQueryList.appendChild(queryItem);
        });
    }

    // Select a query from pending queries
    window.selectQuery = function(id, text) {
        selectedQueryText.textContent = text;
    }

    // Verify the current query
    window.verifyResponse = function() {
        const response = document.getElementById('currentQueryResponse').value;
        if (response.trim()) {
            alert("Response verified successfully!");
        } else {
            alert("Please enter a response before verifying.");
        }
    }

    // Edit the current query
    window.editResponse = function() {
        const response = document.getElementById('currentQueryResponse').value;
        if (response.trim()) {
            alert("Response edited successfully!");
        } else {
            alert("Please enter a response before editing.");
        }
    }

    // Load initial data
    loadPendingQueries();
    loadVerifiedQueries();
});