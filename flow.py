import base64
import io

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from prefect import flow, task
from prefect.client import get_client
from prefect.orion.schemas.filters import FlowFilter
from prefect.orion.schemas.sorting import FlowRunSort


@task
async def get_flow_names(flow_name: str = None, limit: int = 15):
    async with get_client() as client:
        flow_runs = await client.read_flow_runs(
            flow_filter=FlowFilter(name={"any_": flow_name}) if flow_name else None,
            limit=limit,
            sort=FlowRunSort.EXPECTED_START_TIME_DESC,
        )

    flow_run_names = [flow_run.name for flow_run in sorted(flow_runs, key=lambda d: d.created, reverse=True)]
    print(flow_run_names)
    return flow_run_names


@task
def clean_flow_run_names(flow_run_name: str) -> str:
    return flow_run_name.replace("-", " ")


@task
def get_prompt() -> str:
    return "chocolate toad"


@task
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


@task
def get_images_from_response(response: requests.Response) -> list[Image]:
    # Convert bytes to images
    images_bytes = [base64.b64decode(image) for image in response.json()["images"]]
    return [Image.open(io.BytesIO(b)) for b in images_bytes]


@task
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


@task
def add_border_and_prompt(image: Image, prompt: str, border_size: int = 45) -> Image:
    prefect_blue = (2, 77, 253)
    prefect_navy = (9, 4, 34)

    image = ImageOps.expand(image, border=border_size, fill=prefect_navy)
    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size
    h_center = image_width / 2

    font = "FONTS/arial.ttf"

    # Add prompt
    draw.text(
        (h_center, border_size / 2),
        prompt,
        prefect_blue,
        font=ImageFont.truetype(font, 36),
        anchor="mm",
    )

    # Add attribution
    draw.text(
        (h_center, image_height - border_size / 2),
        "Generated using craiyon.com",
        prefect_blue,
        font=ImageFont.truetype(font, 20),
        anchor="mm",
    )
    return image


@task
def save_image(image: Image, file_name: str):
    image.save(f"images/{file_name}.png", "PNG")


@flow(name="Generate Craiyon images")
def craiyon_flow():
    flow_run_names = get_flow_names.submit(limit=5)
    prompt_futures = clean_flow_run_names.map(flow_run_names)  # TODO: Backup prompt

    responses_futures = perform_request.map(prompt_futures)

    for response_f, prompt_f in zip(responses_futures, prompt_futures):
        response = response_f.result()

        if response.status_code == 200:
            prompt = prompt_f.result()

            images = get_images_from_response.submit(response)
            image = combine_images.submit(images)
            image = add_border_and_prompt.submit(image, prompt)
            save_image.submit(image, prompt)

        else:
            print(f"Bad response: {response.status_code}")


if __name__ == "__main__":
    craiyon_flow()
