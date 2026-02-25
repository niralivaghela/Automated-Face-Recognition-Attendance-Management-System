"""
Face Engine - OpenCV-based face detection and encoding
"""
import cv2
import numpy as np

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def detect_faces(gray_image):
    """Detect faces in grayscale image. Always returns a list (never empty tuple)."""
    try:
        faces = face_cascade.detectMultiScale(
            gray_image,
            scaleFactor=1.1,   # was 1.3 — more sensitive now
            minNeighbors=5,
            minSize=(60, 60)   # ignore tiny detections
        )
        # detectMultiScale returns empty tuple () when no faces — convert to list
        if len(faces) == 0:
            return []
        return list(faces)
    except Exception as e:
        print(f"Face detection error: {e}")
        return []

def extract_face_roi(image, x, y, w, h, size=(128, 128)):
    """Extract and resize face ROI"""
    try:
        face = image[y:y+h, x:x+w]
        if face.size == 0:
            return None
        face = cv2.resize(face, size)
        return face
    except Exception as e:
        print(f"Face ROI extraction error: {e}")
        return None

def encode_face(face_roi):
    """Create face encoding from ROI (normalized pixel values)"""
    try:
        if face_roi is None or face_roi.size == 0:
            return None
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
        gray = cv2.resize(gray, (128, 128))
        encoding = gray.flatten().astype(np.float32) / 255.0
        return encoding
    except Exception as e:
        print(f"Face encoding error: {e}")
        return None

def compare_faces(stored_encoding, live_encoding, threshold=7500):
    """
    Compare two face encodings.
    Returns (match: bool, distance: float)
    Lower distance = better match.
    """
    if stored_encoding is None or live_encoding is None:
        return False, 999999

    stored = np.array(stored_encoding, dtype=np.float32).flatten()
    live   = np.array(live_encoding,   dtype=np.float32).flatten()

    # Make sure same length
    min_len = min(len(stored), len(live))
    stored  = stored[:min_len]
    live    = live[:min_len]

    # Euclidean distance
    distance = float(np.linalg.norm(stored - live))
    match    = distance < threshold

    return match, distance

def capture_face_encoding(cap, num_samples=15):
    """Capture multiple frames and create average encoding"""
    encodings    = []
    sample_frame = None
    attempts     = 0
    max_attempts = num_samples * 3  # Try up to 3x samples to find faces

    while len(encodings) < num_samples and attempts < max_attempts:
        attempts += 1
        ret, frame = cap.read()
        if not ret:
            continue

        try:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)

            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_roi   = extract_face_roi(frame, x, y, w, h)
                if face_roi is not None:
                    enc = encode_face(face_roi)
                    if enc is not None:
                        encodings.append(enc)
                        if sample_frame is None:
                            sample_frame = frame.copy()
        except Exception as e:
            print(f"Frame capture error: {e}")
            continue

    if len(encodings) == 0:
        return None, None

    avg_encoding = np.mean(encodings, axis=0)
    return avg_encoding, sample_frame