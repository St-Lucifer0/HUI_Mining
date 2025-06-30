# 📊 Federated Learning Output Examples

This document shows you exactly how the high-utility itemset results will be displayed and saved.

## 🖥️ **Console Output (Terminal)**

When you run the federated learning system, you'll see output like this in the terminal:

```
================================================================================
FEDERATED LEARNING HIGH-UTILITY ITEMSET MINING RESULTS
================================================================================
Generated: 2024-01-15 14:30:25

SERVER STATISTICS:
----------------------------------------
Total Transactions: 4141
Participating Clients: 3
Global Utility Sum: 334.00
Privacy Budget Used: 1.00

GLOBAL HIGH-UTILITY ITEMSETS:
----------------------------------------
Total Itemsets Found: 5

Rank | Itemset                    | Utility | Support | Items
--------------------------------------------------------------------------------
   1 | rice, egg                   |   85.50 |    0.15 | 2
   2 | milk, bread, butter         |   72.30 |    0.08 | 3
   3 | sugar                       |   65.10 |    0.25 | 1
   4 | rice, sugar                 |   58.70 |    0.12 | 2
   5 | egg, milk                   |   52.40 |    0.10 | 2

CLIENT RESULTS SUMMARY:
----------------------------------------
Client client-1: 3 itemsets, Utility: 221.90
Client client-2: 2 itemsets, Utility: 176.20
================================================================================
```

## 📄 **Text File Output (`federated_results_20240115_143025.txt`)**

The same formatted output is saved to a text file:

```
================================================================================
FEDERATED LEARNING HIGH-UTILITY ITEMSET MINING RESULTS
================================================================================
Generated: 2024-01-15 14:30:25

SERVER STATISTICS:
----------------------------------------
Total Transactions: 4141
Participating Clients: 3
Global Utility Sum: 334.00
Privacy Budget Used: 1.00

GLOBAL HIGH-UTILITY ITEMSETS:
----------------------------------------
Total Itemsets Found: 5

Rank | Itemset                    | Utility | Support | Items
--------------------------------------------------------------------------------
   1 | rice, egg                   |   85.50 |    0.15 | 2
   2 | milk, bread, butter         |   72.30 |    0.08 | 3
   3 | sugar                       |   65.10 |    0.25 | 1
   4 | rice, sugar                 |   58.70 |    0.12 | 2
   5 | egg, milk                   |   52.40 |    0.10 | 2

CLIENT RESULTS SUMMARY:
----------------------------------------
Client client-1: 3 itemsets, Utility: 221.90
Client client-2: 2 itemsets, Utility: 176.20
================================================================================
```

## 📊 **CSV File Output (`federated_results_20240115_143025.csv`)**

For data analysis and Excel import:

```csv
Rank,Itemset,Items,Utility,Support,Item_Count
1,"rice, egg","['rice', 'egg']",85.5,0.15,2
2,"milk, bread, butter","['milk', 'bread', 'butter']",72.3,0.08,3
3,"sugar","['sugar']",65.1,0.25,1
4,"rice, sugar","['rice', 'sugar']",58.7,0.12,2
5,"egg, milk","['egg', 'milk']",52.4,0.10,2
```

## 🔧 **JSON File Output (`federated_results_20240115_143025.json`)**

For programmatic access and APIs:

```json
{
  "metadata": {
    "timestamp": "2024-01-15T14:30:25.123456",
    "total_itemsets": 5,
    "server_stats": {
      "total_transactions": 4141,
      "participating_clients": 3,
      "global_utility_sum": 334.0,
      "privacy_budget_used": 1.0
    }
  },
  "global_results": [
    {
      "items": ["rice", "egg"],
      "utility": 85.5,
      "support": 0.15,
      "item_count": 2
    },
    {
      "items": ["milk", "bread", "butter"],
      "utility": 72.3,
      "support": 0.08,
      "item_count": 3
    },
    {
      "items": ["sugar"],
      "utility": 65.1,
      "support": 0.25,
      "item_count": 1
    },
    {
      "items": ["rice", "sugar"],
      "utility": 58.7,
      "support": 0.12,
      "item_count": 2
    },
    {
      "items": ["egg", "milk"],
      "utility": 52.4,
      "support": 0.10,
      "item_count": 2
    }
  ],
  "client_results": {
    "client-1": {
      "itemsets": [
        {
          "items": ["rice", "egg"],
          "utility": 85.5,
          "support": 0.15
        },
        {
          "items": ["milk", "bread", "butter"],
          "utility": 72.3,
          "support": 0.08
        },
        {
          "items": ["sugar"],
          "utility": 65.1,
          "support": 0.25
        }
      ],
      "stats": {
        "local_utility_sum": 221.9,
        "transaction_count": 1500
      }
    },
    "client-2": {
      "itemsets": [
        {
          "items": ["sugar"],
          "utility": 65.1,
          "support": 0.25
        },
        {
          "items": ["rice", "sugar"],
          "utility": 58.7,
          "support": 0.12
        },
        {
          "items": ["egg", "milk"],
          "utility": 52.4,
          "support": 0.10
        }
      ],
      "stats": {
        "local_utility_sum": 176.2,
        "transaction_count": 1200
      }
    }
  }
}
```

