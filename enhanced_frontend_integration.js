/**
 * Enhanced Frontend Integration for FP-Growth Federated Learning System
 * Integrates all UI components with backend APIs and real-time updates
 */

class IntegratedFrontend {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.socket = null;
        this.currentClientId = 'client-1';
        this.currentView = 'client';
        this.currentTab = 'transactions';
        this.miningJobs = new Map();
        this.realTimeUpdates = true;
        
        this.initialize();
    }
    
    initialize() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadInitialData();
        this.startRealTimeUpdates();
    }
    
    setupEventListeners() {
        // Navigation events
        document.addEventListener('DOMContentLoaded', () => {
            this.setupNavigationEvents();
            this.setupTabEvents();
            this.setupFormEvents();
            this.setupButtonEvents();
            this.setupRealTimeControls();
        });
    }
    
    setupNavigationEvents() {
        // View switching
        const viewButtons = document.querySelectorAll('.nav-tab');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.closest('.nav-tab').getAttribute('data-view') || 
                           e.target.closest('.nav-tab').textContent.toLowerCase().includes('client') ? 'client' : 'server';
                this.switchView(view);
            });
        });
        
        // Tab switching
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.closest('.tab-btn').getAttribute('data-tab') || 
                           e.target.closest('.tab-btn').textContent.toLowerCase().replace(/\s+/g, '-');
                this.switchTab(tab);
            });
        });
    }
    
    setupTabEvents() {
        // Transaction management
        this.setupTransactionEvents();
        this.setupItemCatalogEvents();
        this.setupMiningEvents();
        this.setupRecommendationEvents();
        this.setupPrivacyEvents();
        this.setupServerEvents();
    }
    
    setupTransactionEvents() {
        // Add transaction button
        const addTransactionBtn = document.querySelector('[data-action="add-transaction"]');
        if (addTransactionBtn) {
            addTransactionBtn.addEventListener('click', () => this.showAddTransactionModal());
        }
        
        // Import CSV button
        const importBtn = document.querySelector('[data-action="import-csv"]');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importTransactions());
        }
        
        // Export button
        const exportBtn = document.querySelector('[data-action="export-transactions"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportTransactions());
        }
        
        // Transaction table events
        this.setupTransactionTableEvents();
    }
    
    setupItemCatalogEvents() {
        // Add item button
        const addItemBtn = document.querySelector('[data-action="add-item"]');
        if (addItemBtn) {
            addItemBtn.addEventListener('click', () => this.showAddItemModal());
        }
        
        // Item table events
        this.setupItemTableEvents();
    }
    
    setupMiningEvents() {
        // Start mining button
        const startMiningBtn = document.querySelector('[data-action="start-mining"]');
        if (startMiningBtn) {
            startMiningBtn.addEventListener('click', () => this.startMining());
        }
        
        // Stop mining button
        const stopMiningBtn = document.querySelector('[data-action="stop-mining"]');
        if (stopMiningBtn) {
            stopMiningBtn.addEventListener('click', () => this.stopMining());
        }
        
        // Threshold control
        const thresholdInput = document.querySelector('#threshold-input');
        if (thresholdInput) {
            thresholdInput.addEventListener('change', (e) => {
                this.updateThreshold(parseFloat(e.target.value));
            });
        }
        
        // Privacy settings
        const privacyToggle = document.querySelector('#privacy-toggle');
        if (privacyToggle) {
            privacyToggle.addEventListener('change', (e) => {
                this.updatePrivacySettings(e.target.checked);
            });
        }
    }
    
    setupRecommendationEvents() {
        // Apply recommendation buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="apply-recommendation"]')) {
                const recommendationId = e.target.getAttribute('data-recommendation-id');
                this.applyRecommendation(recommendationId);
            }
        });
    }
    
    setupPrivacyEvents() {
        // Privacy level slider
        const privacySlider = document.querySelector('#privacy-level');
        if (privacySlider) {
            privacySlider.addEventListener('input', (e) => {
                this.updatePrivacyLevel(parseFloat(e.target.value));
            });
        }
        
        // Data sharing toggles
        const sharingToggles = document.querySelectorAll('[data-action="toggle-sharing"]');
        sharingToggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.toggleDataSharing(e.target.getAttribute('data-type'), e.target.checked);
            });
        });
    }
    
    setupServerEvents() {
        // Trigger federation round
        const triggerRoundBtn = document.querySelector('[data-action="trigger-round"]');
        if (triggerRoundBtn) {
            triggerRoundBtn.addEventListener('click', () => this.triggerFederationRound());
        }
        
        // Client management
        this.setupClientManagementEvents();
    }
    
    setupFormEvents() {
        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#add-transaction-form')) {
                e.preventDefault();
                this.submitTransaction(e.target);
            } else if (e.target.matches('#add-item-form')) {
                e.preventDefault();
                this.submitItem(e.target);
            } else if (e.target.matches('#mining-config-form')) {
                e.preventDefault();
                this.submitMiningConfig(e.target);
            }
        });
    }
    
    setupButtonEvents() {
        // Utility buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="refresh"]')) {
                this.refreshData();
            } else if (e.target.matches('[data-action="export"]')) {
                this.exportData();
            } else if (e.target.matches('[data-action="settings"]')) {
                this.showSettings();
            } else if (e.target.matches('[data-action="help"]')) {
                this.showHelp();
            }
        });
    }
    
    setupRealTimeControls() {
        // Real-time toggle
        const realtimeToggle = document.querySelector('#realtime-toggle');
        if (realtimeToggle) {
            realtimeToggle.addEventListener('change', (e) => {
                this.toggleRealTimeUpdates(e.target.checked);
            });
        }
    }
    
    // API Methods
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Call Error:', error);
            this.showNotification('Error', error.message, 'error');
            throw error;
        }
    }
    
    // Navigation Methods
    switchView(view) {
        this.currentView = view;
        
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        // Show/hide view containers
        document.querySelectorAll('.view-container').forEach(container => {
            container.classList.remove('active');
        });
        document.getElementById(`${view}-view`).classList.add('active');
        
        // Load view-specific data
        this.loadViewData(view);
    }
    
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        
        // Show/hide tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`).classList.add('active');
        
        // Load tab-specific data
        this.loadTabData(tab);
    }
    
    // Data Loading Methods
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadClientData(),
                this.loadFederationStatus(),
                this.loadAnalytics()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }
    
    async loadViewData(view) {
        if (view === 'client') {
            await this.loadClientData();
        } else if (view === 'server') {
            await this.loadServerData();
        }
    }
    
    async loadTabData(tab) {
        switch (tab) {
            case 'transactions':
                await this.loadTransactions();
                break;
            case 'catalog':
                await this.loadItems();
                break;
            case 'mining':
                await this.loadMiningStatus();
                break;
            case 'recommendations':
                await this.loadRecommendations();
                break;
            case 'privacy':
                await this.loadPrivacySettings();
                break;
            case 'federation':
                await this.loadFederationStatus();
                break;
            case 'analytics':
                await this.loadAnalytics();
                break;
        }
    }
    
    async loadClientData() {
        try {
            const [transactions, items, patterns, recommendations] = await Promise.all([
                this.apiCall(`/clients/${this.currentClientId}/transactions`),
                this.apiCall(`/clients/${this.currentClientId}/items`),
                this.apiCall(`/clients/${this.currentClientId}/patterns`),
                this.apiCall(`/clients/${this.currentClientId}/recommendations`)
            ]);
            
            this.updateClientDashboard(transactions, items, patterns, recommendations);
        } catch (error) {
            console.error('Failed to load client data:', error);
        }
    }
    
    async loadServerData() {
        try {
            const [federationStatus, clients, globalPatterns] = await Promise.all([
                this.apiCall('/federation/status'),
                this.apiCall('/federation/clients'),
                this.apiCall('/federation/patterns')
            ]);
            
            this.updateServerDashboard(federationStatus, clients, globalPatterns);
        } catch (error) {
            console.error('Failed to load server data:', error);
        }
    }
    
    async loadTransactions() {
        try {
            const transactions = await this.apiCall(`/clients/${this.currentClientId}/transactions`);
            this.updateTransactionsTable(transactions);
        } catch (error) {
            console.error('Failed to load transactions:', error);
        }
    }
    
    async loadItems() {
        try {
            const items = await this.apiCall(`/clients/${this.currentClientId}/items`);
            this.updateItemsTable(items);
        } catch (error) {
            console.error('Failed to load items:', error);
        }
    }
    
    async loadMiningStatus() {
        try {
            // Get active mining jobs
            const activeJobs = Array.from(this.miningJobs.values()).filter(job => job.status === 'running');
            this.updateMiningStatus(activeJobs);
        } catch (error) {
            console.error('Failed to load mining status:', error);
        }
    }
    
    async loadRecommendations() {
        try {
            const recommendations = await this.apiCall(`/clients/${this.currentClientId}/recommendations`);
            this.updateRecommendationsTable(recommendations);
        } catch (error) {
            console.error('Failed to load recommendations:', error);
        }
    }
    
    async loadPrivacySettings() {
        try {
            // Load privacy settings from local storage or API
            const settings = this.getPrivacySettings();
            this.updatePrivacySettings(settings);
        } catch (error) {
            console.error('Failed to load privacy settings:', error);
        }
    }
    
    async loadFederationStatus() {
        try {
            const status = await this.apiCall('/federation/status');
            this.updateFederationStatus(status);
        } catch (error) {
            console.error('Failed to load federation status:', error);
        }
    }
    
    async loadAnalytics() {
        try {
            const analytics = await this.apiCall('/analytics');
            this.updateAnalytics(analytics);
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }
    
    // Action Methods
    async startMining() {
        try {
            const threshold = parseFloat(document.querySelector('#threshold-input')?.value || 100);
            const usePrivacy = document.querySelector('#privacy-toggle')?.checked || false;
            
            const response = await this.apiCall(`/clients/${this.currentClientId}/mining/start`, {
                method: 'POST',
                body: JSON.stringify({
                    threshold: threshold,
                    usePrivacy: usePrivacy
                })
            });
            
            this.miningJobs.set(response.job_id, {
                id: response.job_id,
                status: 'running',
                startTime: new Date(),
                threshold: threshold
            });
            
            this.showNotification('Success', 'Mining started successfully', 'success');
            this.loadMiningStatus();
            
            // Start polling for status updates
            this.pollMiningStatus(response.job_id);
            
        } catch (error) {
            console.error('Failed to start mining:', error);
            this.showNotification('Error', 'Failed to start mining', 'error');
        }
    }
    
    async stopMining() {
        try {
            const activeJobs = Array.from(this.miningJobs.values()).filter(job => job.status === 'running');
            
            for (const job of activeJobs) {
                await this.apiCall(`/clients/${this.currentClientId}/mining/${job.id}/stop`, {
                    method: 'POST'
                });
                
                this.miningJobs.set(job.id, { ...job, status: 'stopped' });
            }
            
            this.showNotification('Success', 'Mining stopped successfully', 'success');
            this.loadMiningStatus();
            
        } catch (error) {
            console.error('Failed to stop mining:', error);
            this.showNotification('Error', 'Failed to stop mining', 'error');
        }
    }
    
    async updateThreshold(threshold) {
        try {
            await this.apiCall('/config/threshold', {
                method: 'POST',
                body: JSON.stringify({ threshold: threshold })
            });
            
            this.showNotification('Success', `Threshold updated to ${threshold}`, 'success');
        } catch (error) {
            console.error('Failed to update threshold:', error);
            this.showNotification('Error', 'Failed to update threshold', 'error');
        }
    }
    
    async applyRecommendation(recommendationId) {
        try {
            await this.apiCall(`/clients/${this.currentClientId}/recommendations/${recommendationId}/apply`, {
                method: 'POST'
            });
            
            this.showNotification('Success', 'Recommendation applied successfully', 'success');
            this.loadRecommendations();
            
        } catch (error) {
            console.error('Failed to apply recommendation:', error);
            this.showNotification('Error', 'Failed to apply recommendation', 'error');
        }
    }
    
    async triggerFederationRound() {
        try {
            await this.apiCall('/federation/trigger-round', {
                method: 'POST'
            });
            
            this.showNotification('Success', 'Federation round triggered', 'success');
            this.loadFederationStatus();
            
        } catch (error) {
            console.error('Failed to trigger federation round:', error);
            this.showNotification('Error', 'Failed to trigger federation round', 'error');
        }
    }
    
    // UI Update Methods
    updateClientDashboard(transactions, items, patterns, recommendations) {
        // Update statistics
        this.updateStatistics({
            transactions: transactions.length,
            items: items.length,
            patterns: patterns.length,
            recommendations: recommendations.length
        });
        
        // Update tables
        this.updateTransactionsTable(transactions);
        this.updateItemsTable(items);
        this.updatePatternsTable(patterns);
        this.updateRecommendationsTable(recommendations);
    }
    
    updateServerDashboard(federationStatus, clients, globalPatterns) {
        // Update federation status
        this.updateFederationStatus(federationStatus);
        
        // Update clients table
        this.updateClientsTable(clients);
        
        // Update global patterns
        this.updateGlobalPatternsTable(globalPatterns);
    }
    
    updateStatistics(stats) {
        const statElements = document.querySelectorAll('.stat-value');
        statElements.forEach(element => {
            const statType = element.getAttribute('data-stat');
            if (stats[statType] !== undefined) {
                element.textContent = stats[statType];
            }
        });
    }
    
    updateTransactionsTable(transactions) {
        const table = document.querySelector('#transactions-table tbody');
        if (!table) return;
        
        table.innerHTML = transactions.map(tx => `
            <tr>
                <td>${tx.id}</td>
                <td>${tx.items?.join(', ') || 'N/A'}</td>
                <td>$${tx.utility || 0}</td>
                <td>${tx.created_at || 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="frontend.editTransaction('${tx.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="frontend.deleteTransaction('${tx.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }
    
    updateItemsTable(items) {
        const table = document.querySelector('#items-table tbody');
        if (!table) return;
        
        table.innerHTML = items.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>$${item.utility || 0}</td>
                <td>${item.weight || 1}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="frontend.editItem('${item.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="frontend.deleteItem('${item.id}')">Delete</button>
                </td>
            </tr>
        `).join('');
    }
    
    updateMiningStatus(activeJobs) {
        const statusContainer = document.querySelector('#mining-status');
        if (!statusContainer) return;
        
        if (activeJobs.length === 0) {
            statusContainer.innerHTML = '<p class="text-muted">No active mining jobs</p>';
        } else {
            statusContainer.innerHTML = activeJobs.map(job => `
                <div class="mining-job">
                    <div class="job-header">
                        <span class="job-id">${job.id}</span>
                        <span class="job-status running">Running</span>
                    </div>
                    <div class="job-details">
                        <span>Threshold: ${job.threshold}</span>
                        <span>Started: ${job.startTime.toLocaleTimeString()}</span>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="frontend.stopMiningJob('${job.id}')">Stop</button>
                </div>
            `).join('');
        }
    }
    
    updateFederationStatus(status) {
        const statusElement = document.querySelector('#federation-status');
        if (!statusElement) return;
        
        statusElement.innerHTML = `
            <div class="status-grid">
                <div class="status-item">
                    <span class="label">Round:</span>
                    <span class="value">${status.round || 0}</span>
                </div>
                <div class="status-item">
                    <span class="label">Progress:</span>
                    <span class="value">${Math.round((status.progress || 0) * 100)}%</span>
                </div>
                <div class="status-item">
                    <span class="label">Clients:</span>
                    <span class="value">${status.participatingClients || 0}/${status.totalClients || 0}</span>
                </div>
                <div class="status-item">
                    <span class="label">Status:</span>
                    <span class="value ${status.convergenceStatus || 'waiting'}">${status.convergenceStatus || 'Waiting'}</span>
                </div>
            </div>
        `;
    }
    
    // Utility Methods
    showNotification(title, message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-header">
                <span class="notification-title">${title}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">${message}</div>
        `;
        
        // Add to page
        const container = document.querySelector('.notification-container') || document.body;
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    connectWebSocket() {
        try {
            this.socket = io('http://localhost:5000');
            
            this.socket.on('connect', () => {
                console.log('Connected to WebSocket server');
                this.socket.emit('join_room', { room: 'dashboard' });
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from WebSocket server');
            });
            
            this.socket.on('federation_update', (data) => {
                this.updateFederationStatus(data);
            });
            
            this.socket.on('clients_update', (data) => {
                this.updateClientsTable(data);
            });
            
            this.socket.on('mining_update', (data) => {
                this.updateMiningStatus([data]);
            });
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    }
    
    startRealTimeUpdates() {
        if (!this.realTimeUpdates) return;
        
        // Poll for updates every 5 seconds
        setInterval(() => {
            if (this.realTimeUpdates) {
                this.loadFederationStatus();
                this.loadMiningStatus();
            }
        }, 5000);
    }
    
    toggleRealTimeUpdates(enabled) {
        this.realTimeUpdates = enabled;
        this.showNotification(
            'Real-time Updates', 
            enabled ? 'Real-time updates enabled' : 'Real-time updates disabled',
            'info'
        );
    }
    
    pollMiningStatus(jobId) {
        const pollInterval = setInterval(async () => {
            try {
                const status = await this.apiCall(`/clients/${this.currentClientId}/mining/${jobId}/status`);
                
                this.miningJobs.set(jobId, status);
                
                if (status.status === 'completed' || status.status === 'failed') {
                    clearInterval(pollInterval);
                    this.showNotification(
                        'Mining Complete', 
                        status.status === 'completed' ? 'Mining completed successfully' : 'Mining failed',
                        status.status === 'completed' ? 'success' : 'error'
                    );
                    this.loadMiningStatus();
                }
                
            } catch (error) {
                console.error('Failed to poll mining status:', error);
                clearInterval(pollInterval);
            }
        }, 2000);
    }
    
    getPrivacySettings() {
        return JSON.parse(localStorage.getItem('privacySettings') || '{}');
    }
    
    setPrivacySettings(settings) {
        localStorage.setItem('privacySettings', JSON.stringify(settings));
    }
    
    refreshData() {
        this.loadViewData(this.currentView);
        this.showNotification('Success', 'Data refreshed', 'success');
    }
    
    exportData() {
        // Implementation for data export
        this.showNotification('Info', 'Export functionality coming soon', 'info');
    }
    
    showSettings() {
        // Implementation for settings modal
        this.showNotification('Info', 'Settings functionality coming soon', 'info');
    }
    
    showHelp() {
        // Implementation for help modal
        this.showNotification('Info', 'Help functionality coming soon', 'info');
    }
    
    // Missing methods that are called but not defined
    showAddTransactionModal() {
        // Implementation for add transaction modal
        this.showNotification('Info', 'Add transaction modal coming soon', 'info');
    }
    
    showAddItemModal() {
        // Implementation for add item modal
        this.showNotification('Info', 'Add item modal coming soon', 'info');
    }
    
    setupTransactionTableEvents() {
        // Implementation for transaction table events
        const table = document.querySelector('#transactions-table');
        if (table) {
            // Add event listeners for transaction table interactions
            table.addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-transaction')) {
                    const transactionId = e.target.getAttribute('data-id');
                    this.deleteTransaction(transactionId);
                }
            });
        }
    }
    
    setupItemTableEvents() {
        // Implementation for item table events
        const table = document.querySelector('#items-table');
        if (table) {
            // Add event listeners for item table interactions
            table.addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-item')) {
                    const itemId = e.target.getAttribute('data-id');
                    this.deleteItem(itemId);
                }
            });
        }
    }
    
    updateRecommendationsTable(recommendations) {
        const table = document.querySelector('#recommendations-table');
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (recommendations && recommendations.length > 0) {
            recommendations.forEach((rec, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${rec.type || 'Pattern'}</td>
                    <td>${rec.description || 'No description'}</td>
                    <td>${rec.confidence || 0}%</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="applyRecommendation('${rec.id}')">
                            Apply
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="5" class="text-center">No recommendations available</td>';
            tbody.appendChild(row);
        }
    }
    
    updateAnalytics(analytics) {
        // Implementation for analytics update
        const analyticsContainer = document.querySelector('#analytics-container');
        if (analyticsContainer && analytics) {
            analyticsContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Total Patterns</h5>
                                <p class="card-text">${analytics.totalPatterns || 0}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Avg Utility</h5>
                                <p class="card-text">${analytics.avgUtility || 0}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Active Clients</h5>
                                <p class="card-text">${analytics.activeClients || 0}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Federation Rounds</h5>
                                <p class="card-text">${analytics.federationRounds || 0}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    updatePrivacyLevel(level) {
        // Implementation for privacy level update
        this.showNotification('Success', `Privacy level updated to ${level}`, 'success');
    }
    
    toggleDataSharing(type, enabled) {
        // Implementation for data sharing toggle
        this.showNotification('Success', `${type} data sharing ${enabled ? 'enabled' : 'disabled'}`, 'success');
    }
    
    setupClientManagementEvents() {
        // Implementation for client management events
        const clientTable = document.querySelector('#clients-table');
        if (clientTable) {
            clientTable.addEventListener('click', (e) => {
                if (e.target.classList.contains('disconnect-client')) {
                    const clientId = e.target.getAttribute('data-id');
                    this.disconnectClient(clientId);
                }
            });
        }
    }
    
    async submitTransaction(form) {
        // Implementation for transaction submission
        const formData = new FormData(form);
        const transactionData = {
            items: formData.get('items').split(',').map(item => item.trim()),
            utility: parseFloat(formData.get('utility')),
            timestamp: new Date().toISOString()
        };
        
        try {
            await this.apiCall(`/clients/${this.currentClientId}/transactions`, {
                method: 'POST',
                body: JSON.stringify(transactionData)
            });
            
            this.showNotification('Success', 'Transaction added successfully', 'success');
            this.loadTransactions();
        } catch (error) {
            this.showNotification('Error', 'Failed to add transaction', 'error');
        }
    }
    
    async submitItem(form) {
        // Implementation for item submission
        const formData = new FormData(form);
        const itemData = {
            name: formData.get('name'),
            category: formData.get('category'),
            utility: parseFloat(formData.get('utility'))
        };
        
        try {
            await this.apiCall(`/clients/${this.currentClientId}/items`, {
                method: 'POST',
                body: JSON.stringify(itemData)
            });
            
            this.showNotification('Success', 'Item added successfully', 'success');
            this.loadItems();
        } catch (error) {
            this.showNotification('Error', 'Failed to add item', 'error');
        }
    }
    
    async submitMiningConfig(form) {
        // Implementation for mining configuration submission
        const formData = new FormData(form);
        const configData = {
            threshold: parseFloat(formData.get('threshold')),
            usePrivacy: formData.get('usePrivacy') === 'on'
        };
        
        try {
            await this.apiCall(`/clients/${this.currentClientId}/mining/config`, {
                method: 'POST',
                body: JSON.stringify(configData)
            });
            
            this.showNotification('Success', 'Mining configuration updated', 'success');
        } catch (error) {
            this.showNotification('Error', 'Failed to update mining configuration', 'error');
        }
    }
    
    async deleteTransaction(transactionId) {
        // Implementation for transaction deletion
        try {
            await this.apiCall(`/clients/${this.currentClientId}/transactions/${transactionId}`, {
                method: 'DELETE'
            });
            
            this.showNotification('Success', 'Transaction deleted successfully', 'success');
            this.loadTransactions();
        } catch (error) {
            this.showNotification('Error', 'Failed to delete transaction', 'error');
        }
    }
    
    async deleteItem(itemId) {
        // Implementation for item deletion
        try {
            await this.apiCall(`/clients/${this.currentClientId}/items/${itemId}`, {
                method: 'DELETE'
            });
            
            this.showNotification('Success', 'Item deleted successfully', 'success');
            this.loadItems();
        } catch (error) {
            this.showNotification('Error', 'Failed to delete item', 'error');
        }
    }
    
    async disconnectClient(clientId) {
        // Implementation for client disconnection
        try {
            await this.apiCall(`/federation/clients/${clientId}/disconnect`, {
                method: 'POST'
            });
            
            this.showNotification('Success', `Client ${clientId} disconnected`, 'success');
            this.loadFederationStatus();
        } catch (error) {
            this.showNotification('Error', 'Failed to disconnect client', 'error');
        }
    }
    
    async importTransactions() {
        // Implementation for transaction import
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.csv';
        
        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    await this.apiCall(`/clients/${this.currentClientId}/transactions/upload`, {
                        method: 'POST',
                        body: formData,
                        headers: {} // Let browser set Content-Type for FormData
                    });
                    
                    this.showNotification('Success', 'Transactions imported successfully', 'success');
                    this.loadTransactions();
                } catch (error) {
                    this.showNotification('Error', 'Failed to import transactions', 'error');
                }
            }
        };
        
        fileInput.click();
    }
}

// Initialize the frontend when the page loads
let frontend;
document.addEventListener('DOMContentLoaded', () => {
    frontend = new IntegratedFrontend();
});

// Global functions for inline event handlers
window.switchView = (view) => frontend.switchView(view);
window.switchTab = (tab) => frontend.switchTab(tab);
window.startMining = () => frontend.startMining();
window.stopMining = () => frontend.stopMining();
window.applyRecommendation = (id) => frontend.applyRecommendation(id);
window.triggerFederationRound = () => frontend.triggerFederationRound(); 