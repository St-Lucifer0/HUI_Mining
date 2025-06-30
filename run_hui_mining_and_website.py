#!/usr/bin/env python3
"""
Script to run HUI mining on CSV data and display results on a website
"""

import os
import sys
import webbrowser
import time
from datetime import datetime
from preprocessor import construct_pruned_item_list
from fp_tree_builder import construct_huim_fp_tree
from fp_tree_updater import incremental_fp_tree_update
from hui_miner import HUIMiner
from privacy_wrapper import PrivacyPreservingHUIMining
from data_parser import DataProcessor
from output_formatter import FederatedLearningOutputFormatter
from performance_monitor import PerformanceMonitor, monitor_operation, quick_benchmark

def run_hui_mining_and_create_website():
    """Run HUI mining and create a website to display results"""
    
    # Initialize performance monitor
    monitor = PerformanceMonitor(enable_live_monitoring=True)
    monitor.start_monitoring("HUI Mining and Website Generation")
    
    print("🚀 Starting HUI Mining and Website Generation")
    print("=" * 60)
    
    # Initialize DataProcessor with FoodMart dataset path
    dataset_path = "foodmart_dataset_csv.csv"
    processor = DataProcessor(dataset_path)

    # Load FoodMart Transactions
    print("📊 Loading transactions from CSV...")
    transactions = processor.load_foodmart_transactions_as_tuple()
    if not transactions:
        print("❌ Failed to load transactions... EXITING!")
        monitor.end_monitoring({'success': False, 'error': 'Failed to load transactions'})
        return False

    print(f"✅ Loaded {len(transactions)} transactions")

    # Get utilities and set parameters
    external_utility = processor.get_dummy_foodmart_item_utilities()
    min_util = 100
    epsilon = 1.0

    try:
        # Prune low-utility items
        print("\n🔍 Pruning low-utility items...")
        sorted_items = construct_pruned_item_list(transactions, min_util, external_utility)
        print(f"✅ High-Utility items (sorted by TWU): {len(sorted_items)} items")

        # Construct initial FP-Tree
        print("\n🌳 Constructing HUIM FP-Tree...")
        root, header_table = construct_huim_fp_tree(transactions, sorted_items, external_utility)
        print("✅ FP-Tree constructed successfully")

        # Mine high-utility itemsets
        print("\n⛏️ Mining High-Utility Itemsets...")
        miner = HUIMiner(external_utility, min_util)
        high_utility_itemsets = miner.mine_huis_pseudo_projection(header_table, root)
        print(f"✅ Found {len(high_utility_itemsets)} high-utility itemsets")

        # Privacy-preserving mining
        print(f"\n🔒 Running Privacy-Preserving HUI Mining...")
        privacy_itemsets = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
            transactions_list=transactions,
            item_utils_dict=external_utility,
            minutil_threshold=min_util,
            epsilon=epsilon,
            num_mpc_workers=3
        )
        print(f"✅ Privacy-preserving mining completed")

        # Prepare results for output formatter
        print("\n📝 Preparing results for website...")
        
        # Convert itemsets to the format expected by output formatter
        formatted_itemsets = []
        for itemset in high_utility_itemsets:
            if isinstance(itemset, (list, tuple)):
                items = list(itemset)
            else:
                items = [str(itemset)]
            
            # Calculate utility and support
            utility = sum(external_utility.get(item, 0) for item in items)
            support = len([tx for tx in transactions if all(item in [x[0] for x in tx] for item in items)]) / len(transactions)
            
            formatted_itemsets.append({
                'itemset': set(items),
                'utility': utility,
                'support': support
            })

        # Sort by utility (descending)
        formatted_itemsets.sort(key=lambda x: x['utility'], reverse=True)

        # Create output formatter
        formatter = FederatedLearningOutputFormatter()
        
        # Add global results
        server_stats = {
            'total_transactions': len(transactions),
            'participating_clients': 1,
            'global_utility_sum': sum(item['utility'] for item in formatted_itemsets),
            'privacy_budget_used': epsilon
        }
        
        formatter.add_global_results(formatted_itemsets, server_stats)
        
        # Add client results (single client in this case)
        client_stats = {
            'local_utility_sum': sum(item['utility'] for item in formatted_itemsets),
            'local_transactions': len(transactions)
        }
        formatter.add_client_results("single-client", formatted_itemsets, client_stats)

        # Generate all output formats
        print("\n🌐 Generating website and output files...")
        output_files = formatter.save_all_formats()
        
        # Print console summary
        print("\n" + "=" * 60)
        print("📊 RESULTS SUMMARY")
        print("=" * 60)
        formatter.print_console_summary()
        
        # Open the HTML file in browser
        html_file = output_files.get('html')
        if html_file and os.path.exists(html_file):
            print(f"\n🌐 Opening results website: {html_file}")
            print("📁 All output files saved in 'results/' directory:")
            for format_type, filepath in output_files.items():
                print(f"   • {format_type.upper()}: {filepath}")
            
            # Wait a moment then open browser
            time.sleep(2)
            try:
                webbrowser.open(f'file://{os.path.abspath(html_file)}')
                print("✅ Website opened in your default browser!")
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
                print(f"📂 Please manually open: {html_file}")
        
        # End monitoring and get results
        performance_results = monitor.end_monitoring({
            'success': True,
            'transactions_processed': len(transactions),
            'high_utility_itemsets_found': len(high_utility_itemsets),
            'privacy_itemsets_found': len(privacy_itemsets) if privacy_itemsets else 0,
            'min_utility_threshold': min_util,
            'privacy_epsilon': epsilon
        })
        
        # Save performance report
        monitor.save_report(performance_results, "hui_mining_performance.json")
        
        print("\n" + "=" * 60)
        print("🎉 HUI Mining and Website Generation Complete!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        monitor.end_monitoring({'success': False, 'error': str(e)})
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🎯 HUI Mining with Website Display")
    print("=" * 60)
    print("This script will:")
    print("1. Load your CSV data (foodmart_dataset_csv.csv)")
    print("2. Run High-Utility Itemset Mining")
    print("3. Generate a beautiful website with results")
    print("4. Open the website in your browser")
    print("5. Save results in multiple formats (CSV, JSON, HTML, TXT)")
    print("=" * 60)
    
    success = run_hui_mining_and_create_website()
    
    if success:
        print("\n✅ Success! Check the 'results/' folder for all output files.")
        print("🌐 The HTML file contains a beautiful, interactive report.")
        print("📊 You can import the CSV into Excel for further analysis.")
    else:
        print("\n❌ Failed to complete the process. Check the error messages above.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 