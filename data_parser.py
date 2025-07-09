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
        cleaned_line = line.strip().strip('"')
        if ':' not in cleaned_line:
            print(f"Warning: No utility/quantity info in line: {line}")
            return []

        try:
            items_part, utilities_part, quantities_part = cleaned_line.split(':')
            item_ids = items_part.strip().split()
            utilities = [float(u) for u in utilities_part.strip().split()]
            quantities = [int(q) for q in quantities_part.strip().split()]

            if len(item_ids) != len(quantities) or len(item_ids) != len(utilities):
                print(f"Warning: Mismatch between items, utilities, and quantities in line: {line}")
                return []

            transaction_item_tuples = []
            for item_id, quantity, utility in zip(item_ids, quantities, utilities):
                transaction_item_tuples.append((item_id, quantity, utility))

            return transaction_item_tuples
        except Exception as e:
            print(f"Error parsing line: {line}\n{e}")
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
            if len(self.transactions) != 4141:
                print(f"Warning: Expected 4141 transactions, but found {len(self.transactions)}")
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