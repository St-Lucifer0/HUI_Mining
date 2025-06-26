# hui_miner_helpers.py
from fp_node import UtilityFPNode


class HUIMinerHelpers:
    """
    A collection of static helper methods for High-Utility Itemset Mining algorithms.
    These helpers primarily deal with constructing and analyzing projected databases.
    """

    @staticmethod
    def build_projected_db_from_fp_tree_nodes(item_to_project, initial_header_table, external_utility):
        """
        Builds the first projected database for a single 'item_to_project'.
        It traces paths upwards from all nodes of 'item_to_project' in the main FP-Tree.
        Output tuple: (frozenset_prefix_items, utility_of_item_to_project_in_this_node, node_count)

        Args:
            item_to_project: The item to project the database on.
            initial_header_table (dict): Mapping of items to their first UtilityFPNode.
            external_utility (dict): Mapping of items to their utility values.

        Returns:
            list: List of tuples(frozenset_prefix_items, utility, count).
        """
        projected_db = []
        current_path_node = initial_header_table.get(item_to_project)

        if not current_path_node or not isinstance(current_path_node, UtilityFPNode):
            return []

        while current_path_node is not None:
            if not isinstance(current_path_node, UtilityFPNode):
                break
            prefix_path_items = []
            utility_of_item_in_this_node = current_path_node.utility
            path_count_of_this_node = current_path_node.count

            temp_parent_node = current_path_node.parent_node
            while temp_parent_node is not None and temp_parent_node.item_name is not None:
                prefix_path_items.append(temp_parent_node.item_name)
                temp_parent_node = temp_parent_node.parent_node

            projected_db.append(
                (frozenset(reversed(prefix_path_items)), utility_of_item_in_this_node, path_count_of_this_node)
            )
            current_path_node = current_path_node.node_link
        return projected_db

    @staticmethod
    def build_projected_db_from_existing_projected_db(item_j_to_add, source_projected_db, external_utility):
        """
        Builds a new projected database for 'Prefix U {item_j_to_add}' using a 'source_projected_db'.
        Output tuple: (frozenset_new_prefix_items, combined_utility_of_Prefix_and_item_j, path_count)
        """
        newly_projected_db = []
        for original_prefix_items_set, utility_of_prefix_in_path, path_count in source_projected_db:
            if item_j_to_add in original_prefix_items_set:
                new_prefix_for_j = original_prefix_items_set - {item_j_to_add}
                utility_of_item_j_in_this_path_segment = external_utility.get(item_j_to_add, 0) * path_count
                combined_utility_for_new_db_entry = utility_of_item_j_in_this_path_segment + utility_of_prefix_in_path

                newly_projected_db.append(
                    (frozenset(new_prefix_for_j), combined_utility_for_new_db_entry, path_count)
                )
        return newly_projected_db

    @staticmethod
    def calculate_total_utility(projected_db_for_itemset):
        """
        Calculates the total utility of an itemset given its projected database.
        Assumes projected_db_for_itemset tuples: (prefix, util_of_itemset_for_path, count)
        """
        total_utility = 0
        for _prefix_items, utility_of_itemset_in_path, _path_count in projected_db_for_itemset:
            total_utility += utility_of_itemset_in_path
        return total_utility

    @staticmethod
    def calculate_potential_utility(projected_db, item_utils):
        """
        Calculates the potential utility (upper bound) from a projected database.
        Assumes projected_db tuples: (prefix, util_of_itemset_projected_on, count)
        """
        total_potential_utility = 0
        for prefix_items_set, utility_of_itemset_projected_on, path_count in projected_db:
            current_path_potential = utility_of_itemset_projected_on
            for item_in_prefix in prefix_items_set:
                current_path_potential += item_utils.get(item_in_prefix, 0) * path_count
            total_potential_utility += current_path_potential
        return total_potential_utility

    @staticmethod
    def build_local_header_info(projected_db_for_prefix_p, item_utils):
        """
        Analyzes a projected_db (for a Prefix P) to find unique items 'j' in its prefixes
        and estimates their relevant utilities if P U {j} is formed.
        Output: {item_j: {'total_utility_as_next': val, 'potential_utility_if_chosen': val, 'count_in_paths': val}}
        """
        local_header = {}
        for further_prefix_items_set, utility_of_p_in_that_path, path_count in projected_db_for_prefix_p:
            for item_j_in_further_prefix in further_prefix_items_set:
                if item_j_in_further_prefix not in local_header:
                    local_header[item_j_in_further_prefix] = {
                        'total_utility_as_next': 0,
                        'potential_utility_if_chosen': 0,
                        'count_in_paths': 0
                    }

                utility_of_j_segment = item_utils.get(item_j_in_further_prefix, 0) * path_count
                local_header[item_j_in_further_prefix]['total_utility_as_next'] += (
                    utility_of_j_segment + utility_of_p_in_that_path
                )
                local_header[item_j_in_further_prefix]['count_in_paths'] += path_count

                current_path_potential_for_j = utility_of_j_segment + utility_of_p_in_that_path
                for other_item in further_prefix_items_set:
                    if other_item != item_j_in_further_prefix:
                        current_path_potential_for_j += item_utils.get(other_item, 0) * path_count
                local_header[item_j_in_further_prefix]['potential_utility_if_chosen'] += current_path_potential_for_j
        return local_header
