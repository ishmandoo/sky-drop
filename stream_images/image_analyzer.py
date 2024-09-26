import csv
import os
from datetime import datetime

import easyocr
import numpy as np
from PIL import Image

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def fix_time(datetime_text):
    return f"{datetime_text[:-6]}:{datetime_text[-5:-3]}:{datetime_text[-2:]}"

# Function to extract information from an image
def extract_info(image_path, save_cropped=False):
    # Load the image
    image = Image.open(image_path)

    # Extract temperature from the top-right corner
    width, height = image.size
    temperature_box = (width - 82, 0, width - 48, 16)
    temperature_image = image.crop(temperature_box)
    temperature_image_np = np.array(temperature_image)
    temperature_text = reader.readtext(temperature_image_np, allowlist="0123456789")
    temperature = ' '.join([result[1] for result in temperature_text]).strip()

    # Extract datetime from the top-left corner
    timestamp_box = (0, 0, 380, 16)
    timestamp_image = image.crop(timestamp_box)
    timestamp_image_np = np.array(timestamp_image)
    date_text, time_text, ampm_text = reader.readtext(timestamp_image_np, allowlist="0123456789-:AMP")
    date, time, ampm = date_text[1], fix_time(time_text[1]), ampm_text[1]
    timestamp = datetime.strptime(" ".join([date, time, ampm]), r'%Y-%m-%d %I:%M:%S %p')

    # Calculate the average pixel brightness of the entire image
    grayscale_image = image.convert("L")  # Convert to grayscale

    # crop out top 20 and bottom 20 pixels 
    grayscale_image = grayscale_image.crop((0, 20, width, height-20))
    
    pixel_values = np.array(grayscale_image)
    average_brightness = pixel_values.mean()

    # Save the cropped images for debugging if required
    if save_cropped:
        temperature_image.save(f"temp_{os.path.basename(image_path)}")
        timestamp_image.save(f"datetime_{os.path.basename(image_path)}")

    return temperature, timestamp, average_brightness


# List to hold data for CSV
data_rows = []

# Start checking numbered files sequentially
file_number = 1

for image_directory in ("cam_a", "cam_b"):
    while True:
        filename = f"{str(file_number).zfill(6)}.jpg"  # Assuming the format is 000000.jpg, 000001.jpg, etc.
        image_path = os.path.join(image_directory, filename)

        if not os.path.exists(image_path):
            # Stop if the file is not found
            print(f"File not found: {filename}. Stopping.")
            break

        print(f"Processing: {image_path}")

        # Extract information from the image
        temperature, datetime, brightness = extract_info(image_path, save_cropped=False)
        
        # Append the data as a new row
        data_rows.append([filename, datetime, temperature, brightness])
        
        # Increment file number
        file_number += 1
        

    # Save results to CSV
    with open(os.path.join(image_directory, "data.csv"), mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Filename', 'Datetime', 'Temperature', 'Average Brightness'])
        csv_writer.writerows(data_rows)

    print(f"Data saved to {output_csv}")
