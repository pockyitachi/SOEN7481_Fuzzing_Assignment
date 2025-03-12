import json
import csv
import xml.etree.ElementTree as ET
from jsonschema import validate, ValidationError


class AdvancedJSONProcessor:
    """Processes, validates, and extracts data from complex JSON structures."""

    def __init__(self, json_data):
        """Accepts JSON as a string or dictionary."""
        self.data = None
        self.load_json(json_data)

    def load_json(self, json_data):
        """Loads JSON from a string or dictionary."""
        try:
            if isinstance(json_data, str):
                self.data = json.loads(json_data)
            elif isinstance(json_data, dict):
                self.data = json_data
            else:
                raise ValueError("Invalid JSON input format.")
            return "Valid JSON"
        except json.JSONDecodeError as e:
            return f"JSON Error: {e}"

    def validate_schema(self, schema):
        """Validates JSON against a given schema."""
        if not self.data:
            return "Error: JSON not loaded"
        try:
            validate(instance=self.data, schema=schema)
            return "JSON matches schema"
        except ValidationError as e:
            return f"Schema Validation Error: {e.message}"

    def search_key(self, key):
        """Recursively searches for a key in nested JSON."""
        if not self.data:
            return "Error: JSON not loaded"
        results = []

        def recursive_search(data, key):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == key:
                        results.append(v)
                    recursive_search(v, key)
            elif isinstance(data, list):
                for item in data:
                    recursive_search(item, key)

        recursive_search(self.data, key)
        return results if results else "Key not found"

    def convert_to_csv(self, output_file="output.csv"):
        """Converts JSON into a CSV file if it's a list of dictionaries."""
        if not self.data:
            return "Error: JSON not loaded"
        if not isinstance(self.data, list) or not all(isinstance(i, dict) for i in self.data):
            return "Error: JSON is not a list of dictionaries"

        keys = set()
        for item in self.data:
            keys.update(item.keys())

        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(keys))
            writer.writeheader()
            for item in self.data:
                writer.writerow(item)
        return f"JSON converted to CSV: {output_file}"

    def convert_to_xml(self, root_element="root"):
        """Converts JSON into XML format."""
        if not self.data:
            return "Error: JSON not loaded"

        def build_xml_element(data, parent):
            if isinstance(data, dict):
                for key, value in data.items():
                    sub_elem = ET.SubElement(parent, key)
                    build_xml_element(value, sub_elem)
            elif isinstance(data, list):
                for item in data:
                    item_elem = ET.SubElement(parent, "item")
                    build_xml_element(item, item_elem)
            else:
                parent.text = str(data)

        root = ET.Element(root_element)
        build_xml_element(self.data, root)
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

    def extract_numbers(self):
        """Finds all numbers in the JSON data."""
        if not self.data:
            return "Error: JSON not loaded"

        numbers = []

        def recursive_search(data):
            if isinstance(data, dict):
                for v in data.values():
                    recursive_search(v)
            elif isinstance(data, list):
                for item in data:
                    recursive_search(item)
            elif isinstance(data, (int, float)):
                numbers.append(data)

        recursive_search(self.data)
        return numbers if numbers else "No numbers found"


# Example Usage:
if __name__ == "__main__":
    # Example JSON data
    json_data = {
        "user": {
            "name": "Alice",
            "age": 25,
            "address": {"city": "New York", "zip": 10001}
        },
        "orders": [
            {"id": 1, "amount": 250.50},
            {"id": 2, "amount": 99.99}
        ]
    }

    processor = AdvancedJSONProcessor(json_data)
    print(processor.search_key("name"))  # Example function call
    print(processor.extract_numbers())  # Extract numbers
    print(processor.convert_to_xml())  # Convert to XML
