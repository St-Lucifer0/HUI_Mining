class UtilityFPNode:

    # Create an initial function, defining the necessary variables
    def __init__(self, item_name, count, parent_node):
        """
        Defining variables for an fp-node

        """

        # Raise Value Error if count is negative
        if not isinstance(count, int) or count < 0:
            raise ValueError("Count must be a non-negative integer.")
        if parent_node is not None and not isinstance(parent_node, UtilityFPNode):
            raise ValueError("Parent node must be a Utility FP-Node or none.")
        self.item_name = item_name
        self.count = count
        self.parent_node = parent_node
        self.children = {}
        self.node_link = None
        self.utility = 0

    # define a method to add child
    def add_child(self, child_node):
        self.children[child_node.item_name] = child_node

    # define a method to get child
    def get_child(self, item_name):
        return self.children.get(item_name)

    # define a method for easy printing
    def __repr__(self):
        return f"Node({self.item_name}, Cnt: {self.count}, Util: {self.utility})"
