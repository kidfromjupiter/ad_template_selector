import os
import json
import cv2
from detect_layout import LayoutAnalyzer
from clip_classifier import ClipImageClassifier
from ocr import extract_text_character_count  # <- the OCR function you made

CACHE_PATH = "./cache/layout_metadata.json"

def analyze_and_cache_template(image_path: str, template_name: str):
    la = LayoutAnalyzer()
    clipper = ClipImageClassifier()
    image = cv2.imread(image_path)

    label_boxes = la.analyze(image_path)

    # Get largest text box & char count
    largest_text_box = la.get_largest_text_box(label_boxes)
    x1, y1, x2, y2 = map(int, largest_text_box.box)
    text_roi = image[y1:y2, x1:x2]
    char_count, _ = extract_text_character_count(text_roi)

    # Count house-related image slots
    image_slots = 0
    for label_box in label_boxes:
        label = label_box.label.lower()
        if "picture" in label:
            x1, y1, x2, y2 = map(int, label_box.box)
            roi = image[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            best_label, _ = clipper.classify(roi)
            if clipper.is_house_related(best_label):
                image_slots += 1

    # Load existing cache
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    # Update cache
    cache[template_name] = {
        "image_slots": image_slots,
        "text_char_capacity": char_count
    }

    # Write back
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


