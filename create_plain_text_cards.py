from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import requests
from io import BytesIO
import textwrap
import os

def create_card_image(name, image_url, text, type_line, mana_cost, power, toughness, output_path):
    # Define card dimensions
    card_width = 600
    card_height = int(card_width * 1.6)
    
    # Load the card image
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGBA")

    # Resize the image to fit the card
    img_width, img_height = image.size
    new_img_width = card_width - 20  # Adding padding
    new_img_height = int(img_height * (new_img_width / img_width))
    if new_img_height > card_height * 0.5:
        new_img_height = int(card_height * 0.5)
        new_img_width = int(img_width * (card_height * 0.5 / img_height))

    image = image.resize((new_img_width, new_img_height), Image.LANCZOS)

    # Convert to grayscale and enhance contrast for thermal printing
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)

    # Create a new blank image with white background
    new_image = Image.new("L", (card_width, card_height), 255)  # 'L' mode for grayscale
    
    # Draw text on the image
    draw = ImageDraw.Draw(new_image)

    # Load a typewriter font (adjust the path to your font file)
    font_path = "font.ttf"  # Update with your actual font path
    font_size_name = 36  # Font size for card name
    font_size_text = 22  # Reduced font size for text box
    font_size_type = 28  # Font size for type line
    font_size_power_toughness = 36  # Font size for power/toughness

    # Adjust font size if name exceeds 18 characters
    if len(name) > 18:
        font_size_name = 28  # Reduce font size if name is too long

    font_name = ImageFont.truetype(font_path, font_size_name)
    font_text = ImageFont.truetype(font_path, font_size_text)
    font_type = ImageFont.truetype(font_path, font_size_type)
    font_power_toughness = ImageFont.truetype(font_path, font_size_power_toughness)

    # Define positions
    name_position = (10, 10)
    mana_position = (card_width - 100, 10)  # Slightly more to the right
    artwork_position = (10, 50)
    type_position = (10, 50 + new_img_height + 10)  # Just below artwork
    text_position = (10, 50 + new_img_height + 60)  # Text starts after type line
    power_toughness_position = (card_width - 110, card_height - 50)  # Bottom-right corner

    # Draw card name
    draw.text(name_position, name, font=font_name, fill=0)  # Black text

    # Format the mana cost by removing curly braces
    mana_cost_formatted = mana_cost.replace("{", "").replace("}", "")

    # Draw mana cost at the top-right corner with the same font size as the card name
    draw.text(mana_position, mana_cost_formatted, font=font_name, fill=0)

    # Paste the resized image onto the new white background
    new_image.paste(image, artwork_position)

    # Adjust font size for type line if it exceeds 30 characters
    if len(type_line) > 30:
        font_size_type = 22  # Reduce font size if type line is too long
        font_type = ImageFont.truetype(font_path, font_size_type)

    # Draw the type line below the artwork
    draw.text(type_position, type_line, font=font_type, fill=0)

    # Draw the text box with adjusted wrap width
    y_position = text_position[1]
    max_text_width = card_width - 20  # Width available for text
    wrap_width = 44  # Adjust wrap width as needed
    for line in text.split('\n'):
        wrapped_lines = textwrap.fill(line, width=wrap_width)  # Adjust wrap width
        for wrapped_line in wrapped_lines.split('\n'):
            bbox = draw.textbbox((text_position[0], y_position), wrapped_line, font=font_text)
            text_width = bbox[2] - bbox[0]
            draw.text((text_position[0], y_position), wrapped_line, font=font_text, fill=0)
            y_position += bbox[3] - bbox[1] + 10  # Move down by the height of the line plus extra spacing

        y_position += 18  # Extra space between paragraphs

    # Format power and toughness
    power_toughness_text = f"{power}/{toughness}"
    draw.text(power_toughness_position, power_toughness_text, font=font_power_toughness, fill=0)

    # Save the new image in grayscale
    new_image.save(output_path)

def generate_cards_from_json(json_file):
    # Create the "cards" folder if it doesn't exist
    cards_folder = "cards"
    if not os.path.exists(cards_folder):
        os.makedirs(cards_folder)

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

        for card in data:
            name = card.get("name", "Failed to fetch name")
            image_url = card.get("image_url", "")
            text = card.get("text", "Failed to fetch text box")
            type_line = card.get("types", "Failed to fetch type")

            # Get the mana cost and remove the curly braces
            mana_cost = card.get("mana_cost", "").replace("{", "").replace("}", "")

            # Get the CMC and create a folder inside "cards" for each CMC
            cmc = int(card.get("cmc", 0))  # Convert to integer to avoid .0
            cmc_folder = os.path.join(cards_folder, str(cmc))  # '0', '1', '2', etc.
            if not os.path.exists(cmc_folder):
                os.makedirs(cmc_folder)
            
            # Create output path for the card image
            output_path = os.path.join(cmc_folder, f"{name.replace('/', '_').replace(' ', '_')}.png")

            # Get power and toughness
            power = card.get("power", "!!!")
            toughness = card.get("toughness", "!!!")

            # Create the card image
            create_card_image(name, image_url, text, type_line, mana_cost, power, toughness, output_path)
            print(f"Created image for card: {name}")

# Run the function to generate cards
generate_cards_from_json('creatures_card_data.json')
