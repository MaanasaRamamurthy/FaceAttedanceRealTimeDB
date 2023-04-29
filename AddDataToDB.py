import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendacerealtime-953f0-default-rtdb.firebaseio.com/"
})

# this will create student directory and inside that we can add all IDs of the students
ref = db.reference('Students')

data = {
    "4055":
        {
            "name": "Chanandler Bong",
            "major": "Transponster",
            "starting_year": 1990,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2023-4-29 00:54:34"
        },
    "4056":
        {
            "name": "Monica",
            "major": "Cook",
            "starting_year": 1992,
            "total_attendance": 14,
            "standing": "O",
            "year": 3,
            "last_attendance_time": "2023-4-29 00:54:34"
        },
    "4057":
        {
            "name": "Rachel",
            "major": "Ralph Lauren",
            "starting_year": 1990,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2023-4-29 00:54:34"
        },
    "4058":
        {
            "name": "Joey",
            "major": "Soap Opera",
            "starting_year": 1995,
            "total_attendance": 12,
            "standing": "C",
            "year": 4,
            "last_attendance_time": "2023-4-29 00:54:34"
        },
    "4059":
        {
            "name": "Phoebe",
            "major": "Smelly Cat",
            "starting_year": 1994,
            "total_attendance": 10,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2023-4-29 00:54:34"
        },
    "4060":
        {
            "name": "Ross",
            "major": "Dinosaurs",
            "starting_year": 1990,
            "total_attendance": 7,
            "standing": "O",
            "year": 5,
            "last_attendance_time": "2023-4-29 00:54:34"
        }
    # "321654":
    #     {
    #         "name": "Chanandler Bong",
    #         "major": "sarcasm",
    #         "Starting Year": 1990,
    #         "total_attendance": 6,
    #         "standing": "G",
    #         "year": 4,
    #         "last_attendance_time": "2022-12-11 00:54:34"
    #     },
    # "852741":
    #     {
    #         "name": "Chanandler Bong",
    #         "major": "sarcasm",
    #         "Starting Year": 1990,
    #         "total_attendance": 6,
    #         "standing": "G",
    #         "year": 4,
    #         "last_attendance_time": "2022-12-11 00:54:34"
    #     },
    # "963852":
    #     {
    #         "name": "Chanandler Bong",
    #         "major": "sarcasm",
    #         "Starting Year": 1990,
    #         "total_attendance": 6,
    #         "standing": "G",
    #         "year": 4,
    #         "last_attendance_time": "2022-12-11 00:54:34"
    #     },

}

for key,value in data.items():
    ref.child(key).set(value)