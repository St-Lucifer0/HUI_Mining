# hui_miner_algorithms.py

from hui_miner_helpers import HUIMinerHelpers
from config import get_min_utility_threshold


class HUIMiner:
    """
    Implements High-Utility Itemset Mining algorithms using pseudo-projection.
    This class uses helper methods from HUIMinerHelpers.
    """

    def __init__(self, external_utility=None, min_utility_threshold=None, transactions=None):
        """
        Initializes the HUIMiner.
        If external_utility is None, build it from transactions using the real utility values.
        If min_utility_threshold is None, use the global configuration value.
        """
        if external_utility is None:
            external_utility = {}
            if transactions is not None:
                for tx in transactions:
                    for item_id, _, utility in tx:
                        if item_id not in external_utility:
                            external_utility[item_id] = 0
                        external_utility[item_id] += utility
        
        if not isinstance(external_utility, dict):
            raise ValueError("external_utility must be a dictionary")
        
        # Use global config if threshold not provided
        if min_utility_threshold is None:
            min_utility_threshold = get_min_utility_threshold()
        
        if not isinstance(min_utility_threshold, (int, float)) or min_utility_threshold < 0:
            raise ValueError("min_utility_threshold must be a non-negative number.")
        
        self.external_utility = external_utility
        self.min_utility_threshold = min_utility_threshold
        self.helpers = HUIMinerHelpers()

    def mine_huis_pseudo_projection(self, initial_header_table, fp_tree_root_node=None):
        """
        Algorithm 5: Mines High-Utility Itemsets from an FP-Tree structure.

        Args:
            initial_header_table (dict): The main header table of the full FP-Tree.
            fp_tree_root_node (UtilityFPNode, optional): The root of the FP-Tree.
                                                         Not directly used by helpers if
                                                         initial_header_table is sufficient.

        Returns:
            set: A set of frozensets, where each frozenset is a High-Utility Itemset.
        """
        if not initial_header_table:
            return set()

        HUIs_found = set()
        # Remove artificial limit to allow proper threshold filtering
        itemsets_found = 0

        def get_item_total_utility_from_header(item, ht):  # Simplified utility sum from tree
            node = ht.get(item)
            item_total_util = 0
            while node:
                item_total_util += node.utility
                node = node.node_link
            return item_total_util

        items_to_process = sorted(
            initial_header_table.keys(),
            key=lambda x: get_item_total_utility_from_header(x, initial_header_table)
        )

        # Limit the number of items to process for faster execution
        items_to_process = items_to_process[:50]  # Process only top 50 items

        for item_i in items_to_process:
            # Remove artificial limit check
                
            current_HUI_candidate = frozenset({item_i})

            projected_db_for_i = self.helpers.build_projected_db_from_fp_tree_nodes(
                item_i, initial_header_table, self.external_utility
            )

            if not projected_db_for_i:
                continue

            total_utility_of_i = self.helpers.calculate_total_utility(projected_db_for_i)

            if total_utility_of_i >= self.min_utility_threshold:
                HUIs_found.add(current_HUI_candidate)
                itemsets_found += 1

            potential_utility_for_i = self.helpers.calculate_potential_utility(
                projected_db_for_i, self.external_utility
            )

            if potential_utility_for_i >= self.min_utility_threshold:
                conditional_results = self._mine_conditional_huis(current_HUI_candidate, projected_db_for_i)
                HUIs_found.update(conditional_results)
                itemsets_found += len(conditional_results)
        return HUIs_found

    def _mine_conditional_huis(self, prefix_itemset, current_projected_db, depth=0):
        """
        Algorithm 6 (Recursive Helper): Mines HUIs by extending 'prefix_itemset'
        using items from 'current_projected_db'.

        """
        # Add depth limiting to prevent infinite recursion
        if depth > 5:
            return set()
            
        local_HUIs_found = set()

        local_header_info = self.helpers.build_local_header_info(current_projected_db, self.external_utility)

        if not local_header_info:
            return local_HUIs_found

        sorted_local_items_to_try = sorted(local_header_info.keys(),
            key=lambda item_key: local_header_info[item_key].get('potential_utility_if_chosen', 0), reverse=True)

        # Limit items to try for faster execution
        sorted_local_items_to_try = sorted_local_items_to_try[:20]

        for item_j_to_add in sorted_local_items_to_try:
            # Remove artificial limit check
                
            current_HUI_candidate = prefix_itemset.union({item_j_to_add})

            projected_db_for_new_HUI = self.helpers.build_projected_db_from_existing_projected_db(item_j_to_add,
            current_projected_db, self.external_utility)

            if not projected_db_for_new_HUI:
                continue

            total_utility_of_current_HUI = self.helpers.calculate_total_utility(projected_db_for_new_HUI)

            if total_utility_of_current_HUI >= self.min_utility_threshold:
                local_HUIs_found.add(frozenset(current_HUI_candidate))

            potential_utility_for_current_HUI = self.helpers.calculate_potential_utility(projected_db_for_new_HUI,
                self.external_utility)

            if potential_utility_for_current_HUI >= self.min_utility_threshold:
                deeper_HUIs_found = self._mine_conditional_huis(
                    current_HUI_candidate, 
                    projected_db_for_new_HUI, 
                    depth + 1
                )
                local_HUIs_found.update(deeper_HUIs_found)
        return local_HUIs_found
