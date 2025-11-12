// Tab switching
function switchTab(tab) {
    const ingestSection = document.getElementById('ingestSection');
    const querySection = document.getElementById('querySection');
    const ingestTab = document.getElementById('ingestTab');
    const queryTab = document.getElementById('queryTab');

    if (tab === 'ingest') {
        ingestSection.classList.remove('hidden');
        querySection.classList.add('hidden');
        ingestTab.classList.add('tab-active');
        queryTab.classList.remove('tab-active');
    } else {
        ingestSection.classList.add('hidden');
        querySection.classList.remove('hidden');
        ingestTab.classList.remove('tab-active');
        queryTab.classList.add('tab-active');
    }
}

// INGEST FUNCTIONALITY
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const fileList = document.getElementById('fileList');
const uploadPrompt = document.getElementById('uploadPrompt');
const submitBtn = document.getElementById('submitBtn');
const processingState = document.getElementById('processingState');
const resultArea = document.getElementById('resultArea');

if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        fileInput.files = e.dataTransfer.files;
        displayFiles();
    });

    fileInput.addEventListener('change', displayFiles);
}

function displayFiles() {
    const files = fileInput.files;
    if (files.length > 0) {
        uploadPrompt.classList.add('hidden');
        fileList.classList.remove('hidden');
        fileList.innerHTML = '<p class="font-semibold text-slate-700 mb-2">Selected files:</p>';
        const ul = document.createElement('ul');
        ul.className = 'space-y-1';
        for (let file of files) {
            const li = document.createElement('li');
            li.className = 'flex items-center space-x-2 text-sm text-slate-600';
            li.innerHTML = `
                <svg class="w-4 h-4 text-indigo-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd"/>
                </svg>
                <span>${file.name} (${(file.size / 1024).toFixed(1)} KB)</span>
            `;
            ul.appendChild(li);
        }
        fileList.appendChild(ul);
    } else {
        uploadPrompt.classList.remove('hidden');
        fileList.classList.add('hidden');
    }
}

if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            showResult('error', 'Please select at least one file');
            return;
        }

        const formData = new FormData(uploadForm);
        formData.set('reset', document.getElementById('reset').checked);

        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
        processingState.classList.remove('hidden');
        resultArea.classList.add('hidden');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                showResult('success', result.message, result);
                fileInput.value = '';
                uploadPrompt.classList.remove('hidden');
                fileList.classList.add('hidden');
            } else {
                showResult('error', result.message);
            }
        } catch (error) {
            showResult('error', 'Network error: ' + error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            processingState.classList.add('hidden');
        }
    });
}

function showResult(type, message, data = null) {
    resultArea.classList.remove('hidden');
    
    if (type === 'success') {
        resultArea.innerHTML = `
            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex items-start">
                    <svg class="w-6 h-6 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <div class="ml-3">
                        <h3 class="text-sm font-semibold text-green-900">Success!</h3>
                        <p class="text-sm text-green-800 mt-1">${message}</p>
                        ${data ? `
                            <div class="mt-2 text-sm text-green-700">
                                <p>📊 <strong>Files:</strong> ${data.files}</p>
                                <p>📦 <strong>Chunks:</strong> ${data.chunks}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    } else {
        resultArea.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-start">
                    <svg class="w-6 h-6 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                    </svg>
                    <div class="ml-3">
                        <h3 class="text-sm font-semibold text-red-900">Error</h3>
                        <p class="text-sm text-red-800 mt-1">${message}</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// QUERY FUNCTIONALITY
const queryForm = document.getElementById('queryForm');
const queryBtn = document.getElementById('queryBtn');
const queryProcessingState = document.getElementById('queryProcessingState');
const queryResultArea = document.getElementById('queryResultArea');

if (queryForm) {
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const queryText = document.getElementById('query_text').value.trim();
        if (!queryText) {
            showQueryResult('error', 'Please enter a query');
            return;
        }

        const queryData = {
            query: queryText,
            persist_dir: document.getElementById('query_persist_dir').value,
            collection_name: document.getElementById('query_collection_name').value,
            k: parseInt(document.getElementById('top_k').value),
            ollama_model: document.getElementById('ollama_model').value.trim(),
            use_ollama: document.getElementById('use_ollama').checked
        };

        queryBtn.disabled = true;
        queryBtn.classList.add('opacity-50', 'cursor-not-allowed');
        queryProcessingState.classList.remove('hidden');
        queryResultArea.classList.add('hidden');

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(queryData)
            });

            const result = await response.json();

            if (result.success) {
                displayQueryResults(result);
            } else {
                showQueryResult('error', result.message);
            }
        } catch (error) {
            showQueryResult('error', 'Network error: ' + error.message);
        } finally {
            queryBtn.disabled = false;
            queryBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            queryProcessingState.classList.add('hidden');
        }
    });
}

function displayQueryResults(result) {
    queryResultArea.classList.remove('hidden');
    
    let html = '';

    // Ollama Answer
    if (result.ollama_answer) {
        html += `
            <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
                <div class="flex items-start space-x-3 mb-3">
                    <svg class="w-6 h-6 text-indigo-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                        <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                    </svg>
                    <div class="flex-1">
                        <h3 class="text-lg font-semibold text-indigo-900">🤖 AI Answer (${result.ollama_model})</h3>
                    </div>
                </div>
                <div class="text-slate-800 leading-relaxed whitespace-pre-wrap">${escapeHtml(result.ollama_answer)}</div>
            </div>
        `;
    }

    if (result.ollama_error) {
        html += `
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p class="text-sm text-yellow-800">⚠️ ${result.ollama_error}</p>
            </div>
        `;
    }

    // Retrieved Documents
    if (result.results && result.results.length > 0) {
        html += `
            <div class="mb-4">
                <h3 class="text-lg font-semibold text-slate-800 mb-3">📄 Retrieved Documents (${result.count})</h3>
            </div>
        `;

        result.results.forEach(doc => {
            html += `
                <div class="bg-white border border-slate-200 rounded-lg p-5 mb-4 hover:shadow-md transition">
                    <div class="flex items-start justify-between mb-2">
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800">
                            Rank #${doc.rank}
                        </span>
                        <span class="text-xs text-slate-500">${doc.source}</span>
                    </div>
                    <div class="mt-3">
                        <details class="group">
                            <summary class="cursor-pointer text-slate-700 hover:text-slate-900 font-medium mb-2 flex items-center space-x-2">
                                <span class="group-open:hidden">▶</span>
                                <span class="hidden group-open:inline">▼</span>
                                <span>Full Content</span>
                            </summary>
                            <div class="mt-2 p-4 bg-slate-50 rounded text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">${escapeHtml(doc.content)}</div>
                        </details>
                        <p class="text-sm text-slate-600 mt-2">${doc.preview}...</p>
                    </div>
                </div>
            `;
        });
    } else {
        html += `
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-8 text-center">
                <p class="text-slate-600">No matching documents found</p>
            </div>
        `;
    }

    queryResultArea.innerHTML = html;
}

function showQueryResult(type, message) {
    queryResultArea.classList.remove('hidden');
    
    if (type === 'error') {
        queryResultArea.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-start">
                    <svg class="w-6 h-6 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                    </svg>
                    <div class="ml-3">
                        <h3 class="text-sm font-semibold text-red-900">Error</h3>
                        <p class="text-sm text-red-800 mt-1">${message}</p>
                    </div>
                </div>
            </div>
        `;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
