#!/bin/bash

# Folder containing cmc folders which contain card images
IMAGE_ROOT="/Users/amethystpilzer/Library/Mobile Documents/com~apple~CloudDocs/MomirPi/cards"

# Iterate through all subdirectories
for dir in "${IMAGE_ROOT}"/*; do
    # Check if directory is empty
    if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
        # Create a new folder for the converted files
        mkdir -p "${dir}/converted_files"
        
        # Iterate through each PNG file and convert it to a rescaled monochrome bitmap
        for png_file in "${dir}"/*.png; do
            if [ -f "$png_file" ]; then
                echo "Resizing and converting to grayscale for: $png_file"
                
                # Define the output filename by replacing the extension with bmp
                output_file="${dir}/converted_files/$(basename -- "$png_file" .png).bmp"
                
                # Use ImageMagick's convert command to perform the conversion
                magick convert "$png_file" -resize 384x -colorspace Gray -monochrome "$output_file"
                
                # Check if conversion was successful
                if [ $? -eq 0 ]; then
                    echo "Conversion successful: $png_file"
                else
                    echo "Error converting: $png_file"
                fi
            fi
        done
    else
        echo "No PNG files found in directory: $dir"
    fi
done
