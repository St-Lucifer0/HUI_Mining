#!/usr/bin/env python3
"""
Demonstration script showing the output formats for federated learning results
"""

import os
import sys
from datetime import datetime

def demo_console_output():
    """Demonstrate console output format"""
    print("=" * 80)
    print("FEDERATED LEARNING HIGH-UTILITY ITEMSET MINING RESULTS")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    print("SERVER STATISTICS:")
    print("-" * 40)
    print("Total Transactions: 4141")
    print("Participating Clients: 3")
    print("Global Utility Sum: 334.00")
    print("Privacy Budget Used: 1.00")
    print("")
    
    print("GLOBAL HIGH-UTILITY ITEMSETS:")
    print("-" * 40)
    print("Total Itemsets Found: 5")
    print("")
    print("Rank | Itemset                    | Utility | Support | Items")
    print("-" * 80)
    print("   1 | rice, egg                   |   85.50 |    0.15 | 2")
    print("   2 | milk, bread, butter         |   72.30 |    0.08 | 3")
    print("   3 | sugar                       |   65.10 |    0.25 | 1")
    print("   4 | rice, sugar                 |   58.70 |    0.12 | 2")
    print("   5 | egg, milk                   |   52.40 |    0.10 | 2")
    print("")
    
    print("CLIENT RESULTS SUMMARY:")
    print("-" * 40)
    print("Client client-1: 3 itemsets, Utility: 221.90")
    print("Client client-2: 2 itemsets, Utility: 176.20")
    print("=" * 80)

def demo_csv_output():
    """Demonstrate CSV output format"""
    print("\n📊 CSV OUTPUT FORMAT:")
    print("-" * 50)
    print("Rank,Itemset,Items,Utility,Support,Item_Count")
    print("1,\"rice, egg\",\"['rice', 'egg']\",85.5,0.15,2")
    print("2,\"milk, bread, butter\",\"['milk', 'bread', 'butter']\",72.3,0.08,3")
    print("3,\"sugar\",\"['sugar']\",65.1,0.25,1")
    print("4,\"rice, sugar\",\"['rice', 'sugar']\",58.7,0.12,2")
    print("5,\"egg, milk\",\"['egg', 'milk']\",52.4,0.10,2")

def demo_json_output():
    """Demonstrate JSON output format"""
    print("\n🔧 JSON OUTPUT FORMAT:")
    print("-" * 50)
    print("""{
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
    }
  ]
}""")

def demo_html_output():
    """Demonstrate HTML output format"""
    print("\n🌐 HTML OUTPUT FORMAT:")
    print("-" * 50)
    print("""<!DOCTYPE html>
<html>
<head>
    <title>Federated Learning Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Federated Learning High-Utility Itemset Mining Results</h1>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Itemset</th>
                    <th>Utility</th>
                    <th>Support</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>rice, egg</td>
                    <td>85.50</td>
                    <td>0.15</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>""")

def demo_file_structure():
    """Show the file structure of output files"""
    print("\n📁 OUTPUT FILE STRUCTURE:")
    print("-" * 50)
    print("results/")
    print("├── federated_results_20240115_143025.txt    # Text format")
    print("├── federated_results_20240115_143025.csv    # CSV format")
    print("├── federated_results_20240115_143025.json   # JSON format")
    print("└── federated_results_20240115_143025.html   # HTML format")

def demo_interpretation():
    """Show how to interpret the results"""
    print("\n🎯 RESULT INTERPRETATION:")
    print("-" * 50)
    print("Example: rice, egg (Utility: 85.50, Support: 0.15)")
    print("")
    print("This means:")
    print("• rice and egg are frequently bought together")
    print("• They have a high utility value of 85.50")
    print("• They appear in 15% of all transactions")
    print("• This is the most valuable itemset found")
    print("")
    print("Business Insights:")
    print("• High Utility + High Support: Popular and valuable items")
    print("• High Utility + Low Support: Niche but valuable items")
    print("• Low Utility + High Support: Common but low-value items")

def main():
    """Main demonstration function"""
    print("🎉 FEDERATED LEARNING OUTPUT DEMONSTRATION")
    print("=" * 60)
    print("This shows you exactly how your results will look!")
    print("")
    
    # Show all output formats
    demo_console_output()
    demo_csv_output()
    demo_json_output()
    demo_html_output()
    demo_file_structure()
    demo_interpretation()
    
    print("\n" + "=" * 60)
    print("✅ All output formats will be automatically generated!")
    print("📁 Files will be saved in the 'results/' directory")
    print("🌐 Open the HTML file in your browser for a beautiful report")
    print("📊 Import the CSV into Excel for analysis")
    print("🔧 Use the JSON for custom processing")

if __name__ == '__main__':
    main() 