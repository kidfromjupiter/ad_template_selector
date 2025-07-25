import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_character_count(roi_image):
    """
    Runs OCR on the cropped text region and returns the character count.
    """
    result = reader.readtext(roi_image, detail=0, paragraph=True)
    if result:
        combined_text = " ".join(result)
        return len(combined_text), combined_text
    return 0, ""