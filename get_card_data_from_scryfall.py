import ijson
import time
import requests
import json

creatures = {}

# Open the JSON file from MTGJSON
with open('AtomicCards.json', 'r', encoding='utf-8') as file:
    # Parse the JSON objects one by one
    parser = ijson.items(file, 'data')
    # Iterate over the JSON card objects
    for item in parser:
        # Process each JSON object and get needed values; ignore digital only cards and un cards
        try:
            for key, value in item.items():
                if "Creature" in value[0]["type"]:
                    if value[0]["legalities"] and "A-" not in value[0]["name"]:
                        creatures[key] = value       
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

counter = 0  # Scryfall supports 70 items in each payload
payload_counter = 0  # Keep track of how many API calls we send
payload = {'identifiers': []}  # Identifier payload for Scryfall API call
creature_count = len(creatures)
estimated_payloads = int(creature_count / 70) + (creature_count % 70 > 0)
image_urls = []

for index, (key, value) in enumerate(creatures.items()):
    counter += 1
    payload["identifiers"].append({'oracle_id': value[0]["identifiers"]["scryfallOracleId"]})

    if counter >= 70 or index == creature_count - 1:
        time.sleep(0.3)
        try:
            response = requests.post('https://api.scryfall.com/cards/collection', json=payload)
            response.raise_for_status()
            response_dict = response.json()

            for item in response_dict["data"]:
                try:
                    image_urls.append({
                        "name": item.get("name", "Unknown"),
                        "image_url": item["image_uris"].get("art_crop", "No image available"),
                        "cmc": item.get("cmc", 0),
                        "mana_cost": item.get("mana_cost", "No mana cost available"),  # Fetch mana cost
                        "types": item.get("type_line", "No types available"),  # Fetch types/creature types
                        "text": item.get("oracle_text", "No text available"),  # Fetch card text
                        "power": item.get("power", "No power available"),  # Fetch power
                        "toughness": item.get("toughness", "No toughness available")  # Fetch toughness
                    })
                except Exception as e:
                    print(f"An error occurred while processing response data for {item.get('name', 'Unknown')}: {e}")
                    continue
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            continue
        finally:
            response = {}  # Clear response JSON
            payload = {'identifiers': []}  # Clear payload
            counter = 0
            payload_counter += 1
            print(f"Payload number {payload_counter} out of {estimated_payloads}")

# Write data to JSON file
with open('creatures_card_data.json', 'w') as fout:
    json.dump(image_urls, fout)

print(f"Script completed. {len(image_urls)} creatures with images processed.")
