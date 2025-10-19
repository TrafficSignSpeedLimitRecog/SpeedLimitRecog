import requests
import os

# Folder do zapisu zdjęć
output_dir = './data/picsum_photos'
os.makedirs(output_dir, exist_ok=True)

# Pobierz 100 zdjęć
for i in range(1, 101):
    url = 'https://picsum.photos/300'
    response = requests.get(url)

    if response.status_code == 200:
        filename = f'image_{i:03}.jpg'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f'Pobrano {filename}')
    else:
        print(f'Błąd podczas pobierania zdjęcia {i}: HTTP {response.status_code}')