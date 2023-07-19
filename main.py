import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime
import os

# Directory containing the face images
faces_directory = "faces"

# List all image filenames in the directory
image_filenames = os.listdir(faces_directory)

# List to store the names of known faces and their corresponding encodings
known_face_names = []
known_face_encodings = []

# Loop through each image and encode the faces
for filename in image_filenames:
    image_path = os.path.join(faces_directory, filename)
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        # Assuming there's only one face in each image
        face_encoding = face_encodings[0]
        name = os.path.splitext(filename)[0]  # Extract name from filename
        known_face_names.append(name)
        known_face_encodings.append(face_encoding)

# Get the current date and time
now = datetime.now()
current_date = now.strftime("%Y-%m-%d")

# Open the CSV file for attendance
csv_filename = f"{current_date}.csv"
with open(csv_filename, "w+", newline="") as f:
    lnwriter = csv.writer(f)

    video_capture = cv2.VideoCapture(0)

    while True:
        _, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Recognize faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distance)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # Add the text if a person is present
                if name in known_face_names:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOfText = (10, 100)
                    fontScale = 1.5
                    fontColor = (255, 0, 0)
                    thickness = 3
                    lineType = 2
                    cv2.putText(frame, name + " Present", bottomLeftCornerOfText, font, fontScale, fontColor, thickness,
                                lineType)

                    current_time = now.strftime("%H:%M:%S")
                    lnwriter.writerow([name, current_time])

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()
