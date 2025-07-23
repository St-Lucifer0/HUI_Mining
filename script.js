// Global state
let currentView = 'client';
let currentTab = 'transactions';
let currentServerTab = 'federation';
let selectedClient = null;
let miningInProgress = false;
let currentMiningJobId = null;
let miningProgressInterval = null;

// WebSocket connection for real-time updates
let socket = null;

// Initialize WebSocket connection
function initializeWebSocket() {
    // Load Socket.IO from CDN
    if (typeof io === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
        script.onload = () => {
            connectWebSocket();
        };
        document.head.appendChild(script);
    } else {
        connectWebSocket();
    }
}

function connectWebSocket() {
    socket = io('http://localhost:5000');
    
    socket.on('connect', function() {
        console.log('Connected to Federated HUIM System via WebSocket');
        // Join general room for updates
        socket.emit('join_room', {room: 'general'});
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
    });
    
    socket.on('status', function(data) {
        console.log('Server status:', data.message);
        showNotification(data.message, 'info');
    });
    
    socket.on('federation_update', function(data) {
        updateFederationStatus(data);
    });
    
    socket.on('clients_update', function(data) {
        updateClientsDisplay(data);
    });
    
    socket.on('patterns_update', function(data) {
        updatePatternsDisplay(data);
    });
    
    // Mining-specific WebSocket events
    socket.on('mining_progress', function(data) {
        updateMiningProgress(data);
    });
    
    socket.on('mining_complete', function(data) {
        handleMiningComplete(data);
    });
    
    socket.on('mining_error', function(data) {
        handleMiningError(data);
    });
}

// Real-time update functions
function updateFederationStatus(data) {
    // Update federation status display
    const progressElement = document.querySelector('.training-progress .progress-fill');
    const progressText = document.querySelector('.training-progress .progress-text');
    
    if (progressElement && data.progress) {
        progressElement.style.width = `${data.progress * 100}%`;
    }
    
    if (progressText && data.round) {
        progressText.textContent = `Round ${data.round} - ${Math.round(data.progress * 100)}%`;
    }
}

function updateClientsDisplay(clients) {
    // Update client status displays
    clients.forEach(client => {
        const clientElement = document.querySelector(`[data-client-id="${client.id}"]`);
        if (clientElement) {
            const statusIcon = clientElement.querySelector('.status-icon');
            if (statusIcon) {
                statusIcon.textContent = client.status === 'healthy' ? '✅' : '⚠️';
                statusIcon.className = `status-icon ${client.status}`;
            }
        }
    });
}

function updatePatternsDisplay(patterns) {
    // Update patterns table with real-time data
    console.log('Updated patterns received:', patterns.length);
}

