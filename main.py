from generate_template_cache import analyze_and_cache_template
from template_selector import select_best_template

#analyze_and_cache_template("./templates/template_1.png", "template_1.indt")
#analyze_and_cache_template("./templates/template_2.png", "template_2.indt")
#analyze_and_cache_template("./templates/template_3.png", "template_3.indt")

ad_data = {
  "headline": "Modern Seaside Apartment",
  "description": "A beautiful two-bedroom unit with views...",
  "photos": ["img1.jpg",  "img3.jpg", "img4.jpg","img1.jpg",  "img3.jpg", "img4.jpg"],
  "logo": "agency_logo.png"
}

selected = select_best_template(ad_data)

