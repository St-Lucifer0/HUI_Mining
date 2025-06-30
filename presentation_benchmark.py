#!/usr/bin/env python3
"""
Presentation Benchmarking Tools for HUI Mining System
Easy-to-use functions for checking memory usage and runtime speed
"""

import time
import psutil
import os
from datetime import datetime
from performance_monitor import PerformanceMonitor, monitor_operation, quick_benchmark

def check_system_resources():
    """Check current system resources - perfect for presentation start"""
    print("🖥️ SYSTEM RESOURCES CHECK")
    print("=" * 50)
    
    # CPU Info
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"🖥️  CPU Cores: {cpu_count}")
    print(f"🖥️  Current CPU Usage: {cpu_percent:.1f}%")
    
    # Memory Info
    memory = psutil.virtual_memory()
    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    used_gb = memory.used / (1024**3)
    memory_percent = memory.percent
    
    print(f"💾 Total Memory: {total_gb:.1f} GB")
    print(f"💾 Available Memory: {available_gb:.1f} GB")
    print(f"💾 Used Memory: {used_gb:.1f} GB ({memory_percent:.1f}%)")
    
    # Disk Info
    disk = psutil.disk_usage('/')
    disk_total_gb = disk.total / (1024**3)
    disk_free_gb = disk.free / (1024**3)
    disk_percent = (disk.used / disk.total) * 100
    
    print(f"💿 Total Disk: {disk_total_gb:.1f} GB")
    print(f"💿 Free Disk: {disk_free_gb:.1f} GB")
    print(f"💿 Disk Usage: {disk_percent:.1f}%")
    
    print("=" * 50)
    return {
        'cpu_cores': cpu_count,
        'cpu_usage': cpu_percent,
        'memory_total_gb': total_gb,
        'memory_available_gb': available_gb,
        'memory_used_gb': used_gb,
        'memory_percent': memory_percent,
        'disk_total_gb': disk_total_gb,
        'disk_free_gb': disk_free_gb,
        'disk_percent': disk_percent
    }

def benchmark_data_loading():
    """Benchmark data loading performance"""
    print("\n📊 BENCHMARKING DATA LOADING")
    print("=" * 50)
    
    from data_parser import DataProcessor
    
    monitor = PerformanceMonitor(enable_live_monitoring=True)
    monitor.start_monitoring("Data Loading")
    
    try:
        processor = DataProcessor("foodmart_dataset_csv.csv")
        transactions = processor.load_foodmart_transactions_as_tuple()
        external_utility = processor.get_dummy_foodmart_item_utilities()
        
        results = monitor.end_monitoring({
            'transactions_loaded': len(transactions),
            'utility_items': len(external_utility),
            'file_size_mb': os.path.getsize("foodmart_dataset_csv.csv") / (1024*1024)
        })
        
        print(f"✅ Loaded {len(transactions)} transactions")
        print(f"✅ Loaded {len(external_utility)} utility items")
        return results
        
    except Exception as e:
        monitor.end_monitoring({'error': str(e)})
        print(f"❌ Data loading failed: {e}")
        return None

def benchmark_mining_phases():
    """Benchmark each mining phase separately"""
    print("\n⛏️ BENCHMARKING MINING PHASES")
    print("=" * 50)
    
    from data_parser import DataProcessor
    from preprocessor import construct_pruned_item_list
    from fp_tree_builder import construct_huim_fp_tree
    from hui_miner import HUIMiner
    
    # Load data first
    processor = DataProcessor("foodmart_dataset_csv.csv")
    transactions = processor.load_foodmart_transactions_as_tuple()
    external_utility = processor.get_dummy_foodmart_item_utilities()
    min_util = 100
    
    phases = {}
    
    # Phase 1: Pruning
    print("🔍 Phase 1: Item Pruning...")
    monitor = PerformanceMonitor(enable_live_monitoring=True)
    monitor.start_monitoring("Item Pruning")
    
    sorted_items = construct_pruned_item_list(transactions, min_util, external_utility)
    phases['pruning'] = monitor.end_monitoring({
        'items_after_pruning': len(sorted_items),
        'original_items': len(external_utility)
    })
    
    # Phase 2: FP-Tree Construction
    print("🌳 Phase 2: FP-Tree Construction...")
    monitor = PerformanceMonitor(enable_live_monitoring=True)
    monitor.start_monitoring("FP-Tree Construction")
    
    root, header_table = construct_huim_fp_tree(transactions, sorted_items, external_utility)
    phases['fp_tree'] = monitor.end_monitoring({
        'header_table_size': len(header_table),
        'tree_nodes': 'calculated'  # Could add tree node counting if needed
    })
    
    # Phase 3: Mining
    print("⛏️ Phase 3: HUI Mining...")
    monitor = PerformanceMonitor(enable_live_monitoring=True)
    monitor.start_monitoring("HUI Mining")
    
    miner = HUIMiner(external_utility, min_util)
    high_utility_itemsets = miner.mine_huis_pseudo_projection(header_table, root)
    phases['mining'] = monitor.end_monitoring({
        'itemsets_found': len(high_utility_itemsets)
    })
    
    return phases