function showNotification(message, type = 'info') {
    // Create and show notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'info' ? '#3b82f6' : '#ef4444'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Request real-time updates
function requestRealTimeUpdates() {
    if (socket && socket.connected) {
        socket.emit('request_update', {type: 'all'});
    }
}

// Mining progress monitoring functions
function monitorMiningProgress(jobId) {
    // Clear any existing interval
    if (miningProgressInterval) {
        clearInterval(miningProgressInterval);
    }
    
    // Poll mining status every 2 seconds
    miningProgressInterval = setInterval(async () => {
        try {
            const status = await API.getMiningStatus('client-1', jobId);
            if (status.success) {
                updateMiningProgress({
                    jobId: jobId,
                    progress: status.data.progress,
                    status: status.data.status
                });
                
                if (status.data.status === 'completed' || status.data.status === 'failed') {
                    clearInterval(miningProgressInterval);
                    miningProgressInterval = null;
                }
            }
        } catch (error) {
            console.error('Failed to get mining status:', error);
        }
    }, 2000);
}

function updateMiningProgress(data) {
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    const progressStatus = document.getElementById('progress-status');
    
    if (progressFill && data.progress !== undefined) {
        progressFill.style.width = `${data.progress * 100}%`;
    }
    
    if (progressPercent && data.progress !== undefined) {
        progressPercent.textContent = `${Math.round(data.progress * 100)}%`;
    }
    
    if (progressStatus && data.status) {
        progressStatus.textContent = data.status;
    }
}

function handleMiningComplete(data) {
    showNotification(`Mining completed! Found ${data.totalPatterns} high-utility itemsets.`, 'info');
    
    // Update mining status
    miningInProgress = false;
    currentMiningJobId = null;
    
    // Update button
    const startButton = document.getElementById('start-mining');
    if (startButton) {
        startButton.innerHTML = '<span class="icon">▶️</span> Start Mining';
        startButton.className = 'btn btn-primary';
    }
    
    // Update progress to 100%
    updateMiningProgress({
        progress: 1.0,
        status: 'Completed successfully'
    });
    
    // Update patterns display
    if (data.results && data.results.length > 0) {
        updatePatternsTable(data.results);
    }
    
    // Clear monitoring interval
    if (miningProgressInterval) {
        clearInterval(miningProgressInterval);
        miningProgressInterval = null;
    }
}

function handleMiningError(data) {
    showNotification(`Mining failed: ${data.error}`, 'error');
    
    // Reset mining state
    miningInProgress = false;
    currentMiningJobId = null;
    
    // Update button
    const startButton = document.getElementById('start-mining');
    if (startButton) {
        startButton.innerHTML = '<span class="icon">▶️</span> Start Mining';
        startButton.className = 'btn btn-primary';
    }
    
    // Update progress status
    updateMiningProgress({
        status: `Error: ${data.error}`
    });
    
    // Clear monitoring interval
    if (miningProgressInterval) {
        clearInterval(miningProgressInterval);
        miningProgressInterval = null;
    }
}

function updatePatternsTable(patterns) {
    // Find patterns table and update it with real results
    const patternsTable = document.querySelector('#patterns-tab .data-table tbody');
    if (patternsTable) {
        patternsTable.innerHTML = '';
        
        patterns.forEach((pattern, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>P${index + 1}</td>
                <td>
                    <div class="itemset-tags">
                        ${pattern.itemset.map(item => `<span class="itemset-tag">${item}</span>`).join('')}
                    </div>
                </td>
                <td>${pattern.utility.toFixed(2)}</td>
                <td>${pattern.support}</td>
                <td>${(pattern.confidence * 100).toFixed(1)}%</td>
                <td><span class="trend-indicator up">↗</span></td>
                <td>
                    <button class="action-btn" title="View Details">
                        <span class="icon">👁️</span>
                    </button>
                    <button class="action-btn" title="Export">
                        <span class="icon">📤</span>
                    </button>
                </td>
            `;
            patternsTable.appendChild(row);
        });
    }
}

// View switching
function switchView(view) {
    currentView = view;
    
    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.closest('.nav-tab').classList.add('active');
    
    // Update view containers
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    document.getElementById(`${view}-view`).classList.add('active');
}

// Client tab switching
function switchTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('#client-view .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('#client-view .tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// Server tab switching
function switchServerTab(tab) {
    currentServerTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('#server-view .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('#server-view .tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tab}-tab`).classList.add('active');
}

// Mining controls
function initializeMiningControls() {
    const utilitySlider = document.getElementById('utility-threshold');
    const supportSlider = document.getElementById('support-threshold');
    const utilityValue = document.getElementById('utility-value');
    const supportValue = document.getElementById('support-value');
    const startButton = document.getElementById('start-mining');
    
    if (utilitySlider && utilityValue) {
        utilitySlider.addEventListener('input', function() {
            utilityValue.textContent = this.value;
        });
    }
    
    if (supportSlider && supportValue) {
        supportSlider.addEventListener('input', function() {
            supportValue.textContent = this.value + '.0';
        });
    }
    
    if (startButton) {
        startButton.addEventListener('click', function() {
            if (!miningInProgress) {
                startMining();
            } else {
                stopMining();
            }
        });
    }
}

function startMining() {
    miningInProgress = true;
    const startButton = document.getElementById('start-mining');
    const progressSection = document.getElementById('mining-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    const progressStatus = document.getElementById('progress-status');
    
    // Update button
    startButton.innerHTML = '<span class="icon">⏹️</span> Stop Mining';
    startButton.className = 'btn btn-secondary';
    
    // Get mining configuration from UI
    const utilityThreshold = document.getElementById('utility-threshold')?.value || 100;
    const supportThreshold = document.getElementById('support-threshold')?.value || 2;
    const privacyEnabled = document.getElementById('privacy-enabled')?.checked || false;
    const epsilon = document.getElementById('epsilon-value')?.value || 1.0;
    
    const miningConfig = {
        utilityThreshold: parseFloat(utilityThreshold),
        supportThreshold: parseFloat(supportThreshold),
        privacyEnabled: privacyEnabled,
        epsilon: parseFloat(epsilon)
    };
    
    // Start real mining via API
    API.startMining('client-1', miningConfig)
        .then(response => {
            if (response.success) {
                currentMiningJobId = response.data.id;
                showNotification('Mining started successfully!', 'info');
                
                // Show progress section
                if (progressSection) {
                    progressSection.style.display = 'block';
                }
                
                // Start monitoring mining progress
                monitorMiningProgress(currentMiningJobId);
            } else {
                throw new Error(response.error || 'Failed to start mining');
            }
        })
        .catch(error => {
            console.error('Mining start failed:', error);
            showNotification('Failed to start mining: ' + error.message, 'error');
            stopMining();
        });
    
    // Show progress section
    progressSection.style.display = 'block';
    
    // Simulate mining progress
    let progress = 0;
    const progressSteps = [
        "Initializing FP-Growth algorithm...",
        "Building FP-Tree structure...",
        "Mining frequent patterns...",
        "Calculating utility scores...",
        "Mining completed successfully!"
    ];
    
    const interval = setInterval(() => {
        progress += 10;
        progressFill.style.width = progress + '%';
        progressPercent.textContent = progress + '%';
        
        if (progress < 30) {
            progressStatus.textContent = progressSteps[0];
        } else if (progress < 60) {
            progressStatus.textContent = progressSteps[1];
        } else if (progress < 90) {
            progressStatus.textContent = progressSteps[2];
        } else if (progress < 100) {
            progressStatus.textContent = progressSteps[3];
        } else {
            progressStatus.textContent = progressSteps[4];
            clearInterval(interval);
            setTimeout(() => {
                stopMining();
            }, 2000);
        }
    }, 500);
}

function stopMining() {
    miningInProgress = false;
    const startButton = document.getElementById('start-mining');
    const progressSection = document.getElementById('mining-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressPercent = document.getElementById('progress-percent');
    const progressStatus = document.getElementById('progress-status');
    
    // Update button
    startButton.innerHTML = '<span class="icon">▶️</span> Start Mining';
    startButton.className = 'btn btn-success';
    
    // Reset progress
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
    progressStatus.textContent = 'Ready to start mining...';
    
    // Hide progress section after a delay
    setTimeout(() => {
        progressSection.style.display = 'none';
    }, 1000);
}

// Client monitoring
function selectClient(clientId) {
    selectedClient = clientId;
    
    // Update active client in list
    document.querySelectorAll('.client-monitor-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.client-monitor-item').classList.add('active');
    
    // Update client details
    updateClientDetails(clientId);
}

function updateClientDetails(clientId) {
    const detailsContent = document.getElementById('client-details-content');
    
    const clientData = {
        'client-1': {
            name: 'Electronics Retail Store',
            status: 'Healthy',
            lastUpdate: '2 min ago',
            transactions: '2,847',
            patterns: '156',
            dataQuality: 94,
            contributionScore: 85,
            localAccuracy: 89.2,
            networkLatency: 45
        },
        'client-2': {
            name: 'Fashion Retail Store',
            status: 'Healthy',
            lastUpdate: '1 min ago',
            transactions: '1,923',
            patterns: '134',
            dataQuality: 98,
            contributionScore: 92,
            localAccuracy: 91.7,
            networkLatency: 32
        },
        'client-3': {
            name: 'Home & Garden Store',
            status: 'Warning',
            lastUpdate: '5 min ago',
            transactions: '1,456',
            patterns: '112',
            dataQuality: 87,
            contributionScore: 78,
            localAccuracy: 83.6,
            networkLatency: 89
        }
    };
    
    const client = clientData[clientId];
    if (!client) return;
    
    const statusClass = client.status.toLowerCase();
    const latencyClass = client.networkLatency < 100 ? 'positive' : 
                        client.networkLatency < 200 ? 'warning' : 'negative';
    
    detailsContent.innerHTML = `
        <div class="client-details-header">
            <h3>Client Details</h3>
        </div>
        
        <div class="detail-section">
            <div class="detail-item">
                <div class="detail-label">Client Name</div>
                <div class="detail-value">${client.name}</div>
            </div>
            
            <div class="detail-item">
                <div class="detail-label">Status</div>
                <div class="detail-value ${statusClass}">${client.status}</div>
            </div>
            
            <div class="detail-item">
                <div class="detail-label">Last Update</div>
                <div class="detail-value">${client.lastUpdate}</div>
            </div>
            
            <div class="detail-item">
                <div class="detail-label">Transactions</div>
                <div class="detail-value">${client.transactions}</div>
            </div>
            
            <div class="detail-item">
                <div class="detail-label">Local Patterns</div>
                <div class="detail-value">${client.patterns}</div>
            </div>
        </div>
        
        <div class="performance-section">
            <h4>Performance Metrics</h4>
            
            <div class="metric-item">
                <div class="metric-header">
                    <span>Data Quality</span>
                    <span>${client.dataQuality}%</span>
                </div>
                <div class="progress-bar large">
                    <div class="progress-fill" style="width: ${client.dataQuality}%"></div>
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-header">
                    <span>Contribution Score</span>
                    <span>${client.contributionScore}%</span>
                </div>
                <div class="progress-bar large">
                    <div class="progress-fill" style="width: ${client.contributionScore}%"></div>
                </div>
            </div>
            
            <div class="metric-item">
                <div class="metric-header">
                    <span>Local Accuracy</span>
                    <span>${client.localAccuracy}%</span>
                </div>
                <div class="progress-bar large">
                    <div class="progress-fill" style="width: ${client.localAccuracy}%"></div>
                </div>
            </div>
            
            <div class="latency-item">
                <span class="detail-label">Network Latency:</span>
                <span class="detail-value ${latencyClass}">${client.networkLatency}ms</span>
            </div>
        </div>
        
        ${client.status !== 'Healthy' ? `
        <div class="warning-section">
            <div class="warning-content">
                <span class="warning-icon">⚠️</span>
                <div>
                    <div class="warning-title">Performance Warning</div>
                    <div class="warning-text">Client showing degraded performance. Monitor data quality and network connectivity.</div>
                </div>
            </div>
        </div>
        ` : ''}
    `;
}

// Chart animation
function animateCharts() {
    const chartBars = document.querySelectorAll('.chart-bar');
    chartBars.forEach((bar, index) => {
        setTimeout(() => {
            bar.style.opacity = '1';
            bar.style.transform = 'scaleY(1)';
        }, index * 100);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMiningControls();
    initializeWebSocket();
    
    // Request initial real-time updates every 30 seconds
    setInterval(requestRealTimeUpdates, 30000);
    
    // Add some initial styling for chart animation
    const chartBars = document.querySelectorAll('.chart-bar');
    chartBars.forEach(bar => {
        bar.style.opacity = '0';
        bar.style.transform = 'scaleY(0)';
        bar.style.transformOrigin = 'bottom';
        bar.style.transition = 'all 0.5s ease';
    });
    
    // Animate charts after a short delay
    setTimeout(animateCharts, 500);
    
    // Add hover effects to interactive elements
    addHoverEffects();
});

function addHoverEffects() {
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card, .summary-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Add click effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
}

// Utility functions for API integration
const API = {
    baseUrl: 'http://localhost:5000/api', // Flask API server URL
    
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Transaction endpoints
    async getTransactions(clientId) {
        return this.request(`/clients/${clientId}/transactions`);
    },
    
    async createTransaction(clientId, transaction) {
        return this.request(`/clients/${clientId}/transactions`, {
            method: 'POST',
            body: JSON.stringify(transaction)
        });
    },
    
    // Mining endpoints
    async startMining(clientId, config) {
        return this.request(`/clients/${clientId}/mining/start`, {
            method: 'POST',
            body: JSON.stringify(config)
        });
    },
    
    async getMiningStatus(clientId, jobId) {
        return this.request(`/clients/${clientId}/mining/${jobId}/status`);
    },
    
    // Federation endpoints
    async getFederationStatus() {
        return this.request('/federation/status');
    },
    
    async getGlobalPatterns() {
        return this.request('/federation/patterns');
    },
    
    async getClients() {
        return this.request('/federation/clients');
    }
};

// Example of how to use the API
async function loadTransactions() {
    try {
        const transactions = await API.getTransactions('client-1');
        console.log('Loaded transactions:', transactions);
        // Update UI with real data
    } catch (error) {
        console.error('Failed to load transactions:', error);
        // Show error message to user
    }
}

// Export for use in other scripts
window.HUIM = {
    API,
    switchView,
    switchTab,
    switchServerTab,
    selectClient,
    startMining,
    stopMining
};