from preprocessor import construct_pruned_item_list
from fp_tree_builder import construct_huim_fp_tree
from fp_tree_updater import incremental_fp_tree_update
from hui_miner import HUIMiner
from privacy_wrapper import PrivacyPreservingHUIMining
from data_parser import DataProcessor
import os


def print_fp_tree(node, indent=0):
    """
    Recursively prints the FP-Tree

    Args:
         node: UtilityFPNode to print.
         indent: Indentation for tree visualization
    """

    print(" " * indent + str(node))
    for child in node.children.values():
        print_fp_tree(child, indent + 1)


def print_header_table(header_table):
    """
    Prints the header table and linked nodes

    Args:
        header_table: Dictionary mapping items to head of node link chain.
    """
    print("\nHeader Table:")
    for item, node in header_table.items():
        print(f"Item: {item}")
        current = node
        while current is not None:
            print(f" {current}")
            current = current.node_link


def main():
    # sample dataset
    # transaction_database = [
    # [("rice", 2), ("egg", 1), ("sugar", 1)],
    # [("rice", 1), ("sugar", 3)],
    # [("egg", 2), ("sugar", 2)],
    # [("rice", 3), ("egg", 1)]
    # ]
    # external_utility = {"rice": 5, "egg": 3, "sugar": 2}
    # min_util = 15  # TWU threshold for pruning
    # epsilon = 1.0

    # Initialize DataPreprocessor with FoodMart dataset path
    dataset_path = r"C:\Users\User\PycharmProjects\FP-GROWTH(Enhanced)_for_HUIs\foodmart_dataset_csv.csv"
    processor = DataProcessor(dataset_path)

    # load FoodMart Transactions
    transactions = processor.load_foodmart_transactions_as_tuple()
    if not transactions:
        print("Failed to load transactions...\nEXITING!!!")
        return

    external_utility = processor.get_dummy_foodmart_item_utilities()
    min_util = 50
    epsilon = 1.0

    try:
        # Prune low-utility items
        print("Pruning low-utility items...")
        sorted_items = construct_pruned_item_list(transactions, min_util, external_utility)
        print(f"High-Utility items (sorted by TWU): {sorted_items}")

        # Construct initial FP-Tree
        print("\nConstructing HUIM FP-Tree...")
        root, header_table = construct_huim_fp_tree(transactions, sorted_items, external_utility)

        # display initial results
        print("\nFP-Tree Structure:")
        print_fp_tree(root)
        print_header_table(header_table)

        # adding new transactions using foodmart dataset
        new_transactions_batch = [
            [(str(i), 1) for i in range(1, 4)],
            [(str(i), 1) for i in range(2, 5)]
        ]
        print("\nAdding new transactions...")
        root, header_table = incremental_fp_tree_update(root, header_table, new_transactions_batch,
                                                        external_utility, min_util, sorted_items)

        # Display updated results
        print("\nUpdated FP-Tree Structure:")
        print_fp_tree(root)
        print_header_table(header_table)

        # Mine high-utility itemsets
        print("\nMining High-Utility Itemsets...")
        miner = HUIMiner(external_utility, min_util)
        high_high_utility_itemsets = miner.mine_huis_pseudo_projection(header_table, root)
        print(f"High-Utility Itemsets: {high_high_utility_itemsets}")

        # ensuring data privacy
        print(f"\nStarting Privacy-Preserving HUI Mining for Device at 'time' on 'day'...")
        # use privacy preserving hui mining algorithm for this device's data
        high_utility_itemsets = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
            transactions_list=transactions,
            item_utils_dict=external_utility,
            minutil_threshold=min_util,
            epsilon=epsilon,
            num_mpc_workers=3
        )
        print(f"\nFinal High-Utility Itemsets for this device: {high_utility_itemsets}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
