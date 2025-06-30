#!/usr/bin/env python3
"""
Performance Benchmarking for FP-Growth Federated Learning System
"""

import time
import psutil
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd

class PerformanceBenchmark:
    """Benchmark the performance of the federated learning system"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.start_memory = None
        
    def start_benchmark(self, test_name: str):
        """Start timing and memory tracking"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"🔄 Starting benchmark: {test_name}")
        
    def end_benchmark(self, test_name: str, additional_metrics: Dict = None):
        """End timing and record results"""
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        duration = end_time - self.start_time
        memory_used = end_memory - self.start_memory
        
        self.results[test_name] = {
            'duration_seconds': duration,
            'memory_mb': memory_used,
            'peak_memory_mb': end_memory,
            'timestamp': datetime.now().isoformat(),
            **additional_metrics or {}
        }
        
        print(f"✅ {test_name}: {duration:.2f}s, Memory: {memory_used:.2f}MB")
        
    def benchmark_single_mining(self, dataset_size: int = 1000):
        """Benchmark single client mining performance"""
        from data_parser import DataProcessor
        from preprocessor import construct_pruned_item_list
        from fp_tree_builder import construct_huim_fp_tree
        from hui_miner import HUIMiner
        
        self.start_benchmark(f"single_mining_{dataset_size}")
        
        # Load data
        processor = DataProcessor("foodmart_dataset_csv.csv")
        transactions = processor.load_foodmart_transactions_as_tuple()[:dataset_size]
        external_utility = processor.get_dummy_foodmart_item_utilities()
        
        # Run mining
        min_util = 50
        sorted_items = construct_pruned_item_list(transactions, min_util, external_utility)
        root, header_table = construct_huim_fp_tree(transactions, sorted_items, external_utility)
        miner = HUIMiner(external_utility, min_util)
        itemsets = miner.mine_huis_pseudo_projection(header_table, root)
        
        self.end_benchmark(f"single_mining_{dataset_size}", {
            'transactions': len(transactions),
            'itemsets_found': len(itemsets),
            'items_processed': len(sorted_items)
        })
        
    def benchmark_privacy_mining(self, epsilon_values: List[float] = [0.5, 1.0, 2.0]):
        """Benchmark privacy-preserving mining with different epsilon values"""
        from privacy_wrapper import PrivacyPreservingHUIMining
        from data_parser import DataProcessor
        
        processor = DataProcessor("foodmart_dataset_csv.csv")
        transactions = processor.load_foodmart_transactions_as_tuple()[:1000]
        external_utility = processor.get_dummy_foodmart_item_utilities()
        min_util = 50
        
        for epsilon in epsilon_values:
            self.start_benchmark(f"privacy_mining_epsilon_{epsilon}")
            
            itemsets = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
                transactions_list=transactions,
                item_utils_dict=external_utility,
                minutil_threshold=min_util,
                epsilon=epsilon,
                num_mpc_workers=3
            )
            
            self.end_benchmark(f"privacy_mining_epsilon_{epsilon}", {
                'epsilon': epsilon,
                'itemsets_found': len(itemsets),
                'privacy_budget_used': epsilon
            })
            
    def benchmark_federated_rounds(self, num_clients: int = 3, num_rounds: int = 3):
        """Benchmark federated learning rounds"""
        from federated_client import FederatedLearningClient
        from federated_server import FederatedLearningServer
        import threading
        import time
        
        self.start_benchmark(f"federated_{num_clients}_clients_{num_rounds}_rounds")
        
        # Start server
        server = FederatedLearningServer(min_utility_threshold=50, epsilon=1.0, num_rounds=num_rounds)
        server_thread = threading.Thread(target=server.start, args=('localhost', 50051))
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Start clients
        client_threads = []
        for i in range(num_clients):
            client = FederatedLearningClient(
                client_id=f"benchmark-client-{i}",
                server_address="localhost",
                server_port=50051,
                min_utility_threshold=50,
                epsilon=1.0
            )
            thread = threading.Thread(target=client.run_federated_learning)
            thread.daemon = True
            thread.start()
            client_threads.append(thread)
            
        # Wait for completion
        for thread in client_threads:
            thread.join()
            
        self.end_benchmark(f"federated_{num_clients}_clients_{num_rounds}_rounds", {
            'num_clients': num_clients,
            'num_rounds': num_rounds,
            'total_communication': num_clients * num_rounds
        })
        
    def benchmark_scalability(self, client_counts: List[int] = [1, 2, 3, 5, 10]):
        """Benchmark system scalability with different client counts"""
        for num_clients in client_counts:
            self.benchmark_federated_rounds(num_clients, 1)
            
    def generate_report(self, output_file: str = "performance_report.json"):
        """Generate comprehensive performance report"""
        report = {
            'benchmark_info': {
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'cpu_count': psutil.cpu_count(),
                    'total_memory_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                    'python_version': os.sys.version
                }
            },
            'results': self.results,
            'summary': self._generate_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📊 Performance report saved to: {output_file}")
        return report
        
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if not self.results:
            return {}
            
        durations = [r['duration_seconds'] for r in self.results.values()]
        memories = [r['memory_mb'] for r in self.results.values()]
        
        return {
            'total_tests': len(self.results),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'avg_memory': sum(memories) / len(memories),
            'max_memory': max(memories),
            'min_memory': min(memories)
        }
        
    def plot_results(self, output_file: str = "performance_charts.png"):
        """Generate performance visualization charts"""
        if not self.results:
            print("No results to plot")
            return
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Duration comparison
        test_names = list(self.results.keys())
        durations = [self.results[name]['duration_seconds'] for name in test_names]
        ax1.bar(range(len(test_names)), durations)
        ax1.set_title('Execution Time Comparison')
        ax1.set_ylabel('Duration (seconds)')
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels(test_names, rotation=45)
        
        # Memory usage comparison
        memories = [self.results[name]['memory_mb'] for name in test_names]
        ax2.bar(range(len(test_names)), memories, color='orange')
        ax2.set_title('Memory Usage Comparison')
        ax2.set_ylabel('Memory (MB)')
        ax2.set_xticks(range(len(test_names)))
        ax2.set_xticklabels(test_names, rotation=45)
        
        # Scalability analysis
        scalability_tests = [name for name in test_names if 'federated_' in name]
        if scalability_tests:
            client_counts = []
            scalability_durations = []
            for test in scalability_tests:
                # Extract client count from test name
                parts = test.split('_')
                if len(parts) >= 3:
                    try:
                        client_count = int(parts[1])
                        client_counts.append(client_count)
                        scalability_durations.append(self.results[test]['duration_seconds'])
                    except ValueError:
                        continue
                        
            if client_counts:
                ax3.plot(client_counts, scalability_durations, 'bo-')
                ax3.set_title('Scalability Analysis')
                ax3.set_xlabel('Number of Clients')
                ax3.set_ylabel('Duration (seconds)')
                ax3.grid(True)
        
        # Privacy impact analysis
        privacy_tests = [name for name in test_names if 'privacy_mining' in name]
        if privacy_tests:
            epsilons = []
            privacy_durations = []
            for test in privacy_tests:
                epsilon = self.results[test].get('epsilon', 0)
                epsilons.append(epsilon)
                privacy_durations.append(self.results[test]['duration_seconds'])
                
            ax4.plot(epsilons, privacy_durations, 'ro-')
            ax4.set_title('Privacy Impact Analysis')
            ax4.set_xlabel('Epsilon (Privacy Budget)')
            ax4.set_ylabel('Duration (seconds)')
            ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📈 Performance charts saved to: {output_file}")
        
