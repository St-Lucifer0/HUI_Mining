# Federated High Utility Itemset Mining System - HTML Frontend

A simple HTML/CSS/JavaScript frontend for a federated learning system that discovers High Utility Itemsets across 3 retail stores.

## Files Structure

```
├── index.html          # Main application with both client and server views
├── client.html         # Standalone client interface
├── server.html         # Standalone server interface
├── styles.css          # All styling for the application
├── script.js           # JavaScript functionality and API integration
└── README.md           # This file
```

## Features

### Client Interface
- **Transaction Management**: Upload, view, and manage transaction data
- **Item Catalog**: Configure item utilities and weights for HUIM analysis
- **Mining Controls**: Set utility thresholds, support levels, and privacy settings
- **Recommendations**: View AI-powered recommendations based on patterns
- **Privacy Settings**: Control data sharing with the federation

### Server Interface
- **Federation Dashboard**: Monitor client status and training progress
- **Global Patterns**: View high-utility itemsets discovered across all clients
- **Client Monitoring**: Track client health, performance, and data quality
- **Analytics**: Comprehensive performance metrics and insights

## Usage

### Option 1: Single Application
Open `index.html` in your browser for the complete application with both client and server views.

### Option 2: Separate Interfaces
- Open `client.html` for the client-only interface
- Open `server.html` for the server-only interface

## Backend Integration

The JavaScript includes an API service ready for backend integration:

```javascript
const API = {
    baseUrl: 'http://localhost:8000/api', // Change to your backend URL
    
    // Transaction endpoints
    async getTransactions(clientId) { ... },
    async createTransaction(clientId, transaction) { ... },
    
    // Mining endpoints
    async startMining(clientId, config) { ... },
    async getMiningStatus(clientId, jobId) { ... },
    
    // Federation endpoints
    async getFederationStatus() { ... },
    async getGlobalPatterns() { ... },
    async getClients() { ... }
};
```

### Expected API Endpoints

#### Client APIs
```
GET    /api/clients/{clientId}/transactions
POST   /api/clients/{clientId}/transactions
PUT    /api/clients/{clientId}/transactions/{transactionId}
DELETE /api/clients/{clientId}/transactions/{transactionId}
POST   /api/clients/{clientId}/transactions/upload

GET    /api/clients/{clientId}/items
POST   /api/clients/{clientId}/items
PUT    /api/clients/{clientId}/items/{itemId}
DELETE /api/clients/{clientId}/items/{itemId}

POST   /api/clients/{clientId}/mining/start
POST   /api/clients/{clientId}/mining/{jobId}/stop
GET    /api/clients/{clientId}/mining/{jobId}/status
GET    /api/clients/{clientId}/patterns

GET    /api/clients/{clientId}/recommendations
POST   /api/clients/{clientId}/recommendations/{recommendationId}/apply
```

#### Federation APIs
```
GET    /api/federation/status
GET    /api/federation/clients
GET    /api/federation/patterns
GET    /api/federation/clients/{clientId}/metrics
POST   /api/federation/trigger-round

GET    /api/analytics?timeRange={timeRange}
POST   /api/analytics/export?timeRange={timeRange}&format={format}
```

## Data Models

### Transaction
```json
{
  "id": "T1",
  "timestamp": "2024-01-15 10:30:00",
  "items": [
    {
      "name": "Smartphone",
      "quantity": 1,
      "utility": 650
    }
  ],
  "totalUtility": 650,
  "clientId": "client-1"
}
```

### Item
```json
{
  "id": "1",
  "name": "Smartphone",
  "category": "Electronics",
  "baseUtility": 650,
  "weight": 1.0,
  "frequency": 24
}
```

### High Utility Pattern
```json
{
  "id": "pattern-1",
  "itemset": ["Smartphone", "Phone Case", "Screen Protector"],
  "utility": 690,
  "support": 0.67,
  "confidence": 0.89,
  "isLocal": false,
  "clientCount": 3,
  "trend": "rising"
}
```

### Client Status
```json
{
  "id": "client-1",
  "name": "Electronics Retail Store",
  "status": "healthy",
  "lastUpdate": "2 min ago",
  "dataQuality": 94,
  "contributionScore": 85,
  "networkLatency": 45,
  "localAccuracy": 89.2,
  "transactionCount": 2847,
  "patterns": 156
}
```

## Customization

### Changing Client Information
Edit the client data in `script.js`:

```javascript
const clientData = {
    'client-1': {
        name: 'Your Store Name',
        // ... other properties
    }
};
```

### Adding New Features
1. Add HTML structure to the appropriate tab
2. Add CSS styling in `styles.css`
3. Add JavaScript functionality in `script.js`
4. Update API endpoints as needed

### Styling
The application uses a dark theme with these main colors:
- Primary: #6366f1 (Indigo)
- Success: #10b981 (Emerald)
- Warning: #f59e0b (Amber)
- Error: #ef4444 (Red)
- Background: #111827 (Dark Gray)
- Cards: #374151 (Medium Gray)

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Development

To modify the application:

1. Edit HTML structure in the respective files
2. Update styles in `styles.css`
3. Add functionality in `script.js`
4. Test in multiple browsers
5. Update API endpoints to match your backend

## Integration with Backend

1. Update the `API.baseUrl` in `script.js` to point to your backend
2. Implement the expected endpoints in your backend
3. Use the provided data models for consistency
4. Test API calls using the browser's developer tools
5. Handle errors appropriately in the UI

The frontend is designed to work with any backend technology (Python Flask/FastAPI, Node.js, Java Spring, etc.) as long as it implements the expected REST API endpoints.