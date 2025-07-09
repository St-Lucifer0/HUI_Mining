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
    dataset_path = "generated_foodmart_dataset.csv"
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
    # external_utility = processor.get_dummy_foodmart_item_utilities()  # No longer needed
    min_util = 30  # Lowered from 50 to 30 for more frequent high-utility itemsets
    epsilon = 1.0

    try:
        # Prune low-utility items
        print("\n🔍 Pruning low-utility items...")
        sorted_items = construct_pruned_item_list(transactions, min_util, None) # Pass None for external_utility
        print(f"✅ High-Utility items (sorted by TWU): {len(sorted_items)} items")

        # Construct initial FP-Tree
        print("\n🌳 Constructing HUIM FP-Tree...")
        root, header_table = construct_huim_fp_tree(transactions, sorted_items, None) # Pass None for external_utility
        print("✅ FP-Tree constructed successfully")

        # Mine high-utility itemsets
        print("\n⛏️ Mining High-Utility Itemsets...")
        miner = HUIMiner(None, min_util) # Pass None for external_utility
        high_utility_itemsets = miner.mine_huis_pseudo_projection(header_table, root)
        print(f"✅ Found {len(high_utility_itemsets)} high-utility itemsets")

        # DEBUG: Print first 5 itemsets and transactions to check types/values
        print("\nDEBUG: First 5 mined itemsets:")
        for idx, itemset in enumerate(list(high_utility_itemsets)[:5]):
            print(f"Itemset {idx+1}: {itemset} (type: {type(itemset)})")
            if isinstance(itemset, (set, frozenset, list, tuple)):
                for item in itemset:
                    print(f"  - {item} (type: {type(item)})")
        print("\nDEBUG: First 5 transactions (item IDs):")
        for idx, tx in enumerate(transactions[:5]):
            tx_items = [x[0] for x in tx]
            print(f"Transaction {idx+1}: {tx_items} (types: {[type(x[0]) for x in tx]})")

        # Print a few example transactions for reference
        print("\nExample transactions (first 5):")
        for idx, tx in enumerate(transactions[:5]):
            print(f"Transaction {idx+1}: {[x[0] for x in tx]}")

        # Filter itemsets to only include those with size 2 or 3
        min_size = 2
        max_size = 3
        high_utility_itemsets = [iset for iset in high_utility_itemsets if min_size <= len(iset) <= max_size]
        print(f"\nFiltered to {len(high_utility_itemsets)} itemsets of size {min_size} to {max_size}.")

        # Create item utilities dictionary from transaction data
        print(f"\n🔒 Creating item utilities dictionary for privacy-preserving mining...")
        item_utils_dict = {}
        for tx in transactions:
            for item_id, _, utility in tx:
                if item_id not in item_utils_dict:
                    item_utils_dict[item_id] = 0
                item_utils_dict[item_id] += utility
        
        # Convert transactions to format expected by privacy wrapper: [{'item': count}, ...]
        print(f"\n🔒 Converting transactions to privacy wrapper format...")
        privacy_transactions = []
        for tx in transactions:
            tx_dict = {}
            for item_id, quantity, _ in tx:
                tx_dict[item_id] = quantity
            privacy_transactions.append(tx_dict)
        
        # Privacy-preserving mining
        print(f"\n🔒 Running Privacy-Preserving HUI Mining...")
        privacy_itemsets = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
            transactions_list=privacy_transactions,
            item_utils_dict=item_utils_dict,
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
            items = list(itemset)
            # Calculate actual utility and support for this itemset using real utility from data
            utility = 0
            support_count = 0
            
            for tx in transactions:
                tx_items = [x[0] for x in tx]  # Get item IDs from transaction
                tx_utilities = {x[0]: x[2] for x in tx}  # Get utility from transaction
                print(f"Checking itemset: {items} in transaction: {tx_items}")
                # Check if all items in itemset are present in transaction
                if all(item in tx_items for item in items):
                    print(f"MATCH FOUND for itemset {items} in transaction {tx_items}")
                    support_count += 1
                    # Calculate utility for this transaction (sum the utility field for each item in the itemset)
                    for item in items:
                        utility += tx_utilities.get(item, 0)
            
            support = support_count / len(transactions) if transactions else 0
            
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