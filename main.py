#!/usr/bin/env python3
"""
Main script to test FP-Growth algorithm for High-Utility Itemset Mining
Takes user input for minimum utility threshold and uses the generated foodmart dataset
"""

import sys
import os
import time
from typing import List, Dict, Set, Tuple

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from data_parser import DataProcessor
from preprocessor import construct_pruned_item_list
from fp_tree_builder import construct_huim_fp_tree
from hui_miner import HUIMiner
from config import get_min_utility_threshold, set_min_utility_threshold

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from data_parser import DataProcessor
        print("✅ DataProcessor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DataProcessor: {e}")
        return False
    
    try:
        from preprocessor import construct_pruned_item_list
        print("✅ Preprocessor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import preprocessor: {e}")
        return False
    
    try:
        from fp_tree_builder import construct_huim_fp_tree
        print("✅ FP-Tree builder imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import fp_tree_builder: {e}")
        return False
    
    try:
        from hui_miner import HUIMiner
        print("✅ HUIMiner imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import hui_miner: {e}")
        return False
    
    try:
        from config import get_min_utility_threshold, set_min_utility_threshold
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    return True

def get_user_input() -> float:
    """Get minimum utility threshold from user"""
    print("\n" + "="*60)
    print("FP-Growth High-Utility Itemset Mining Test")
    print("="*60)
    
    # Show current default threshold
    try:
        current_threshold = get_min_utility_threshold()
    except NameError:
        current_threshold = 100  # Default fallback
    print(f"Current default minimum utility threshold: {current_threshold}")
    
    while True:
        try:
            user_input = input("\nEnter minimum utility threshold (or press Enter for default): ").strip()
            
            if not user_input:  # User pressed Enter
                threshold = current_threshold
                print(f"Using default threshold: {threshold}")
                break
            
            threshold = float(user_input)
            if threshold < 0:
                print("❌ Threshold must be non-negative. Please try again.")
                continue
            
            print(f"Using threshold: {threshold}")
            break
            
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
            continue
    
    return threshold

def load_dataset() -> Tuple[List, Dict]:
    """Load the generated foodmart dataset"""
    print("\nLoading dataset...")
    
    # Check if dataset file exists
    dataset_path = "generated_foodmart_dataset.csv"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found: {dataset_path}")
        print("Available dataset files:")
        for file in os.listdir("."):
            if "foodmart" in file.lower() and file.endswith(".csv"):
                print(f"  - {file}")
        return [], {}
    
    try:
        # Load dataset using DataProcessor
        processor = DataProcessor(dataset_path)
        transactions = processor.load_foodmart_transactions_as_tuple()
        
        if not transactions:
            print("❌ No transactions loaded from dataset")
            return [], {}
        
        # Generate external utility values
        external_utility = processor.get_dummy_foodmart_item_utilities()
        
        print(f"✅ Dataset loaded successfully:")
        print(f"   - Transactions: {len(transactions)}")
        print(f"   - Unique items: {len(external_utility)}")
        print(f"   - Sample transaction: {transactions[0] if transactions else 'None'}")
        
        return transactions, external_utility
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return [], {}

