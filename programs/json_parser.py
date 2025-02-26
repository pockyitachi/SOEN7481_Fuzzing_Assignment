import json


def parse_json(json_str):
    try:
        data = json.loads(json_str)
        return f"Valid JSON: {data}"
    except json.JSONDecodeError as e:
        return f"JSON Error: {e}"


if __name__ == "__main__":
    json_str = input("Enter JSON data: ")
    print(parse_json(json_str))
