import json

# Define file paths
items_file_path = 'items.json'
batch_processed_file_path = 'batch_processed.json'
processed_output_path = 'processed_items.json'
unprocessed_output_path = 'unprocessed_items.json'

# Create a mapping of ID to description from batch_processed.json
id_to_description = {}
try:
    with open(batch_processed_file_path, 'r') as f:
        batch_data = json.load(f)
        for item in batch_data:
            if item.get('description'):  # Check for non-empty description
                id_to_description[item['id']] = item['description']
except FileNotFoundError:
    print(
        f"Warning: {batch_processed_file_path} not found. Starting with empty description mapping."
    )
except json.JSONDecodeError:
    print(f"Error: Invalid JSON in {batch_processed_file_path}")
    exit(1)

# Process items.json
processed_items = []
unprocessed_items = []
try:
    with open(items_file_path, 'r') as f:
        all_items = json.load(f)

    for item in all_items:
        item_id = item.get('id')
        if item_id in id_to_description:
            # Create a copy of the item and add the description from batch_processed
            processed_item = item.copy()
            processed_item['description'] = id_to_description[item_id]
            processed_items.append(processed_item)
        else:
            unprocessed_items.append(item)

except FileNotFoundError:
    print(f"Error: {items_file_path} not found.")
    exit(1)
except json.JSONDecodeError:
    print(f"Error: Invalid JSON in {items_file_path}")
    exit(1)

# Write processed items
try:
    with open(processed_output_path, 'w') as f:
        json.dump(processed_items, f, indent=4)
    print(
        f"Created {processed_output_path} with {len(processed_items)} processed items"
    )
except IOError:
    print(f"Error writing to {processed_output_path}")
    exit(1)

# Write unprocessed items
try:
    with open(unprocessed_output_path, 'w') as f:
        json.dump(unprocessed_items, f, indent=4)
    print(
        f"Created {unprocessed_output_path} with {len(unprocessed_items)} unprocessed items"
    )
except IOError:
    print(f"Error writing to {unprocessed_output_path}")
    exit(1)

# Print summary
print("\nSummary:")
print(f"Total items in {items_file_path}: {len(all_items)}")
print(f"Processed items with descriptions: {len(processed_items)}")
print(f"Unprocessed items: {len(unprocessed_items)}")
print(f"Descriptions available in batch_processed: {len(id_to_description)}")
