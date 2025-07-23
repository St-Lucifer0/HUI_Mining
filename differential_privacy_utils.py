import numpy as np


class DifferentialPrivacyUtils:
    @staticmethod
    def add_laplace_noise(value, sensitivity, epsilon):
        """
        Adds Laplace noise to a single value for differential privacy.

        Args:
            value (float): The value to add noise to.
            sensitivity (float): The sensitivity (maximum change in output due to one record).
            epsilon (float): Privacy budget (smaller values increase privacy, must be positive).

        Returns:
            float: The value with added noise.

        Raises:
            ValueError: If epsilon <= 0 or sensitivity < 0.
        """
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        if sensitivity < 0:
            raise ValueError("sensitivity must be non-negative")

        scale = sensitivity / epsilon
        noise = np.random.laplace(loc=0, scale=scale)
        return value + noise

    @staticmethod
    def add_laplace_noise_to_dict(data_dict, sensitivity, epsilon):
        """
        Adds Laplace noise to each value in the dictionary for differential privacy.

        Args:
            data_dict (dict): Dictionary containing numeric values to add noise to.
            sensitivity (float): The sensitivity (maximum change in output due to one record).
            epsilon (float): Privacy budget (smaller values increase privacy, must be positive).

        Returns:
            dict: A new dictionary with noisy values.

        Raises:
            ValueError: If epsilon <= 0, data_dict is not a dictionary, or values are non-numeric.
        """
        if not isinstance(data_dict, dict):
            raise ValueError("data_dict must be a dictionary")
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        if sensitivity < 0:
            raise ValueError("sensitivity must be non-negative")

        # Validate that all values are numeric
        for value in data_dict.values():
            if not isinstance(value, (int, float)):
                raise ValueError("All values in data_dict must be numeric")

        scale = sensitivity / epsilon
        noisy_dict = {}
        for key, value in data_dict.items():
            noise = np.random.laplace(loc=0, scale=scale)
            noisy_dict[key] = value + noise

        return noisy_dict