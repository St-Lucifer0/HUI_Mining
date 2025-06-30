#!/usr/bin/env python3
"""
Output formatter for federated learning high-utility itemset results
Provides multiple output formats: console, text file, JSON, CSV, and HTML
"""

import json
import csv
import os
import time
from datetime import datetime
from typing import List, Dict, Set, Any
import logging

logger = logging.getLogger(__name__)

class FederatedLearningOutputFormatter:
    """Formats and saves federated learning results in multiple formats"""
    
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Results storage
        self.global_results = []
        self.client_results = {}
        self.server_stats = {}
        
    def add_global_results(self, itemsets: List[Dict], stats: Dict):
        """Add global aggregated results"""
        self.global_results = itemsets
        self.server_stats = stats
        
    def add_client_results(self, client_id: str, itemsets: List[Dict], stats: Dict):
        """Add individual client results"""
        self.client_results[client_id] = {
            'itemsets': itemsets,
            'stats': stats
        }
    
    def format_console_output(self) -> str:
        """Format results for console display"""
        output = []
        output.append("=" * 80)
        output.append("FEDERATED LEARNING HIGH-UTILITY ITEMSET MINING RESULTS")
        output.append("=" * 80)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # Server statistics
        output.append("SERVER STATISTICS:")
        output.append("-" * 40)
        output.append(f"Total Transactions: {self.server_stats.get('total_transactions', 0)}")
        output.append(f"Participating Clients: {self.server_stats.get('participating_clients', 0)}")
        output.append(f"Global Utility Sum: {self.server_stats.get('global_utility_sum', 0):.2f}")
        output.append(f"Privacy Budget Used: {self.server_stats.get('privacy_budget_used', 0):.2f}")
        output.append("")
        
        # Global results
        output.append("GLOBAL HIGH-UTILITY ITEMSETS:")
        output.append("-" * 40)
        if self.global_results:
            output.append(f"Total Itemsets Found: {len(self.global_results)}")
            output.append("")
            output.append("Rank | Itemset | Utility | Support | Items")
            output.append("-" * 80)
            
            for i, itemset_data in enumerate(self.global_results, 1):
                items = list(itemset_data['itemset'])
                utility = itemset_data['utility']
                support = itemset_data['support']
                items_str = ", ".join(items)
                
                output.append(f"{i:4d} | {items_str:30s} | {utility:7.2f} | {support:6.2f} | {len(items)}")
        else:
            output.append("No high-utility itemsets found.")
        
        output.append("")
        
        # Client results summary
        if self.client_results:
            output.append("CLIENT RESULTS SUMMARY:")
            output.append("-" * 40)
            for client_id, client_data in self.client_results.items():
                itemsets = client_data['itemsets']
                stats = client_data['stats']
                output.append(f"Client {client_id}: {len(itemsets)} itemsets, "
                            f"Utility: {stats.get('local_utility_sum', 0):.2f}")
        
        output.append("=" * 80)
        return "\n".join(output)
    
    def save_text_file(self, filename: str = None) -> str:
        """Save results to a text file"""
        if filename is None:
            filename = f"federated_results_{self.timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.format_console_output())
        
        logger.info(f"Results saved to text file: {filepath}")
        return filepath
    
    def save_json_file(self, filename: str = None) -> str:
        """Save results to a JSON file"""
        if filename is None:
            filename = f"federated_results_{self.timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare JSON data
        json_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_itemsets': len(self.global_results),
                'server_stats': self.server_stats
            },
            'global_results': [
                {
                    'items': list(itemset_data['itemset']),
                    'utility': itemset_data['utility'],
                    'support': itemset_data['support'],
                    'item_count': len(itemset_data['itemset'])
                }
                for itemset_data in self.global_results
            ],
            'client_results': {
                client_id: {
                    'itemsets': [
                        {
                            'items': list(itemset_data['itemset']),
                            'utility': itemset_data['utility'],
                            'support': itemset_data['support']
                        }
                        for itemset_data in client_data['itemsets']
                    ],
                    'stats': client_data['stats']
                }
                for client_id, client_data in self.client_results.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to JSON file: {filepath}")
        return filepath
    
    def save_csv_file(self, filename: str = None) -> str:
        """Save results to a CSV file"""
        if filename is None:
            filename = f"federated_results_{self.timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Rank', 'Itemset', 'Items', 'Utility', 'Support', 'Item_Count'])
            
            # Write data
            for i, itemset_data in enumerate(self.global_results, 1):
                items = list(itemset_data['itemset'])
                items_str = ", ".join(items)
                utility = itemset_data['utility']
                support = itemset_data['support']
                item_count = len(items)
                
                writer.writerow([i, items_str, items, utility, support, item_count])
        
        logger.info(f"Results saved to CSV file: {filepath}")
        return filepath
    
    def save_html_file(self, filename: str = None) -> str:
        """Save results to an HTML file with nice formatting"""
        if filename is None:
            filename = f"federated_results_{self.timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate HTML content
        html_content = self._generate_html_content()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Results saved to HTML file: {filepath}")
        return filepath
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for results"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federated Learning Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .stats h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .stat-label {{
            font-weight: bold;
            color: #7f8c8d;
        }}
        .stat-value {{
            font-size: 1.2em;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .itemset {{
            font-family: monospace;
            background-color: #f1f2f6;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .utility {{
            font-weight: bold;
            color: #27ae60;
        }}
        .support {{
            color: #e74c3c;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Federated Learning High-Utility Itemset Mining Results</h1>
        
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
        </div>
        
        <div class="stats">
            <h3>Server Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Transactions</div>
                    <div class="stat-value">{self.server_stats.get('total_transactions', 0):,}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Participating Clients</div>
                    <div class="stat-value">{self.server_stats.get('participating_clients', 0)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Global Utility Sum</div>
                    <div class="stat-value">{self.server_stats.get('global_utility_sum', 0):.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Privacy Budget Used</div>
                    <div class="stat-value">{self.server_stats.get('privacy_budget_used', 0):.2f}</div>
                </div>
            </div>
        </div>
        
        <h3>Global High-Utility Itemsets ({len(self.global_results)} found)</h3>
"""
        
        if self.global_results:
            html += """
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
"""
            
            for i, itemset_data in enumerate(self.global_results, 1):
                items = list(itemset_data['itemset'])
                items_str = ", ".join(items)
                utility = itemset_data['utility']
                support = itemset_data['support']
                item_count = len(items)
                
                html += f"""
                <tr>
                    <td>{i}</td>
                    <td><span class="itemset">{items_str}</span></td>
                    <td class="utility">{utility:.2f}</td>
                    <td class="support">{support:.2f}</td>
                    <td>{item_count}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
"""
        else:
            html += """
        <p><em>No high-utility itemsets found.</em></p>
"""
        
        # Add client results if available
        if self.client_results:
            html += """
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
"""
            
            for client_id, client_data in self.client_results.items():
                itemsets = client_data['itemsets']
                stats = client_data['stats']
                local_utility = stats.get('local_utility_sum', 0)
                
                html += f"""
                <tr>
                    <td>{client_id}</td>
                    <td>{len(itemsets)}</td>
                    <td class="utility">{local_utility:.2f}</td>
                </tr>
"""
            
            html += """
            </tbody>
        </table>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def save_all_formats(self, base_filename: str = None) -> Dict[str, str]:
        """Save results in all available formats"""
        if base_filename is None:
            base_filename = f"federated_results_{self.timestamp}"
        
        results = {}
        
        # Save in all formats
        results['text'] = self.save_text_file(f"{base_filename}.txt")
        results['json'] = self.save_json_file(f"{base_filename}.json")
        results['csv'] = self.save_csv_file(f"{base_filename}.csv")
        results['html'] = self.save_html_file(f"{base_filename}.html")
        
        logger.info(f"Results saved in all formats to: {self.output_dir}")
        return results
    
    def print_console_summary(self):
        """Print a summary to console"""
        print(self.format_console_output())

def create_sample_output():
    """Create a sample output for demonstration"""
    formatter = FederatedLearningOutputFormatter()
    
    # Sample global results
    sample_itemsets = [
        {'itemset': frozenset(['rice', 'egg']), 'utility': 85.5, 'support': 0.15},
        {'itemset': frozenset(['milk', 'bread', 'butter']), 'utility': 72.3, 'support': 0.08},
        {'itemset': frozenset(['sugar']), 'utility': 65.1, 'support': 0.25},
        {'itemset': frozenset(['rice', 'sugar']), 'utility': 58.7, 'support': 0.12},
        {'itemset': frozenset(['egg', 'milk']), 'utility': 52.4, 'support': 0.10}
    ]
    
    # Sample server stats
    sample_stats = {
        'total_transactions': 4141,
        'participating_clients': 3,
        'global_utility_sum': 334.0,
        'privacy_budget_used': 1.0
    }
    
    # Sample client results
    sample_client_results = {
        'client-1': {
            'itemsets': sample_itemsets[:3],
            'stats': {'local_utility_sum': 221.9, 'transaction_count': 1500}
        },
        'client-2': {
            'itemsets': sample_itemsets[2:],
            'stats': {'local_utility_sum': 176.2, 'transaction_count': 1200}
        }
    }
    
    # Add data to formatter
    formatter.add_global_results(sample_itemsets, sample_stats)
    for client_id, client_data in sample_client_results.items():
        formatter.add_client_results(client_id, client_data['itemsets'], client_data['stats'])
    
    # Save all formats
    results = formatter.save_all_formats("sample_results")
    
    print("Sample output files created:")
    for format_name, filepath in results.items():
        print(f"  {format_name.upper()}: {filepath}")
    
    print("\nConsole output preview:")
    formatter.print_console_summary()

if __name__ == '__main__':
    create_sample_output() 