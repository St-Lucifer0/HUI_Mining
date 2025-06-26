import random
from typing import Dict, List, Any

class ImaginaryMPCFramework:
    def __init__(self, num_workers=3, epsilon=1.0):
        """
        Initializes the MPC framework with virtual workers and differential privacy parameter.

        Args:
            num_workers (int): Number of virtual workers.
            epsilon (float): Privacy budget for differential privacy (smaller = more privacy).
        """
        if not isinstance(num_workers, int) or num_workers <= 0:
            raise ValueError("num_workers must be a positive integer")
        if not isinstance(epsilon, (int, float)) or epsilon <= 0:
            raise ValueError("epsilon must be a positive number")
        self.num_workers = num_workers
        self.workers = [f"worker_{i+1}" for i in range(num_workers)]
        self.epsilon = epsilon
        print(f"MPC_SIM: Initialized with {self.num_workers} virtual workers, epsilon={self.epsilon}: {self.workers}")

    def _generate_noisy_twu(self, twu_value: float, sensitivity: float) -> float:
        """Generates noisy TWU using the add_laplace_noise function."""
        from differential_privacy_utils import DifferentialPrivacyUtils  # Import here to avoid circular dependency
        noisy_dict = DifferentialPrivacyUtils.add_laplace_noise({key: twu_value for key in ["dummy"]}, sensitivity, self.epsilon)
        return next(iter(noisy_dict.values()))  # Return the noisy value

    def share_data(self, data_to_share: Any, data_description: str = "") -> Dict[str, Any]:
        """Simulates secret sharing data among workers."""
        if not data_to_share:
            raise ValueError("data_to_share cannot be empty")
        if data_description:
            print(f"MPC_SIM: Secret sharing '{data_description}' among {self.num_workers} workers.")
        else:
            print(f"MPC_SIM: Secret sharing data among {self.num_workers} workers.")
        return {"shared_data_content": data_to_share, "status": "shared", "shared_by_MPC": True}

    def secure_twu_computation(self, shared_transaction_pointers_list: List, all_items_list: List[str]) -> Dict[str, Any]:
        """Simulates secure computation of Transaction-Weighted Utility."""
        if not isinstance(shared_transaction_pointers_list, list) or not isinstance(all_items_list, list):
            raise ValueError("Invalid input types for transactions or items")
        print(f"MPC_SIM: Performing secure TWU computation for {len(all_items_list)} items "
              f"using {len(shared_transaction_pointers_list)} shared transactions.")
        twu_dict = {item: len(shared_transaction_pointers_list) * 5 for item in all_items_list}  # Mock TWU
        encrypted_twu_dict = {item: "encrypted_twu_for_" + item for item in all_items_list}
        return {"encrypted_data_content": encrypted_twu_dict, "status": "encrypted", "description": "item_TWUs",
                "plaintext_twu": twu_dict}

    def apply_noise_to_shared_data(self, shared_encrypted_twus: Dict[str, Any], sensitivity: float) -> Dict[str, Any]:
        """Simulates applying noise to TWUs with differential privacy."""
        print(f"MPC_SIM: Applying noise to TWUs within MPC with sensitivity {sensitivity}.")
        plaintext_twus = shared_encrypted_twus.get("plaintext_twu", {})
        noisy_twus = {item: self._generate_noisy_twu(twu, sensitivity) for item, twu in plaintext_twus.items()}
        return {"shared_data_content": noisy_twus, "status": "shared_noisy", "description": "noisy_item_TWUs"}

    def secure_prune_and_sort_items(self, shared_noisy_twus_obj: Dict[str, Any], minutil_threshold: float) -> Dict[str, Any]:
        """Simulates secure pruning and sorting based on noisy TWUs."""
        if not isinstance(minutil_threshold, (int, float)) or minutil_threshold < 0:
            raise ValueError("minutil_threshold must be non-negative")
        print(f"MPC_SIM: Performing secure pruning (threshold: {minutil_threshold}) and sorting of items.")
        noisy_twus_dict = shared_noisy_twus_obj.get("shared_data_content", {})
        high_potential_items = {item for item, noisy_twu in noisy_twus_dict.items() if noisy_twu >= minutil_threshold}
        sorted_list = sorted(list(high_potential_items), key=lambda item: noisy_twus_dict.get(item, float('-inf')),
                             reverse=True)
        print(f"MPC_SIM: Pruned and sorted items (count: {len(sorted_list)}): {sorted_list[:5]}...")
        return {"shared_data_content": sorted_list, "status": "shared_sorted",
                "description": "sorted_high_potential_items"}

    def secure_fp_tree_construction(self, shared_transaction_pointers_list: List, shared_sorted_items_obj: Dict[str, Any],
                                   item_utils_public: Dict[str, float]) -> Dict[str, Any]:
        """Simulates secure construction of an FP-Tree."""
        sorted_items_list = shared_sorted_items_obj.get("shared_data_content", [])
        if not isinstance(item_utils_public, dict):
            raise ValueError("item_utils_public must be a dictionary")
        print(f"MPC_SIM: Performing secure FP-Tree construction using {len(shared_transaction_pointers_list)} "
              f"shared transactions and {len(sorted_items_list)} shared sorted items.")
        return {
            "encrypted_fp_root": "SECRET_ENCRYPTED_FP_ROOT_POINTER",
            "encrypted_header_table": {item: f"SECRET_ENCR_HEADER_NODE_{item}" for item in sorted_items_list},
            "status": "encrypted_fp_tree",
            "description": "FP_Tree_structure"
        }

    def secure_hui_mining_on_tree(self, encrypted_fp_tree_data_obj: Dict[str, Any], minutil_threshold: float) -> Dict[str, Any]:
        """Simulates secure HUI mining on the encrypted FP-Tree."""
        if not isinstance(minutil_threshold, (int, float)) or minutil_threshold < 0:
            raise ValueError("minutil_threshold must be non-negative")
        print(f"MPC_SIM: Performing secure HUI mining on the encrypted FP-Tree (minutil: {minutil_threshold}).")
        items = list(encrypted_fp_tree_data_obj.get("encrypted_header_table", {}).keys())
        mock_encrypted_huis = [f"ENCRYPTED_FROZENSET_{'_'.join(items[:i+1])}" for i in range(min(2, len(items)))]
        return {"encrypted_data_list_content": mock_encrypted_huis, "status": "encrypted_list",
                "description": "high_utility_itemsets"}

    def reveal_data(self, shared_or_encrypted_data_obj: Dict[str, Any], data_description: str = "") -> Any:
        """Simulates securely revealing the final plaintext result."""
        desc = data_description if data_description else shared_or_encrypted_data_obj.get("description", "data")
        print(f"MPC_SIM: Securely revealing '{desc}'.")
        content = shared_or_encrypted_data_obj.get("shared_data_content",
                                                  shared_or_encrypted_data_obj.get("encrypted_data_content",
                                                                                  shared_or_encrypted_data_obj.get(
                                                                                      "encrypted_data_list_content")))

        if content is None:
            return f"REVEALED_OPAQUE_DATA_FOR_{desc}"

        if desc == "high_utility_itemsets" and isinstance(content, list):
            revealed_huis = set()
            for enc_hui in content:
                items = enc_hui.replace("ENCRYPTED_FROZENSET_", "").split("_")
                if items:
                    revealed_huis.add(frozenset(items))
            return revealed_huis

        return content