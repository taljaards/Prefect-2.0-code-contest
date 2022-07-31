import base64
import io

import requests
from PIL import Image


def get_prompt() -> str:
    return "chocolate toad"


def perform_request(prompt: str) -> requests.Response:
    print("Starting request")
    headers = {
        "authority": "backend.craiyon.com",
        "accept": "application/json",
        "accept-language": "en-ZA,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,af;q=0.6,es;q=0.5",
        # Already added when you pass json=
        # 'content-type': 'application/json',
        "origin": "https://www.craiyon.com",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }

    json_data = {"prompt": prompt}

    post = requests.post("https://backend.craiyon.com/generate", headers=headers, json=json_data)
    print("Request done")
    return post


def get_images_from_response(response: requests.Response) -> list[Image]:
    # Convert bytes to images
    images_bytes = [base64.b64decode(image) for image in response.json()["images"]]
    return [Image.open(io.BytesIO(b)) for b in images_bytes]


def combine_images(images: list[Image]) -> Image:
    width, height = images[0].size  # Assume all images have the same size
    shape = (3, 3)

    combined_image_size = width * shape[1], height * shape[0]

    image = Image.new("RGB", combined_image_size)
    for row in range(shape[0]):
        for col in range(shape[1]):
            offset = width * col, height * row
            idx = row * shape[1] + col
            image.paste(images[idx], offset)
    return image


def save_image(image: Image, file_name: str = "image.png"):
    image.save(file_name, "PNG")


def main():
    prompt = get_prompt()
    response = perform_request(prompt)

    if response.status_code == 200:
        images = get_images_from_response(response)
        image = combine_images(images)
        save_image(image)

    else:
        print(f"Bad response: {response.status_code}")


main()
