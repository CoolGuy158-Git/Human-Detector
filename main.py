import os

import cv2 # My first time using this module, wish me luck!
import pyttsx3
import threading
import winsound
from datetime import datetime

alarm_thread = False # Check if alarm Thread is running
with open("logs.txt", "a") as file:
    file.write("=========================\n")
    file.write(f"Detector started at {datetime.now().strftime("%I:%M %p")}\n")
    file.write("=========================\n")
def play_alarm(text):
    """
    Function that plays the alarm sound and says 'text',
    it also logs the text to logs.txt.
    It also saves a jpg of the Intruder or basically just what cv2 sees.
    """
    with open("logs.txt", "r") as readable: # Check if the thing is already written
        readable = readable.read()
        if f"{datetime.now().strftime('%I:%M %p')} : {text}" not in readable: # if so do not write the log cuz then you'd just have duplicate
            with open("logs.txt", "a") as file:
                file.write(f"{datetime.now().strftime('%I:%M %p')} : {text}\n")
    global alarm_thread
    if alarm_thread:
        return
    alarm_thread = True

    if not os.path.exists(f"images/{text.replace(" ", "_")}_{datetime.now().strftime('%I-%M-%p')}.jpg"):
        cv2.imwrite(f"images/{text.replace(" ", "_")}_{datetime.now().strftime('%I-%M-%p')}.jpg", frame)
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    for i in range(2):
        winsound.Beep(800, 200)
        winsound.Beep(1500, 200)
    alarm_thread = False
alarm_thread_two = False # Check if alarm Thread is running

face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
side_face = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
smile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

camera = cv2.VideoCapture(0)
while True:
    ret, frame = camera.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        """
        Had to check for smiles inside the face loop because before that,
        Everytime it detected something that resembled a smile it would think human is close to the camera,
        however by adding this inside the face loop, smile would only be detected if there is a human face.
        """
        smiles = smile.detectMultiScale(roi_gray, 1.7, 20)
        for (sx, sy, sw, sh) in smiles:
            cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 0, 255), 2)

    side_faces = side_face.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in side_faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Camera", frame)
    try: # smiles could be undefined, so I wrapped it in a try
        if len(smiles) == 1 or len(smiles) > 1 and not len(faces) > 1: # Ok so I realized that if cv2 detects a smile that usually means the human is close to the camera so yea.
            # Ok this is a mess but basically if smile is one or smile is over 1 BUT faces is only 1 then yea only say 1 human is close, cuz sometimes it thinks there's two humans close to the cam just because like hte face looks like there's two smiles
            threading.Thread(target=play_alarm, args=("Human maybe close to the camera",), daemon=True).start()
        elif len(smiles) > 1:
            threading.Thread(target=play_alarm, args=(f"{len(smiles)} humans maybe close to the camera",), daemon=True).start()
    except NameError:
        pass

    if len(faces) == 1 or len(side_faces) == 1:
        threading.Thread(target=play_alarm, args=("Human detected",), daemon=True).start()
    elif len(faces) > 1 or len(side_faces) > 1:
        threading.Thread(target=play_alarm, args=(f"{len(faces)} humans detected",), daemon=True).start()
    if cv2.waitKey(1) & 0xFF == ord('e'):
        with open("logs.txt", "a") as file:
            file.write("========================\n")
            file.write(f"Detector ended at : {datetime.now().strftime("%I:%M %p")}\n")
            file.write("========================\n")
        break
camera.release()
cv2.destroyAllWindows()
