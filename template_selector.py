import json


def analyze_ad_data(ad_data):
    return {
        "num_photos": len(ad_data.get("photos", [])),
        "text_length": len(ad_data.get("description", "").strip()),
        "has_logo": bool(ad_data.get("logo"))
    }

def photo_score(ad_photos, template_slots):
    if template_slots < ad_photos:
        # Penalize templates that can't fit all photos
        return template_slots / ad_photos
    else:
        # Allow extra slots, but prefer tighter fit
        return ad_photos / template_slots
def score_template(template_meta, ad_meta):
    img_score = photo_score(ad_meta["num_photos"], template_meta["image_slots"])
    text_score = min(ad_meta["text_length"], template_meta["text_char_capacity"]) / max(1, ad_meta["text_length"])
    return 0.6 * img_score + 0.4 * text_score

def select_best_template(ad_data, cache_path="./cache/layout_metadata.json"):
    with open(cache_path, "r") as f:
        templates = json.load(f)

    ad_meta = analyze_ad_data(ad_data)

    best_template = None
    best_score = -1

    for name, meta in templates.items():
        score = score_template(meta, ad_meta)
        if score > best_score:
            best_score = score
            best_template = name

    return {"selected_template": best_template}