## 🌐 **HTML File Output (`federated_results_20240115_143025.html`)**

A beautiful, formatted web page that you can open in any browser:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federated Learning Results - 2024-01-15 14:30:25</title>
    <style>
        /* Beautiful CSS styling */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        /* ... more styling ... */
    </style>
</head>
<body>
    <div class="container">
        <h1>Federated Learning High-Utility Itemset Mining Results</h1>
        
        <div class="timestamp">
            Generated on 2024-01-15 at 14:30:25
        </div>
        
        <div class="stats">
            <h3>Server Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Transactions</div>
                    <div class="stat-value">4,141</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Participating Clients</div>
                    <div class="stat-value">3</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Global Utility Sum</div>
                    <div class="stat-value">334.00</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Privacy Budget Used</div>
                    <div class="stat-value">1.00</div>
                </div>
            </div>
        </div>
        
        <h3>Global High-Utility Itemsets (5 found)</h3>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Itemset</th>
                    <th>Utility</th>
                    <th>Support</th>
                    <th>Items</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td><span class="itemset">rice, egg</span></td>
                    <td class="utility">85.50</td>
                    <td class="support">0.15</td>
                    <td>2</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td><span class="itemset">milk, bread, butter</span></td>
                    <td class="utility">72.30</td>
                    <td class="support">0.08</td>
                    <td>3</td>
                </tr>
                <!-- ... more rows ... -->
            </tbody>
        </table>
        
        <h3>Client Results Summary</h3>
        <table>
            <thead>
                <tr>
                    <th>Client ID</th>
                    <th>Itemsets Found</th>
                    <th>Local Utility Sum</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>client-1</td>
                    <td>3</td>
                    <td class="utility">221.90</td>
                </tr>
                <tr>
                    <td>client-2</td>
                    <td>2</td>
                    <td class="utility">176.20</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
```

## 📁 **File Locations**

All output files are saved in the `results/` directory:

```
results/
├── federated_results_20240115_143025.txt    # Text format
├── federated_results_20240115_143025.csv    # CSV format
├── federated_results_20240115_143025.json   # JSON format
└── federated_results_20240115_143025.html   # HTML format
```

## 🎯 **What Each Output Contains**

### **Server Statistics**
- **Total Transactions**: Number of transactions processed across all clients
- **Participating Clients**: Number of clients that contributed data
- **Global Utility Sum**: Total utility value across all itemsets
- **Privacy Budget Used**: Amount of differential privacy budget consumed

### **High-Utility Itemsets**
- **Rank**: Position based on utility value (highest first)
- **Itemset**: The actual items found together
- **Utility**: The utility value of this itemset
- **Support**: How frequently this itemset appears
- **Item Count**: Number of items in the set

### **Client Results**
- **Client ID**: Identifier for each participating laptop
- **Itemsets Found**: Number of high-utility itemsets from this client
- **Local Utility Sum**: Total utility from this client's data

## 🔍 **Understanding the Results**

### **Example Interpretation**
```
Rank 1: rice, egg (Utility: 85.50, Support: 0.15)
```
This means:
- **rice** and **egg** are frequently bought together
- They have a high utility value of 85.50
- They appear in 15% of all transactions
- This is the most valuable itemset found

### **Business Insights**
- **High Utility + High Support**: Popular and valuable items (good for promotions)
- **High Utility + Low Support**: Niche but valuable items (good for targeted marketing)
- **Low Utility + High Support**: Common but low-value items (good for bundling)

## 📊 **Using the Results**

### **Text/Console Output**
- Quick overview and monitoring
- Real-time results during mining
- Easy to read and understand

### **CSV Output**
- Import into Excel for analysis
- Create charts and graphs
- Further data processing

### **JSON Output**
- Programmatic access
- API integration
- Custom analysis scripts

### **HTML Output**
- Professional reports
- Web-based dashboards
- Sharing with stakeholders

## 🚀 **Accessing Your Results**

After running the federated learning system:

1. **Check the console** for immediate results
2. **Open the HTML file** in your browser for a beautiful report
3. **Import the CSV** into Excel for analysis
4. **Use the JSON** for custom processing

The system automatically saves all formats, so you'll have multiple ways to view and use your high-utility itemset results! 