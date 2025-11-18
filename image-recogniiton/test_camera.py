import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
# Step 1: Path to the folder containing your images
path = 'images'  # Make sure the folder is named "images" and is in the same directory as this script

# Lists to hold image data
images = []
names = []

# Load images and names from the folder
image_files = os.listdir(path)
for file in image_files:
    img = cv2.imread(f'{path}/{file}')
    images.append(img)
    names.append(os.path.splitext(file)[0])  # Extract name without extension

# -----------------------------
# Step 1: Load images and names
# -----------------------------path = 'Images'  # Folder containing images of people
images = []
names = []
image_files = os.listdir(path)

for img_file in image_files:
    img = cv2.imread(f'{path}/{img_file}')
    images.append(img)
    names.append(os.path.splitext(img_file)[0])  # Get name without extension

# -----------------------------
# Step 2: Encode faces
# -----------------------------
def find_encodings(images):
    encode_list = []
    for img in images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img_rgb)
        if encodes:  # Make sure at least one face is found
            encode_list.append(encodes[0])
    return encode_list

encode_list_known = find_encodings(images)
print("✅ Face encoding complete")

# -----------------------------
# Step 3: Attendance logging
# -----------------------------
def mark_attendance(name):
    filename = 'Attendance.csv'
    try:
        with open(filename, 'r+') as f:
            data_list = f.readlines()
            name_list = [line.split(',')[0] for line in data_list]
            if name not in name_list:
                now = datetime.now()
                dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
                f.writelines(f'{name},{dt_string}\n')
    except FileNotFoundError:
        with open(filename, 'w') as f:
            f.writelines('Name,Time\n')
            now = datetime.now()
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'{name},{dt_string}\n')

# -----------------------------
# Step 4: Start webcam
# -----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend for Windows

if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()
else:
    print("🎥 Camera is on! Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame.")
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the current frame
    faces_current = face_recognition.face_locations(rgb_small_frame)
    encodes_current = face_recognition.face_encodings(rgb_small_frame, faces_current)

    for encode_face, face_loc in zip(encodes_current, faces_current):
        matches = face_recognition.compare_faces(encode_list_known, encode_face)
        face_distances = face_recognition.face_distance(encode_list_known, encode_face)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = names[best_match_index].upper()
            mark_attendance(name)

            # Scale back face locations since we used a smaller frame
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

            # Draw rectangle and label on the original frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow('Smart Attendance System', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()