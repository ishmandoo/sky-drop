import os

import requests


# Function to download an image from a URL
def download_image(url, folder, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Create the folder if it doesn't exist
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {file_path}")
        return True
    else:
        print(f"Failed to download: {filename} (HTTP {response.status_code})")
        return False

# Define the base URLs and folders
archives = {
    "archiveA": ("cam_a", 1),
    "archiveB": ("cam_b", 100),
}
base_url = "https://projectskydrop.com/cameras/"


# Loop through archives and download images
for archive, (folder, start) in archives.items():
    image_number = start
    while True:
        filename = f"{str(image_number).zfill(6)}.jpg"
        
        # Check if the file already exists in the folder
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            print(f"Already downloaded: {file_path}")
        else:
            url = f"{base_url}{archive}/{filename}"
            if not download_image(url, folder, filename):
                # Break the loop if the download fails (indicating no more images)
                break
        
        # Increment the image number
        image_number += 1
