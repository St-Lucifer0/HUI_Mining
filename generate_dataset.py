import random
import csv

def generate_foodmart_dataset(num_transactions=1500, output_file="generated_foodmart_dataset.csv"):
    """
    Generate a FoodMart-formatted dataset with the specified number of transactions.
    
    New Format: item_id1 item_id2 ... item_idN:utility1 utility2 ... utilityN:quantity1 quantity2 ... quantityN
    Each transaction line has the same number of items, per-item utilities, and quantities.
    Some itemsets are repeated across multiple transactions.
    """
    
    # Define item categories and their possible items
    item_categories = {
        'food': ['bread', 'milk', 'eggs', 'cheese', 'butter', 'yogurt', 'cereal', 'pasta', 'rice', 'beans'],
        'beverages': ['coffee', 'tea', 'juice', 'soda', 'water', 'beer', 'wine', 'milk_drink', 'energy_drink'],
        'snacks': ['chips', 'cookies', 'crackers', 'nuts', 'candy', 'chocolate', 'popcorn', 'pretzels'],
        'household': ['soap', 'shampoo', 'toothpaste', 'paper_towels', 'detergent', 'cleaning_supplies'],
        'electronics': ['batteries', 'phone_charger', 'headphones', 'usb_cable', 'power_bank'],
        'clothing': ['socks', 'underwear', 't_shirt', 'jeans', 'shoes', 'hat', 'scarf'],
        'health': ['vitamins', 'pain_reliever', 'bandages', 'sunscreen', 'first_aid'],
        'automotive': ['motor_oil', 'car_wash', 'air_freshener', 'tire_pressure_gauge']
    }
    
    # Flatten all items into a single list
    all_items = []
    for category, items in item_categories.items():
        all_items.extend(items)
    
    # Define some frequent itemsets to repeat
    frequent_itemsets = [
        ['milk', 'bread'],
        ['chips', 'soda'],
        ['eggs', 'bacon', 'toast'],
        ['coffee', 'cookies'],
        ['rice', 'beans', 'chicken'],
        ['detergent', 'paper_towels'],
        ['shampoo', 'soap'],
        ['popcorn', 'candy', 'soda'],
        ['t_shirt', 'jeans'],
        ['batteries', 'phone_charger']
    ]
    
    # Generate transactions
    transactions = []
    num_frequent = int(num_transactions * 0.3)  # 30% will be frequent itemsets
    for i in range(num_frequent):
        itemset = random.choice(frequent_itemsets)
        num_items = len(itemset)
        utilities = [random.randint(10, 50) for _ in range(num_items)]
        quantities = [random.randint(1, 5) for _ in range(num_items)]
        items_str = ' '.join(itemset)
        utilities_str = ' '.join(map(str, utilities))
        quantities_str = ' '.join(map(str, quantities))
        transaction_line = f"{items_str}:{utilities_str}:{quantities_str}"
        transactions.append(transaction_line)
    
    # The rest are random itemsets
    for i in range(num_transactions - num_frequent):
        num_items = random.randint(2, 6)
        selected_items = random.sample(all_items, k=num_items)
        utilities = [random.randint(10, 50) for _ in range(num_items)]
        quantities = [random.randint(1, 5) for _ in range(num_items)]
        items_str = ' '.join(selected_items)
        utilities_str = ' '.join(map(str, utilities))
        quantities_str = ' '.join(map(str, quantities))
        transaction_line = f"{items_str}:{utilities_str}:{quantities_str}"
        transactions.append(transaction_line)
    
    # Shuffle transactions
    random.shuffle(transactions)
    
    # Write to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['transaction'])
        # Write transactions
        for transaction in transactions:
            writer.writerow([transaction])
    
    print(f"Generated {num_transactions} transactions and saved to {output_file}")
    print(f"Sample transactions:")
    for i in range(min(5, len(transactions))):
        print(f"  {i+1}. {transactions[i]}")
    
    return output_file

if __name__ == "__main__":
    # Generate the dataset
    output_file = generate_foodmart_dataset(1500, "generated_foodmart_dataset.csv")
    print(f"\nDataset generated successfully: {output_file}") 