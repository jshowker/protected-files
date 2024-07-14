import cv2
import face_recognition
import os

def load_known_faces(known_faces_dir):
    known_faces = []
    known_names = []
    for filename in os.listdir(known_faces_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(image_path)
            if len(image.shape) == 2:
                # Grayscale image, convert to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                # Image with alpha channel, convert to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            # Ensure image is in uint8 format
            image = image.astype('uint8')
            # Get face encoding
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(os.path.splitext(filename)[0])
    return known_faces, known_names

def highlight_face(frame, known_faces, known_names):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_faces, face_encoding)
        best_match_index = face_distances.argmin()
        if matches[best_match_index]:
            name = known_names[best_match_index]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return frame

def recognize_face_with_camera(known_faces_dir, target_name):
    known_faces, known_names = load_known_faces(known_faces_dir)

    video = cv2.VideoCapture(0)
    recognized = False

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = face_distances.argmin()

            if matches[best_match_index] and known_names[best_match_index] == target_name:
                recognized = True
                break

        if recognized:
            break

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
    return recognized
