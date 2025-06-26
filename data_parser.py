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
        Parses a single line from the dataset.
        Line format: "item1 item2 itemLastBeforeUtil: TotalUtil: SumProfits item4 item5"
        Returns a list of (item_id_str, quantity) tuples. Quantity is assumed 1.
        The utility block is currently ignored for item extraction.
        """
        cleaned_line = line.strip().strip('"')
        parts = cleaned_line.split(' ')
        transaction_item_tuples = []
        items_seen_in_this_line = set()

        for part in parts:
            try:
                if ':' in part:
                    # Handle items before the utility block separator
                    item_before_util = part.split(':')[0]
                    if item_before_util:
                        item_id_int = int(item_before_util)
                        item_id_str = str(item_id_int)
                        if item_id_str not in items_seen_in_this_line:
                            transaction_item_tuples.append((item_id_str, 1))
                            items_seen_in_this_line.add(item_id_str)
                else:
                    # Handle regular items (before or after utility block)
                    item_id_int = int(part)
                    item_id_str = str(item_id_int)
                    if item_id_str not in items_seen_in_this_line:
                        transaction_item_tuples.append((item_id_str, 1))
                        items_seen_in_this_line.add(item_id_str)
            except ValueError:
                if part and ':' not in part:  # Avoid warning for utility parts
                    print(f"Warning (parse_foodmart_transaction_line): Could not parse item: {part} in line: {line}")

        return transaction_item_tuples

    def load_foodmart_transactions_as_tuple(self):
        """
        Loads transactions from a FoodMart-formatted file.
        Each transaction will be a list of (item_id_str, quantity) tuples.
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
            for item_id_str, _ in tx_tuples:
                all_items.add(item_id_str)

        self.external_utility = {item: random.randint(20, 100) for item in all_items}
        print(f"\nGenerated utilities for {len(self.external_utility)} items. Sample: {list(self.external_utility.items())[:5]}")
        return self.external_utility