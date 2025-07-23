# DataProcessor.py

import os
import random


class DataProcessor:
    def __init__(self, dataset_path):
        """Initialize the DataProcessor with the dataset file path."""
        self.dataset_path = dataset_path
        self.transactions = []
        self.external_utility = {}

    def parse_foodmart_transaction_line(self, line):
        """
        Parses a line in the format:
        item_id1 item_id2 ... item_idN:utility1 utility2 ... utilityN:quantity1 quantity2 ... quantityN
        Returns a list of (item_id, quantity, utility) tuples.
        """
        # Clean the line and remove quotes
        cleaned_line = line.strip().strip('"')
        
        # Remove any line breaks within the string
        cleaned_line = cleaned_line.replace('\n', ' ').replace('\r', ' ')
        
        if ':' not in cleaned_line:
            print(f"Warning: No utility/quantity info in line: {line[:100]}...")
            return []

        try:
            parts = cleaned_line.split(':')
            if len(parts) != 3:
                print(f"Warning: Expected 3 parts (items:utilities:quantities), got {len(parts)} in line: {line[:100]}...")
                return []
                
            items_part, utilities_part, quantities_part = parts
            
            # Clean and split each part
            item_ids = [item.strip() for item in items_part.strip().split() if item.strip()]
            utilities = [float(u.strip()) for u in utilities_part.strip().split() if u.strip()]
            quantities = [int(q.strip()) for q in quantities_part.strip().split() if q.strip()]

            if len(item_ids) != len(quantities) or len(item_ids) != len(utilities):
                print(f"Warning: Mismatch between items ({len(item_ids)}), utilities ({len(utilities)}), and quantities ({len(quantities)}) in line: {line[:100]}...")
                return []

            transaction_item_tuples = []
            for item_id, quantity, utility in zip(item_ids, quantities, utilities):
                transaction_item_tuples.append((item_id, quantity, utility))

            return transaction_item_tuples
        except Exception as e:
            print(f"Error parsing line: {line[:100]}...\n{e}")
            return []

    def load_foodmart_transactions_as_tuple(self):
        """
        Loads transactions from a FoodMart-formatted file.
        Each transaction will be a list of (item_id_str, quantity, utility) tuples.
        """
        self.transactions = []
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        parsed_tx_tuples = self.parse_foodmart_transaction_line(line)
                        if parsed_tx_tuples:
                            self.transactions.append(parsed_tx_tuples)
            print(f"Loaded {len(self.transactions)} transactions from {self.dataset_path}")
            # Updated expected transaction count for new dataset size
            if len(self.transactions) != 4000:
                print(f"Warning: Expected 4000 transactions, but found {len(self.transactions)}")
        except FileNotFoundError:
            print(f"Error: File not found at {self.dataset_path}")
            self.transactions = []
        except Exception as e:
            print(f"An error occurred while reading {self.dataset_path}: {e}")
            self.transactions = []
        return self.transactions

    def get_dummy_foodmart_item_utilities(self):
        """
        Generates DUMMY item utilities. For real analysis, these MUST be provided.
        Assigns a random utility between 1 and 10 for each unique item found.
        """
        print("\nGenerating DUMMY item utilities. ")
        all_items = set()
        for tx_tuples in self.transactions:
            for item_id_str, _, _ in tx_tuples:
                all_items.add(item_id_str)

        self.external_utility = {item: random.randint(20, 100) for item in all_items}
        print(f"\nGenerated utilities for {len(self.external_utility)} items. Sample: {list(self.external_utility.items())[:5]}")
        return self.external_utility