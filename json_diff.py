
"""
json_diff.py
------------
Recursively compares two JSON files (before/after) and reports:
  - Added fields/items
  - Removed fields/items
  - Changed fields (old -> new)

"""

import json
import sys


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def compare(old, new, path="", key_field="name"):
    """
    Recursively compares `old` vs `new`.
    Returns a dict with 'added', 'removed', 'changed' lists.
    Each entry is a tuple: (path, old_value, new_value) for changed,
    or (path, value) for added/removed.
    """
    added, removed, changed = [], [], []

    if isinstance(old, dict) and isinstance(new, dict):
        all_keys = set(old.keys()) | set(new.keys())
        for key in sorted(all_keys, key=str):
            current_path = f"{path}.{key}" if path else key

            if key not in new:
                removed.append((current_path, old[key]))
            elif key not in old:
                added.append((current_path, new[key]))
            else:
                sub = compare(old[key], new[key], current_path, key_field)
                added.extend(sub["added"])
                removed.extend(sub["removed"])
                changed.extend(sub["changed"])

    elif isinstance(old, list) and isinstance(new, list):
       
        if all(isinstance(i, dict) and key_field in i for i in old + new if i):
            old_map = {item[key_field]: item for item in old}
            new_map = {item[key_field]: item for item in new}
            all_ids = set(old_map.keys()) | set(new_map.keys())

            for item_id in sorted(all_ids, key=str):
                current_path = f"{path}[{key_field}={item_id}]"
                if item_id not in new_map:
                    removed.append((current_path, old_map[item_id]))
                elif item_id not in old_map:
                    added.append((current_path, new_map[item_id]))
                else:
                    sub = compare(old_map[item_id], new_map[item_id],
                                  current_path, key_field)
                    added.extend(sub["added"])
                    removed.extend(sub["removed"])
                    changed.extend(sub["changed"])
        else:
  
            max_len = max(len(old), len(new))
            for i in range(max_len):
                current_path = f"{path}[{i}]"
                if i >= len(old):
                    added.append((current_path, new[i]))
                elif i >= len(new):
                    removed.append((current_path, old[i]))
                else:
                    sub = compare(old[i], new[i], current_path, key_field)
                    added.extend(sub["added"])
                    removed.extend(sub["removed"])
                    changed.extend(sub["changed"])

    else:
        if old != new:
            changed.append((path, old, new))

    return {"added": added, "removed": removed, "changed": changed}


def print_report(result):
    def fmt(items, kind):
        print(f"\n{kind}")
        print("-" * 30)
        if not items:
            print("(none)")
        for item in items:
            if kind == "Changed":
                path, old_val, new_val = item
                print(f"{path}: {old_val!r} -> {new_val!r}")
            else:
                path, val = item
                print(f"{path}: {val!r}")

    fmt(result["added"], "Added")
    fmt(result["removed"], "Removed")
    fmt(result["changed"], "Changed")


def main():
    before_path = sys.argv[1] if len(sys.argv) > 1 else "before.json"
    after_path = sys.argv[2] if len(sys.argv) > 2 else "after.json"

    before = load_json(before_path)
    after = load_json(after_path)

    result = compare(before, after)
    print_report(result)


    with open("diff_report.json", "w") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    main()
