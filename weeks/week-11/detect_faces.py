"""Still-image detection; no identity or attendance inference.
Install OpenCV 4 first: python3 -m pip install "opencv-python<5"
Run: python3 detect_faces.py [path/to/image.jpg]
"""
import csv
import sys
from pathlib import Path
import cv2


def detect(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    height, width = image.shape[:2]
    image = cv2.resize(image, (1200, round(height * 1200 / width)))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1,
                                       minNeighbors=5, minSize=(20, 20))
    return image, faces


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("reitaku.jpg")
    image, faces = detect(source)
    cv2.imwrite("vision-input.jpg", image)
    with open("detected-boxes.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["x", "y", "w", "h"])
        for x, y, w, h in faces:
            writer.writerow([int(x), int(y), int(w), int(h)])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite("detected-faces.jpg", image)
    print(len(faces), "candidate face boxes; inspect misses and false positives.")


if __name__ == "__main__":
    main()
