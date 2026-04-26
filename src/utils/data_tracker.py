import json
import os

class DataTracker:
    def __init__(self, data_file='previous_data.json', unique_key='id'):
        """
        Initialize the data tracker.

        Args:
            data_file (str): File to store previous data.
            unique_key (str): Key to identify unique items (e.g., 'id', 'name').
        """
        self.data_file = data_file
        self.unique_key = unique_key
        self.previous_data = self.load_previous_data()

    def load_previous_data(self):
        """
        Load previous data from file.

        Returns:
            set: Set of unique keys from previous data.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {item.get(self.unique_key) for item in data if item.get(self.unique_key)}
                    else:
                        return set()
            except (json.JSONDecodeError, KeyError):
                return set()
        return set()

    def save_data(self, data):
        """
        Save current data to file.

        Args:
            data (list or dict): Data to save.
        """
        # Ensure directory exists
        dirname = os.path.dirname(self.data_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
            
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_new_items(self, current_data):
        """
        Get new items not in previous data.

        Args:
            current_data (list): Current list of items.

        Returns:
            list: List of new items.
        """
        if not isinstance(current_data, list):
            return []

        current_keys = {item.get(self.unique_key) for item in current_data if item.get(self.unique_key)}
        new_keys = current_keys - self.previous_data
        new_items = [item for item in current_data if item.get(self.unique_key) in new_keys]

        # Update previous data
        self.previous_data = current_keys
        self.save_data(current_data)

        return new_items