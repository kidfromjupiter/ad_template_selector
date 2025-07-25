import cv2
from ultralytics import YOLO
from pydantic import BaseModel, Field
from loguru import logger


def remove_supersets(boxes: list[tuple[int, int, int, int]], iou_threshold: float = 0.95) -> list[tuple[int, int, int, int]]:
    """
    Remove any boxes that fully contain smaller boxes (i.e., supersets).

    Args:
        boxes: List of (x1, y1, x2, y2) boxes
        iou_threshold: Minimum IOU that defines a near-full overlap

    Returns:
        Filtered list of boxes with supersets removed
    """
    def box_area(box):
        x1, y1, x2, y2 = box
        return max(0, x2 - x1) * max(0, y2 - y1)

    def iou(inner, outer):
        xi1 = max(inner[0], outer[0])
        yi1 = max(inner[1], outer[1])
        xi2 = min(inner[2], outer[2])
        yi2 = min(inner[3], outer[3])
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        return inter_area / box_area(inner)

    keep = []
    for i, box in enumerate(boxes):
        is_superset = False
        for j, other in enumerate(boxes):
            if i == j:
                continue
            if iou(other, box) > iou_threshold and box_area(other) < box_area(box):
                is_superset = True
                break
        if not is_superset:
            keep.append(box)
    return keep


class LabelBox(BaseModel):
    label: str = Field(example="Text", description="Label of the object")
    box: list[float] = Field(
        example=[0.0, 0.0, 0.0, 0.0], description="Bounding box coordinates"
    )


class LayoutAnalyzer:
    def __init__(self, model_path: str = "./weights/yolo-doclaynet.pt"):
        self.model = YOLO(model_path)

    def get_largest_text_box(self, label_boxes: list[LabelBox]) -> LabelBox | None:
        largest = None
        max_area = 0
        for lb in label_boxes:
            if lb.label.lower() == "text":
                x1, y1, x2, y2 = map(int, lb.box)
                area = (x2 - x1) * (y2 - y1)
                if area > max_area:
                    largest = lb
                    max_area = area
        return largest

    def analyze(self, image_path: str):
        logger.info(f"Analyzing layout from image: {image_path}")
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Invalid image: {image_path}")

        result = self.model.predict(image, verbose=True)[0]

        height = result.orig_shape[0]
        width = result.orig_shape[1]

        picture_boxes = []
        raw_label_boxes = []

        for cls_id, box in zip(result.boxes.cls.tolist(), result.boxes.xyxyn.tolist()):
            x1, y1, x2, y2 = box
            x1 = int(x1 * width)
            y1 = int(y1 * height)
            x2 = int(x2 * width)
            y2 = int(y2 * height)

            label = result.names[int(cls_id)]
            raw_label_boxes.append(LabelBox(label=label, box=[x1, y1, x2, y2]))

            if "picture" in label.lower() or "photo" in label.lower() or "image" in label.lower():
                picture_boxes.append((x1, y1, x2, y2))

        # Superset removal function
        def remove_supersets(boxes: list[tuple[int, int, int, int]], iou_threshold: float = 0.95):
            def box_area(box):
                x1, y1, x2, y2 = box
                return max(0, x2 - x1) * max(0, y2 - y1)

            def iou(inner, outer):
                xi1 = max(inner[0], outer[0])
                yi1 = max(inner[1], outer[1])
                xi2 = min(inner[2], outer[2])
                yi2 = min(inner[3], outer[3])
                inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
                return inter_area / box_area(inner)

            keep = []
            for i, box in enumerate(boxes):
                is_superset = False
                for j, other in enumerate(boxes):
                    if i == j:
                        continue
                    if iou(other, box) > iou_threshold and box_area(other) < box_area(box):
                        is_superset = True
                        break
                if not is_superset:
                    keep.append(box)
            return keep

        # Filter picture boxes
        filtered_picture_boxes = remove_supersets(picture_boxes)
        # Final filtered label list
        label_boxes = []
        for lb in raw_label_boxes:
            if (
                    "picture" in lb.label.lower()
                    or "photo" in lb.label.lower()
                    or "image" in lb.label.lower()
            ):
                box = tuple(map(int, lb.box))
                if box in filtered_picture_boxes:
                    label_boxes.append(lb)
            else:
                label_boxes.append(lb)

        logger.info(
            f"Detected objects: {len(label_boxes)}, Image size: {width}x{height}, Speed: {result.speed}"
        )

        return label_boxes