def run_fp_growth_mining(transactions: List, external_utility: Dict, min_utility_threshold: float):
    """Run the complete FP-Growth mining process"""
    print(f"\nRunning FP-Growth mining with threshold: {min_utility_threshold}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Step 1: Prune low-utility items
        print("Step 1: Pruning low-utility items...")
        sorted_items = construct_pruned_item_list(transactions, min_utility_threshold, external_utility)
        print(f"   - High-utility items after pruning: {len(sorted_items)}")
        if sorted_items:
            print(f"   - Top 5 items: {sorted_items[:5]}")
        
        if not sorted_items:
            print("❌ No items meet the minimum utility threshold")
            return []
        
        # Step 2: Construct FP-Tree
        print("\nStep 2: Constructing FP-Tree...")
        root, header_table = construct_huim_fp_tree(transactions, sorted_items, external_utility)
        print(f"   - FP-Tree constructed successfully")
        print(f"   - Header table size: {len(header_table)}")
        
        # Step 3: Mine high-utility itemsets
        print("\nStep 3: Mining high-utility itemsets...")
        miner = HUIMiner(external_utility, min_utility_threshold)
        huis = miner.mine_huis_pseudo_projection(header_table, root)
        
        # Convert to list format for easier processing
        results = []
        for itemset in huis:
            items = list(itemset)
            # Calculate utility and support
            utility = calculate_itemset_utility(items, transactions, external_utility)
            support = calculate_itemset_support(items, transactions)
            
            results.append({
                'itemset': itemset,
                'items': items,
                'utility': utility,
                'support': support
            })
        
        # Sort by utility (descending)
        results.sort(key=lambda x: x['utility'], reverse=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n✅ Mining completed successfully!")
        print(f"   - Execution time: {execution_time:.2f} seconds")
        print(f"   - High-utility itemsets found: {len(results)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during mining: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_itemset_utility(items: List[str], transactions: List, external_utility: Dict) -> float:
    """Calculate utility of an itemset"""
    total_utility = 0.0
    for tx in transactions:
        tx_items = {item for item, _, _ in tx}
        if all(item in tx_items for item in items):
            # Calculate utility for this transaction
            tx_utility = 0.0
            for item in items:
                # Find the item in transaction and get its quantity
                for tx_item, quantity, _ in tx:
                    if tx_item == item:
                        tx_utility += quantity * external_utility.get(item, 0)
                        break
            total_utility += tx_utility
    return total_utility

def calculate_itemset_support(items: List[str], transactions: List) -> float:
    """Calculate support (frequency) of an itemset"""
    support_count = 0
    for tx in transactions:
        tx_items = {item for item, _, _ in tx}
        if all(item in tx_items for item in items):
            support_count += 1
    
    return support_count / len(transactions) if transactions else 0.0

def display_results(results: List, min_utility_threshold: float):
    """Display mining results"""
    if not results:
        print("\n❌ No high-utility itemsets found")
        return
    
    print(f"\n" + "="*60)
    print(f"MINING RESULTS (Threshold: {min_utility_threshold})")
    print("="*60)
    
    print(f"Found {len(results)} high-utility itemsets:")
    print("-" * 60)
    
    # Display top 20 results
    max_display = min(20, len(results))
    for i, result in enumerate(results[:max_display], 1):
        items = result['items']
        utility = result['utility']
        support = result['support']
        
        print(f"{i:2d}. Itemset: {{{', '.join(items)}}}")
        print(f"    Utility: {utility:.2f}")
        print(f"    Support: {support:.4f} ({support*100:.2f}%)")
        print()
    
    if len(results) > max_display:
        print(f"... and {len(results) - max_display} more itemsets")
    
    # Summary statistics
    utilities = [r['utility'] for r in results]
    supports = [r['support'] for r in results]
    
    print("Summary Statistics:")
    print(f"  - Average utility: {sum(utilities)/len(utilities):.2f}")
    print(f"  - Max utility: {max(utilities):.2f}")
    print(f"  - Min utility: {min(utilities):.2f}")
    print(f"  - Average support: {sum(supports)/len(supports):.4f}")

def save_results(results: List, min_utility_threshold: float):
    """Save results to file"""
    if not results:
        return
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"fp_growth_results_threshold_{min_utility_threshold}_{timestamp}.txt"
    
    try:
        with open(filename, 'w') as f:
            f.write(f"FP-Growth Mining Results\n")
            f.write(f"Minimum Utility Threshold: {min_utility_threshold}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Itemsets Found: {len(results)}\n")
            f.write("="*60 + "\n\n")
            
            for i, result in enumerate(results, 1):
                items = result['items']
                utility = result['utility']
                support = result['support']
                
                f.write(f"{i:3d}. Itemset: {{{', '.join(items)}}}\n")
                f.write(f"     Utility: {utility:.2f}\n")
                f.write(f"     Support: {support:.4f} ({support*100:.2f}%)\n\n")
        
        print(f"✅ Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def main():
    """Main function"""
    print("🔍 FP-Growth Algorithm Test")
    print("="*60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your installation.")
        return
    
    # Get user input
    min_utility_threshold = get_user_input()
    
    # Load dataset
    transactions, external_utility = load_dataset()
    if not transactions:
        print("\n❌ Failed to load dataset. Exiting.")
        return
    
    # Run FP-Growth mining
    results = run_fp_growth_mining(transactions, external_utility, min_utility_threshold)
    
    # Display results
    display_results(results, min_utility_threshold)
    
    # Save results
    save_results(results, min_utility_threshold)
    
    print(f"\n" + "="*60)
    print("Test completed successfully!")
    print("="*60)

if __name__ == '__main__':
    main() 