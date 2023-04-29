import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-953f0-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendacerealtime-953f0.appspot.com"
})


folderPath = 'Images'
PathList = os.listdir(folderPath)
StudentImgList = []
StudentIds = []

# -------------------------------------------- looping through the images ----------------------------------------
# i) storing the image path in one list
# ii) storing the image names in one list
# iii) uploading the images in the firebase storage

for path in PathList:
    # this will stores all image path inside the list
    StudentImgList.append(cv2.imread(os.path.join(folderPath, path)))
    # this will store the image name(student id is given as name) inside the list
    StudentIds.append(os.path.splitext(path)[0])

    # storing the images in the storage
    # it will create a Images folder and upload the images inside it in the DB
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


# ----------------------------------------- creating encodings for each image ------------------------------------
def findEncodings(Images):
    encodeList = []
    for img in Images:
        # face recognition module take images in RGB format only. So, conversion is done.
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


# ------------------------------------------------ encoding the images -------------------------------------------
print("Encoding Started....")
encodedImages = findEncodings(StudentImgList)
# creating another list that contains the encoded images and the corresponding student id.
# this list (encoded images + student id) is dumped into the pickle file and not the encoded images alone.
encodedImagesWithIds = [encodedImages, StudentIds]
print("Encoding Ended")

# ------------------------------------ we are storing the encodings in a pickle file ----------------------------------
file = open("EncodedFile.p", 'wb')
pickle.dump(encodedImagesWithIds, file)
file.close()
print("File saved")
