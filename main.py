import os
import cv2
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-953f0-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-953f0.appspot.com"
})
bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread("Resources/background.png")


# --------------------------------------IMPORTING MODE IMAGES INTO A LIST --------------------------------
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))


# ----------------------------------------- LOAD THE ENCODED FILE -----------------------------------------
print("Loading encoded file")
file = open('EncodedFile.p', 'rb')
encodedImagesWithIds = pickle.load(file)
file.close()
# the pickle file returns 2 lists (images and the ids)
encodedList, StudentIds = encodedImagesWithIds
print("Encoded file loaded")


# ---------------------------------------- modify the input image and find the encoding --------------------------------
def modify_image(img):
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)    # scaling down the image for faster computation
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)     # converting the image to RGB because the face recognition module works only with RGB values
    faceCurFrame = face_recognition.face_locations(imgS)    # identifying the faces in the current frame
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)     # finding the face encodings in the current face
    return encodeCurFrame, faceCurFrame


def display_details(imgStudent_):
    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (808 + 50, 45 + 80), cv2.FONT_HERSHEY_COMPLEX,
                1, (0, 0, 0), 1)
    cv2.putText(imgBackground, str(ids), (808 + 197, 45 + 450), cv2.FONT_HERSHEY_COMPLEX,
                0.5, (255, 255, 255), 0)
    cv2.putText(imgBackground, str(studentInfo['major']), (808 + 196, 45 + 506), cv2.FONT_HERSHEY_COMPLEX,
                0.5, (255, 255, 255), 0)
    cv2.putText(imgBackground, str(studentInfo['standing']), (808 + 100, 45 + 580), cv2.FONT_HERSHEY_COMPLEX,
                0.7, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['year']), (808 + 205, 45 + 580), cv2.FONT_HERSHEY_COMPLEX,
                0.7, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo['starting_year']), (808 + 305, 45 + 580), cv2.FONT_HERSHEY_COMPLEX,
                0.7, (100, 100, 100), 1)

    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
    offset = (414 - w) // 2
    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 45 + 400), cv2.FONT_HERSHEY_COMPLEX,
                1, (50, 50, 50), 1)

    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent_


modeType = 0
counter = 0
ids = -1
imgStudent =[]

while True:
    success, img = cap.read()
    # ------------------------------------------- editing the images -----------------------------------------------
    encodeCurFrame, faceCurFrame = modify_image(img)

    # ------------------------------------- rendering the images on the background image ------------------------------
    imgBackground[160:640, 55:695] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

    # --------------------------------------- Comparing the images and storing the values -----------------------------
    # compare_faces returns a list with true or false for matching for each image
    # face_distance returns a list with face Distance(amt of how much each image in DB matches with the image on cam)
    # the index of minimum of the face_distance values is stored in the matchIndex variable

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodedList, encodeFace)
            faceDist = face_recognition.face_distance(encodedList, encodeFace)
            matchIndex = np.argmin(faceDist)

            if matches[matchIndex]:
                # ----------------------------------------- DISPLAY BOUNDING BOX -----------------------------------------
                # we scaled down the video image by 1/4 th. So, now, we multiply it by 4
                # we are adding the bounding box on the image background and not on the video itself. So, we need to add an
                # offset value since the video is not embedded at (0,0) of the background
                # bounding box takes the value as : x-value, y-value, width, height
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 160+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                ids = StudentIds[matchIndex]    # if match is found, it sets the id of the particular student
                if counter == 0:
                    counter = 1                 # if match is found, counter is updated to 1
                    modeType = 1                # if match is found, mode image that shows the details is displayed

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{ids}').get()         # Get the data of corresponding id
                blob = bucket.get_blob(f'Images/{ids}.jpg')                 # Get the Image from the storage for the id
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)        # converts the image to RGB value

                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapse = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapse)
                if secondsElapse > 30:
                    ref = db.reference(f'Students/{ids}')                       # update database for attendance
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2        # after 10 frames, update the mode to
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter <= 10:
                    display_details(imgStudent)

                counter += 1
                if counter >= 20:
                    counter = 0             # updates the mode image to active state
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Face Attendance", imgBackground)

    # ---------------------------------------------------- quit ---------------------------------------------------
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