def benchmark_privacy_mining():
    """Benchmark privacy-preserving mining"""
    print("\n🔒 BENCHMARKING PRIVACY-PRESERVING MINING")
    print("=" * 50)
    
    from data_parser import DataProcessor
    from privacy_wrapper import PrivacyPreservingHUIMining
    
    processor = DataProcessor("foodmart_dataset_csv.csv")
    transactions = processor.load_foodmart_transactions_as_tuple()
    external_utility = processor.get_dummy_foodmart_item_utilities()
    min_util = 100
    
    epsilon_values = [0.5, 1.0, 2.0]
    results = {}
    
    for epsilon in epsilon_values:
        print(f"🔒 Testing epsilon = {epsilon}...")
        monitor = PerformanceMonitor(enable_live_monitoring=True)
        monitor.start_monitoring(f"Privacy Mining (ε={epsilon})")
        
        try:
            privacy_itemsets = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
                transactions_list=transactions,
                item_utils_dict=external_utility,
                minutil_threshold=min_util,
                epsilon=epsilon,
                num_mpc_workers=3
            )
            
            results[f'epsilon_{epsilon}'] = monitor.end_monitoring({
                'epsilon': epsilon,
                'itemsets_found': len(privacy_itemsets) if privacy_itemsets else 0,
                'privacy_budget_used': epsilon
            })
            
        except Exception as e:
            results[f'epsilon_{epsilon}'] = monitor.end_monitoring({
                'epsilon': epsilon,
                'error': str(e)
            })
    
    return results

def run_full_benchmark():
    """Run complete benchmark suite"""
    print("🚀 STARTING FULL BENCHMARK SUITE")
    print("=" * 60)
    
    # Check system resources
    system_info = check_system_resources()
    
    # Benchmark data loading
    loading_results = benchmark_data_loading()
    
    # Benchmark mining phases
    mining_phases = benchmark_mining_phases()
    
    # Benchmark privacy mining
    privacy_results = benchmark_privacy_mining()
    
    # Compile final report
    final_report = {
        'timestamp': datetime.now().isoformat(),
        'system_info': system_info,
        'data_loading': loading_results,
        'mining_phases': mining_phases,
        'privacy_mining': privacy_results
    }
    
    # Save comprehensive report
    import json
    os.makedirs("results", exist_ok=True)
    report_file = f"results/full_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n📄 Full benchmark report saved: {report_file}")
    print("=" * 60)
    print("🎉 BENCHMARK SUITE COMPLETE!")
    print("=" * 60)
    
    return final_report

def quick_performance_check():
    """Quick performance check for presentations"""
    print("⚡ QUICK PERFORMANCE CHECK")
    print("=" * 40)
    
    # System resources
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    print(f"🖥️  CPU Usage: {cpu_percent:.1f}%")
    print(f"💾 Memory Usage: {memory.percent:.1f}%")
    print(f"💾 Available: {memory.available / (1024**3):.1f} GB")
    
    # Quick data loading test
    try:
        start_time = time.time()
        from data_parser import DataProcessor
        processor = DataProcessor("foodmart_dataset_csv.csv")
        transactions = processor.load_foodmart_transactions_as_tuple()
        load_time = time.time() - start_time
        
        print(f"📊 Data Load Time: {load_time:.2f}s")
        print(f"📊 Transactions: {len(transactions)}")
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
    
    print("=" * 40)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "system":
            check_system_resources()
        elif command == "loading":
            benchmark_data_loading()
        elif command == "phases":
            benchmark_mining_phases()
        elif command == "privacy":
            benchmark_privacy_mining()
        elif command == "full":
            run_full_benchmark()
        elif command == "quick":
            quick_performance_check()
        else:
            print("Usage: python presentation_benchmark.py [system|loading|phases|privacy|full|quick]")
    else:
        print("🎯 PRESENTATION BENCHMARKING TOOLS")
        print("=" * 50)
        print("Available commands:")
        print("  system  - Check system resources")
        print("  loading - Benchmark data loading")
        print("  phases  - Benchmark mining phases")
        print("  privacy - Benchmark privacy mining")
        print("  full    - Run complete benchmark suite")
        print("  quick   - Quick performance check")
        print("=" * 50)
        print("Example: python presentation_benchmark.py quick") 