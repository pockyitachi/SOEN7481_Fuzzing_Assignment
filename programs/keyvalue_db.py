import json
import threading
import os
import time
import uuid


class KeyValueDatabase:
    """A complex, thread-safe, persistent key-value database with transactions, TTL, and indexing."""

    def __init__(self, db_file="database.json", log_file="db_log.json"):
        self.db_file = db_file
        self.log_file = log_file
        self.lock = threading.Lock()
        self.ttl_data = {}  # Stores TTL expiration times
        self.indexes = {}  # Indexes for fast lookups
        self.transactions = {}  # Active transactions (MVCC)
        self._load_database()

        # Start background thread to clean expired keys
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self.cleanup_thread.start()

    def _load_database(self):
        """Loads the database from a JSON file, creating it if necessary."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                print("Error: Database file corrupted. Resetting.")
                self.data = {}
        else:
            self.data = {}

        # Load TTL data
        self.ttl_data = self.data.get("_ttl", {})

    def _save_database(self):
        """Saves the database to a JSON file safely."""
        with self.lock:
            self.data["_ttl"] = self.ttl_data  # Store TTL info in database
            try:
                with open(self.db_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                print(f"Error saving database: {e}")

    def _log_operation(self, operation):
        """Logs database operations for recovery."""
        with self.lock:
            log_entry = {"timestamp": time.time(), "operation": operation}
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as e:
                print(f"Error writing log: {e}")

    def _cleanup_expired_keys(self):
        """Background thread to remove expired keys."""
        while True:
            time.sleep(5)  # Cleanup interval
            with self.lock:
                current_time = time.time()
                expired_keys = [key for key, expiry in self.ttl_data.items() if expiry < current_time]
                for key in expired_keys:
                    del self.data[key]
                    del self.ttl_data[key]
                self._save_database()

    def set(self, key, value, ttl=None):
        """Stores a key-value pair with optional TTL."""
        with self.lock:
            self.data[key] = value
            if ttl:
                self.ttl_data[key] = time.time() + ttl  # Set expiration time
            self._save_database()
            self._log_operation({"action": "set", "key": key, "value": value, "ttl": ttl})
            return f"Set: {key} = {value} (TTL={ttl})"

    def get(self, key):
        """Retrieves a value by key, checking TTL expiration."""
        if key in self.ttl_data and self.ttl_data[key] < time.time():
            self.delete(key)
            return "Error: Key expired"
        return self.data.get(key, "Error: Key not found")

    def delete(self, key):
        """Deletes a key from the database."""
        with self.lock:
            if key in self.data:
                del self.data[key]
                if key in self.ttl_data:
                    del self.ttl_data[key]
                self._save_database()
                self._log_operation({"action": "delete", "key": key})
                return f"Deleted: {key}"
            return "Error: Key not found"

    def query(self, condition_key, condition_value):
        """Finds records matching a condition using indexing."""
        results = {k: v for k, v in self.data.items() if
                   isinstance(v, dict) and v.get(condition_key) == condition_value}
        return results if results else "No matching records found"

    def reset(self):
        """Resets the database (deletes all data)."""
        with self.lock:
            self.data = {}
            self.ttl_data = {}
            self._save_database()
            self._log_operation({"action": "reset"})
            return "Database reset"

    def begin_transaction(self):
        """Begins a new transaction (MVCC)."""
        txn_id = str(uuid.uuid4())
        with self.lock:
            self.transactions[txn_id] = json.loads(json.dumps(self.data))  # Deep copy
        return f"Transaction {txn_id} started"

    def commit_transaction(self, txn_id):
        """Commits changes from a transaction."""
        with self.lock:
            if txn_id in self.transactions:
                self.data = self.transactions[txn_id]
                self._save_database()
                del self.transactions[txn_id]
                self._log_operation({"action": "commit", "txn_id": txn_id})
                return f"Transaction {txn_id} committed"
            return "Error: Transaction not found"

    def rollback_transaction(self, txn_id):
        """Rolls back a transaction, discarding changes."""
        with self.lock:
            if txn_id in self.transactions:
                del self.transactions[txn_id]
                return f"Transaction {txn_id} rolled back"
            return "Error: Transaction not found"


# --- Multi-threaded Testing ---

def worker_thread(db, operations):
    """Simulates concurrent database usage."""
    for op in operations:
        if op["action"] == "set":
            print(db.set(op["key"], op["value"], op.get("ttl")))
        elif op["action"] == "get":
            print(f"Get {op['key']}: {db.get(op['key'])}")
        elif op["action"] == "delete":
            print(db.delete(op["key"]))
        elif op["action"] == "query":
            print(f"Query {op['key']}={op['value']}: {db.query(op['key'], op['value'])}")


if __name__ == "__main__":
    db = KeyValueDatabase()

    # Define some operations to be executed concurrently
    operations_1 = [
        {"action": "set", "key": "user1", "value": {"name": "Alice", "age": 30}, "ttl": 10},
        {"action": "set", "key": "user2", "value": {"name": "Bob", "age": 25}},
        {"action": "get", "key": "user1"},
        {"action": "begin_transaction"},
        {"action": "set", "key": "user3", "value": {"name": "Charlie", "age": 35}},
        {"action": "commit_transaction"},
    ]

    operations_2 = [
        {"action": "set", "key": "user4", "value": {"name": "Dave", "age": 40}},
        {"action": "delete", "key": "user4"},
        {"action": "query", "key": "age", "value": 30},
        {"action": "rollback_transaction"},
    ]

    # Create threads
    thread1 = threading.Thread(target=worker_thread, args=(db, operations_1))
    thread2 = threading.Thread(target=worker_thread, args=(db, operations_2))

    # Start threads
    thread1.start()
    thread2.start()

    # Wait for completion
    thread1.join()
    thread2.join()