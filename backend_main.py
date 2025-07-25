import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

from generate_template_cache import analyze_and_cache_template
from template_selector import select_best_template

app = FastAPI()

TEMPLATE_DIR = "./templates"

os.makedirs(TEMPLATE_DIR, exist_ok=True)


@app.post("/upload-template/")
async def upload_template(
        template_image: UploadFile = File(...),
        template_name: str = Form(...)
):
    # Save the file
    template_path = os.path.join(TEMPLATE_DIR, template_image.filename)
    with open(template_path, "wb") as buffer:
        shutil.copyfileobj(template_image.file, buffer)

    # Analyze and cache it
    indt_filename = f"{template_name}.indt"
    try:
        analyze_and_cache_template(template_path, indt_filename)
        return {"message": "Template uploaded and cached successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


class AdData(BaseModel):
    headline: str
    description: str
    photos: list[str]
    logo: str

@app.post("/select-template/")
async def select_template(ad_data: AdData):
    # Check if metadata exists
    if not os.path.exists("./cache"):
        return JSONResponse(
            status_code=400,
            content={"error": "No cached template metadata found. Please upload and cache templates first."}
        )
    try:
        best_template = select_best_template(ad_data.model_dump())
        return {"selected_template": best_template}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)