def main():
    """Run comprehensive performance benchmarks"""
    print("🚀 Starting Performance Benchmarking")
    print("=" * 60)
    
    benchmark = PerformanceBenchmark()
    
    # Run benchmarks
    print("\n1. Single Mining Performance")
    benchmark.benchmark_single_mining(500)
    benchmark.benchmark_single_mining(1000)
    benchmark.benchmark_single_mining(2000)
    
    print("\n2. Privacy-Preserving Mining Performance")
    benchmark.benchmark_privacy_mining([0.5, 1.0, 2.0])
    
    print("\n3. Federated Learning Performance")
    benchmark.benchmark_federated_rounds(2, 2)
    benchmark.benchmark_federated_rounds(3, 3)
    
    print("\n4. Scalability Analysis")
    benchmark.benchmark_scalability([1, 2, 3])
    
    # Generate reports
    print("\n5. Generating Reports")
    report = benchmark.generate_report("results/performance_benchmark.json")
    benchmark.plot_results("results/performance_charts.png")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)
    summary = report['summary']
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Average Duration: {summary['avg_duration']:.2f}s")
    print(f"Average Memory: {summary['avg_memory']:.2f}MB")
    print(f"Fastest Test: {summary['min_duration']:.2f}s")
    print(f"Slowest Test: {summary['max_duration']:.2f}s")
    
    print("\n✅ Performance benchmarking completed!")
    print("📁 Check 'results/' directory for detailed reports")

if __name__ == "__main__":
    main() 