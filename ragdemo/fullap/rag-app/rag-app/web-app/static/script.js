// API Base URL
const API_BASE = '';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendBtnLoader = document.getElementById('sendBtnLoader');
const loadDataBtn = document.getElementById('loadDataBtn');
const clearBtn = document.getElementById('clearBtn');
const refreshBtn = document.getElementById('refreshBtn');
const systemStatus = document.getElementById('systemStatus');
const documentCount = document.getElementById('documentCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    loadDataBtn.addEventListener('click', loadSampleData);
    clearBtn.addEventListener('click', clearVectorStore);
    refreshBtn.addEventListener('click', checkStatus);
}

// Check System Status
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.success) {
            systemStatus.textContent = data.collection_ready ? '✅ Ready' : '⚠️ No Data';
            systemStatus.style.background = data.collection_ready ? '#d4edda' : '#fff3cd';
            systemStatus.style.color = data.collection_ready ? '#155724' : '#856404';
            systemStatus.style.borderColor = data.collection_ready ? '#28a745' : '#ffc107';
            documentCount.textContent = data.document_count;
        }
    } catch (error) {
        console.error('Status check error:', error);
        systemStatus.textContent = '❌ Error';
        systemStatus.style.background = '#f8d7da';
        systemStatus.style.color = '#721c24';
        systemStatus.style.borderColor = '#dc3545';
    }
}

// Load Sample Data
async function loadSampleData() {
    loadDataBtn.disabled = true;
    loadDataBtn.textContent = '⏳ Loading...';
    
    try {
        const response = await fetch(`${API_BASE}/api/load-sample-data`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addSystemMessage(`✅ ${data.message}`);
            checkStatus();
        } else {
            addSystemMessage(`❌ ${data.message}`, true);
        }
    } catch (error) {
        console.error('Load data error:', error);
        addSystemMessage(`❌ Error loading data: ${error.message}`, true);
    } finally {
        loadDataBtn.disabled = false;
        loadDataBtn.textContent = '📖 Load Sample Data';
    }
}

// Clear Vector Store
async function clearVectorStore() {
    if (!confirm('Are you sure you want to clear all documents?')) {
        return;
    }
    
    clearBtn.disabled = true;
    clearBtn.textContent = '⏳ Clearing...';
    
    try {
        const response = await fetch(`${API_BASE}/api/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addSystemMessage('✅ Vector store cleared successfully');
            checkStatus();
            
            // Clear chat messages except system message
            chatMessages.innerHTML = `
                <div class="message system-message">
                    <div class="message-content">
                        👋 Welcome! Load sample data or upload documents to get started.
                    </div>
                </div>
            `;
        } else {
            addSystemMessage(`❌ ${data.message}`, true);
        }
    } catch (error) {
        console.error('Clear error:', error);
        addSystemMessage(`❌ Error clearing vector store: ${error.message}`, true);
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent = '🗑️ Clear Vector Store';
    }
}

// Send Message
async function sendMessage() {
    const question = questionInput.value.trim();
    
    if (!question) {
        return;
    }
    
    // Add user message to chat
    addUserMessage(question);
    
    // Clear input
    questionInput.value = '';
    
    // Disable send button
    sendBtn.disabled = true;
    sendBtnText.style.display = 'none';
    sendBtnLoader.style.display = 'inline-block';
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addAssistantMessage(data.answer, data.sources);
        } else {
            addSystemMessage(`❌ ${data.message}`, true);
        }
    } catch (error) {
        console.error('Query error:', error);
        addSystemMessage(`❌ Error processing query: ${error.message}`, true);
    } finally {
        sendBtn.disabled = false;
        sendBtnText.style.display = 'inline';
        sendBtnLoader.style.display = 'none';
    }
}

// Add User Message
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-label">You</div>
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add Assistant Message
function addAssistantMessage(text, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    
    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="sources">
                <div class="sources-title">📚 Sources:</div>
                ${sources.map((source, i) => `
                    <div class="source-item">
                        <div class="source-text">${escapeHtml(source)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-label">Assistant</div>
        <div class="message-content">
            ${escapeHtml(text)}
            ${sourcesHtml}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Add System Message
function addSystemMessage(text, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isError ? 'error-message' : 'system-message'}`;
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
