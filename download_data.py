import requests
import zipfile
import os
import shutil


selected_files = [
    "202310-divvy-tripdata.zip",  # oct 2023
]

def download_and_extract_files():
    base_url = "https://divvy-tripdata.s3.amazonaws.com/"
    for file_name in selected_files:
        zip_url = base_url + file_name
        local_zip_path = os.path.join('downloads', file_name)
        print(f"Downloading {file_name}...")

        response = requests.get(zip_url, stream=True)
        os.makedirs('downloads', exist_ok=True)
        with open(local_zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_csv')

        csv_file = file_name.replace('zip', 'csv')
        source_csv_path = os.path.join('temp_csv', csv_file)
        target_csv_path = os.path.join('downloads', csv_file)
        os.rename(source_csv_path, target_csv_path)

        os.remove(local_zip_path)
        shutil.rmtree('temp_csv')

download_and_extract_files()