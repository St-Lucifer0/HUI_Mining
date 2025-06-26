from dummy_mpc import ImaginaryMPCFramework
from differential_privacy_utils import DifferentialPrivacyUtils

class PrivacyPreservingHUIMining:
    @staticmethod
    def privacy_preserving_hui_mining_algorithm8(
        transactions_list,    # List of plaintext transactions, e.g., [{'item': count}, ...]
        item_utils_dict,      # Plaintext item utilities, e.g., {'item': utility_value}
        minutil_threshold,    # Plaintext minimum utility threshold
        epsilon,              # Differential privacy budget (float)
        num_mpc_workers=3     # Number of virtual workers for MPC simulation
    ):
        """
        Implements the conceptual flow of Algorithm 8: Privacy-Preserving HUI Mining
        using a simulated MPC framework and differential privacy.

        Args:
            transactions_list (list): List of dictionaries representing transactions (e.g., [{'item': count}, ...]).
            item_utils_dict (dict): Dictionary of item utilities (e.g., {'item': utility_value}).
            minutil_threshold (float): Minimum utility threshold for HUIs.
            epsilon (float): Privacy budget for differential privacy (must be positive).
            num_mpc_workers (int): Number of virtual workers for MPC simulation.

        Returns:
            set: Set of frozensets representing differentially private high-utility itemsets.

        Raises:
            ValueError: If inputs are invalid or epsilon <= 0.
        """
        if not isinstance(transactions_list, list):
            raise ValueError("transactions_list must be a list")
        if not isinstance(item_utils_dict, dict):
            raise ValueError("item_utils_dict must be a dictionary")
        if not isinstance(minutil_threshold, (int, float)) or minutil_threshold < 0:
            raise ValueError("minutil_threshold must be a non-negative number")
        if not isinstance(epsilon, (int, float)) or epsilon <= 0:
            raise ValueError("epsilon must be a positive number")
        if not isinstance(num_mpc_workers, int) or num_mpc_workers <= 0:
            raise ValueError("num_mpc_workers must be a positive integer")

        print("\n===== Starting: Privacy-Preserving HUI Mining Simulation =====")

        # 1: Setup Secure Computation Environment
        mpc = ImaginaryMPCFramework(num_workers=num_mpc_workers)
        print("-" * 30)

        # 2: Encrypt/Share Data: Share transactions among workers
        shared_transaction_objects = []
        print("Step 2: Sharing transaction data securely...")
        for i, tx in enumerate(transactions_list):
            if not tx:
                continue
            if isinstance(tx[0], tuple):
                tx_dict = dict(tx)
            else:
                tx_dict = tx

            if not isinstance(tx_dict, dict):
                raise ValueError(f"Transaction {i} must be convertible to a dictionary, got {type(tx_dict)}")

            # calculate utility value
            tx_utility_val = sum(count * item_utils_dict.get(item, 0) for item, count in tx_dict.items())

            # prepare data to share
            tx_data_to_share = {"id": f"tx_{i}", "items": tx_dict, "transaction_utility_value": tx_utility_val}

            # share data using MPC
            shared_tx_obj = mpc.share_data(tx_data_to_share, f"transaction_{i}")
            shared_transaction_objects.append(shared_tx_obj)
            print(f"Processed transaction {i}: {tx_dict}")
            print("-" * 30)

        # 3: Secure TWU Computation
        print("Step 3: Securely Computing Item TWUs via MPC...")
        all_items_in_dataset = set()
        for tx in transactions_list:
            if not tx:
                continue
            if isinstance(tx[0], tuple):
                items = [item for item, _ in tx]
            else:
                items = list(tx.keys())

            all_items_in_dataset.update(items)
        all_items_in_dataset = list(all_items_in_dataset)

        encrypted_twu_obj = mpc.secure_twu_computation(shared_transaction_objects, all_items_in_dataset)
        print("-" * 30)


        # 4: Apply Differential Privacy# privacy_wrapper.py (Step 4 updated)
        print(f"Step 4: Applying Differential Privacy (Laplace Noise, epsilon={epsilon}) to TWU scores...")
        max_tx_utility_for_sensitivity = 0
        if transactions_list:
            max_tx_utility_for_sensitivity = max(sum(count * item_utils_dict.get(item, 0) for item, count in tx)
                                                 for tx in transactions_list if tx)
        print(f" Sensitivity for TWU (max transaction utility): {max_tx_utility_for_sensitivity}")

        shared_noisy_twus_obj = mpc.apply_noise_to_shared_data(encrypted_twu_obj, max_tx_utility_for_sensitivity)
        noisy_twus = mpc.reveal_data(shared_noisy_twus_obj)
        print(f" Noisy TWUs generated: {noisy_twus}")
        print("-" * 30)



        # 5: Secure FP-Tree Construction/Mining
        print("Step 5: Secure Pruning, Sorting, FP-Tree Construction, and HUI Mining using MPC...")
        shared_sorted_high_potential_items_obj = mpc.secure_prune_and_sort_items(shared_noisy_twus_obj,
                                                                                 minutil_threshold)
        encrypted_fp_tree_obj = mpc.secure_fp_tree_construction(
            shared_transaction_objects, shared_sorted_high_potential_items_obj, item_utils_dict
        )
        encrypted_final_HUI_list_obj = mpc.secure_hui_mining_on_tree(encrypted_fp_tree_obj, minutil_threshold)
        print("-" * 30)

        # 6: Result Revelation
        print("Step 6: Securely Revealing the final HUIs...")
        final_differentially_private_HUIs = mpc.reveal_data(encrypted_final_HUI_list_obj, "high_utility_itemsets")
        print("===== Algorithm 8 Simulation Finished =====")
        return final_differentially_private_HUIs