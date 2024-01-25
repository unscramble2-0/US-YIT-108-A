from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import requests
from roboflow import Roboflow
import requests
import os
from ultralytics import YOLO
import shutil
model = YOLO(r"D:\Unscramble\image_analysis\best.pt")


app = FastAPI()

# Add CORS middleware to allow all origins (you can customize this based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you may want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Replace with your Imgur API key
IMGUR_CLIENT_ID = "406e5aeef8c86b3"

# Roboflow API key
ROBOFLOW_API_KEY = "sJHTpV6pUYQWa6xBXgMC"  # Use the provided API key

ROBOFLOW_PROJECT_NAME = "dentex-3xe7e"
ROBOFLOW_MODEL_VERSION = 2

# Initialize Roboflow
# rf = Roboflow(api_key=ROBOFLOW_API_KEY)
# project = rf.workspace().project(ROBOFLOW_PROJECT_NAME)
# model = project.version(ROBOFLOW_MODEL_VERSION).model

def upload_to_imgur(file):
    imgur_response = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"},
        files={"image": (file.filename, file.file, file.content_type)},
    )
    
    imgur_data = imgur_response.json()
    print(imgur_data)
    imgur_link = imgur_data["data"]["link"]
    return imgur_link

def download_and_save_image(original_link, save_path):
    try:
        # Download image from the original link
        response = requests.get(original_link)
        response.raise_for_status()  # Check for HTTP errors

        # Save the image to the specified path
        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"Image downloaded and saved at: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
def from_dir_image_to_imgur(image_path):
    try:
        # Prepare headers for the request
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}

        # Read the image file
        with open(image_path, 'rb') as file:
            # Make the upload request to Imgur
            imgur_response = requests.post(
                'https://api.imgur.com/3/image',
                headers=headers,
                files={'image': (os.path.basename(image_path), file)}
            )

            imgur_data = imgur_response.json()

            if imgur_response.status_code == 200 and imgur_data.get('data'):
                imgur_link = imgur_data['data']['link']
                print(f"Image uploaded to Imgur. Link: {imgur_link}")
                return imgur_link
            else:
                print(f"Error uploading image to Imgur: {imgur_data}")

    except Exception as e:
        print(f"Error uploading image to Imgur: {e}")
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # Upload original image to Imgur
    # original_imgur_link = upload_to_imgur(file)
    # print(file)
    # download_and_save_image(original_imgur_link, 'temp_in/temp.jpg')
    os.makedirs('temp_in', exist_ok=True)
    save_path = f'temp_in/temp.jpg'
    with open(save_path, 'wb') as save_file:
        save_file.write(file.file.read())
    os.makedirs('temp_out', exist_ok=True)
    results = model.predict(source="temp_in/temp.jpg", save=True ,project='temp_out',name='prediction')
    # Download the image from Imgur
    # imgur_response = requests.get(original_imgur_link)
    # img_data = BytesIO(imgur_response.content)

    # # Save the image to a temporary file in a specific directory (e.g., temp_in)
    # temp_in_dir = "temp_in"
    
    # with tempfile.NamedTemporaryFile(dir=temp_in_dir, delete=False, suffix=".jpg") as temp_file:
    #     temp_file.write(imgur_response.content)
    #     temp_file_path = temp_file.name
    # img_data = BytesIO(imgur_response.content)

    # Process the image using Roboflow
    # roboflow_response = model.predict(r'D:\Unscramble\temp_in\temp.jpg', confidence=40, overlap=30).save('temp_out/prediction.jpg')
    
    # Upload processed image to Imgur
    processed_image_path = f"temp_out/prediction/temp.jpg"
    
    
    processed_imgur_link = from_dir_image_to_imgur(processed_image_path)
    shutil.rmtree('temp_out/prediction')
    

    # Return links
    return { "processed_image_link": processed_imgur_link}


@app.get("/", response_class=HTMLResponse)
async def get_form():
    return """
    <form action="/uploadfile/" enctype="multipart/form-data" method="post">
        <input name="file" type="file">
        <input type="submit">
    </form>
    """

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
