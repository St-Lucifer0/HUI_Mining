# hui_miner_algorithms.py

from hui_miner_helpers import HUIMinerHelpers


class HUIMiner:
    """
    Implements High-Utility Itemset Mining algorithms using pseudo-projection.
    This class uses helper methods from HUIMinerHelpers.
    """

    def __init__(self, external_utility, min_utility_threshold):
        """
        Initializes the HUIMiner.

        Args:
            external_utility (dict): Global item utilities {item_name: utility_value}.
            min_utility_threshold (float or int): The minimum utility for an HUI.
        """
        # Input Validation
        if not isinstance(external_utility, dict):
            raise ValueError("external_utility must be a dictionary")
        if not isinstance(min_utility_threshold, (int, float)) or min_utility_threshold < 0:
            raise ValueError("min_utility_threshold must be a non-negative nuber.")

        self.external_utility = external_utility
        self.min_utility_threshold = min_utility_threshold
        self.helpers = HUIMinerHelpers()  # Instantiate or just use static methods directly

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

        for item_i in items_to_process:
            current_HUI_candidate = frozenset({item_i})

            projected_db_for_i = self.helpers.build_projected_db_from_fp_tree_nodes(
                item_i, initial_header_table, self.external_utility
            )

            if not projected_db_for_i:
                continue

            total_utility_of_i = self.helpers.calculate_total_utility(projected_db_for_i)

            if total_utility_of_i >= self.min_utility_threshold:
                HUIs_found.add(current_HUI_candidate)

            potential_utility_for_i = self.helpers.calculate_potential_utility(
                projected_db_for_i, self.external_utility
            )

            if potential_utility_for_i >= self.min_utility_threshold:
                conditional_results = self._mine_conditional_huis(current_HUI_candidate, projected_db_for_i)
                HUIs_found.update(conditional_results)
        return HUIs_found

    def _mine_conditional_huis(self, prefix_itemset, current_projected_db):
        """
        Algorithm 6 (Recursive Helper): Mines HUIs by extending 'prefix_itemset'
        using items from 'current_projected_db'.

        """
        local_HUIs_found = set()

        local_header_info = self.helpers.build_local_header_info(current_projected_db, self.external_utility)

        if not local_header_info:
            return local_HUIs_found

        sorted_local_items_to_try = sorted(local_header_info.keys(),
            key=lambda item_key: local_header_info[item_key].get('potential_utility_if_chosen', 0), reverse=True)

        for item_j_to_add in sorted_local_items_to_try:
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
                deeper_HUIs_found = self._mine_conditional_huis(current_HUI_candidate, projected_db_for_new_HUI)
                local_HUIs_found.update(deeper_HUIs_found)
        return local_HUIs_found
