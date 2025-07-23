import random
import csv

def generate_client2_dataset(num_transactions=1200, output_file="client2_foodmart_dataset.csv"):
    """
    Generate a FoodMart-formatted dataset for Client 2 with different items and patterns.
    
    New Format: item_id1 item_id2 ... item_idN:utility1 utility2 ... utilityN:quantity1 quantity2 ... quantityN
    Each transaction line has the same number of items, per-item utilities, and quantities.
    Different itemsets and patterns compared to the original dataset.
    """
    
    # Define different item categories for Client 2 (different store focus)
    item_categories = {
        'premium_food': ['organic_milk', 'artisan_bread', 'free_range_eggs', 'aged_cheese', 'grass_fed_butter', 
                        'greek_yogurt', 'granola', 'quinoa', 'organic_rice', 'lentils'],
        'premium_beverages': ['espresso', 'herbal_tea', 'fresh_juice', 'craft_soda', 'mineral_water', 
                             'craft_beer', 'organic_wine', 'almond_milk', 'green_tea'],
        'gourmet_snacks': ['organic_chips', 'artisan_cookies', 'whole_grain_crackers', 'premium_nuts', 
                          'dark_chocolate', 'organic_popcorn', 'sea_salt_pretzels'],
        'premium_household': ['natural_soap', 'organic_shampoo', 'fluoride_free_toothpaste', 
                             'bamboo_paper_towels', 'eco_detergent', 'natural_cleaning'],
        'tech_accessories': ['wireless_charger', 'bluetooth_headphones', 'type_c_cable', 'portable_speaker', 
                            'smart_watch_band'],
        'premium_clothing': ['organic_cotton_socks', 'bamboo_underwear', 'premium_t_shirt', 'designer_jeans', 
                            'leather_shoes', 'wool_hat', 'cashmere_scarf'],
        'wellness': ['probiotics', 'omega_3', 'collagen_peptides', 'natural_sunscreen', 'essential_oils'],
        'outdoor': ['hiking_boots', 'camping_gear', 'water_bottle', 'backpack', 'sports_nutrition']
    }
    
    # Flatten all items into a single list
    all_items = []
    for category, items in item_categories.items():
        all_items.extend(items)
    
    # Define different frequent itemsets for Client 2 (different buying patterns)
    frequent_itemsets = [
        ['organic_milk', 'artisan_bread'],
        ['espresso', 'artisan_cookies'],
        ['free_range_eggs', 'organic_rice', 'quinoa'],
        ['herbal_tea', 'dark_chocolate'],
        ['organic_juice', 'greek_yogurt'],
        ['eco_detergent', 'bamboo_paper_towels'],
        ['natural_soap', 'organic_shampoo'],
        ['organic_popcorn', 'craft_soda', 'premium_nuts'],
        ['premium_t_shirt', 'designer_jeans'],
        ['wireless_charger', 'bluetooth_headphones'],
        ['probiotics', 'omega_3'],
        ['hiking_boots', 'water_bottle'],
        ['organic_wine', 'aged_cheese'],
        ['granola', 'almond_milk'],
        ['essential_oils', 'natural_sunscreen']
    ]
    
    # Generate transactions
    transactions = []
    num_frequent = int(num_transactions * 0.35)  # 35% will be frequent itemsets (higher than original)
    for i in range(num_frequent):
        itemset = random.choice(frequent_itemsets)
        num_items = len(itemset)
        # Higher utility range for premium items
        utilities = [random.randint(25, 75) for _ in range(num_items)]
        quantities = [random.randint(1, 3) for _ in range(num_items)]  # Lower quantities for premium items
        items_str = ' '.join(itemset)
        utilities_str = ' '.join(map(str, utilities))
        quantities_str = ' '.join(map(str, quantities))
        transaction_line = f"{items_str}:{utilities_str}:{quantities_str}"
        transactions.append(transaction_line)
    
    # The rest are random itemsets with different patterns
    for i in range(num_transactions - num_frequent):
        # Client 2 tends to buy fewer items per transaction but higher quality
        num_items = random.randint(1, 4)  # Smaller transaction sizes
        selected_items = random.sample(all_items, k=num_items)
        # Higher utilities for premium items
        utilities = [random.randint(20, 80) for _ in range(num_items)]
        quantities = [random.randint(1, 3) for _ in range(num_items)]  # Lower quantities
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
    
    print(f"Generated {num_transactions} transactions for Client 2 and saved to {output_file}")
    print(f"Sample transactions:")
    for i in range(min(5, len(transactions))):
        print(f"  {i+1}. {transactions[i]}")
    
    return output_file

if __name__ == "__main__":
    # Generate the dataset for Client 2 with 3500 transactions
    output_file = generate_client2_dataset(3500, "client2_foodmart_dataset.csv")
    print(f"\nClient 2 dataset generated successfully: {output_file}") 