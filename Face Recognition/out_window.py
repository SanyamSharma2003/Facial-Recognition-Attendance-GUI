# FACIAL RECOGNITION ATTENDANCE GUI
from PyQt5.QtGui import QImage, QPixmap 
from PyQt5.uic import loadUi 
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog,QMessageBox
import cv2 # "pip install opencv-python" - use this if cv2 is not working or installed in your device.
import face_recognition # "pip install face_recognition" - to use face recognition functions and APIs.
import numpy as np # It will automatically installed when you will install face_recognition module.
import datetime
import os 
import csv
"""
Note: The UI design is made in Qt Designer and the tools used here(buttons, MessageBox, etc) are already instantiated in the Qt Designer.
You can see the UI design by opening the outputwindow.ui file in the Qt Designer("designer.exe" in your device).
"""
# Get current system time
class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self) # Load output form UI

        # datetime Time module
        now = QDate.currentDate() # Reading the date from the system clock
        current_date = now.toString('ddd dd MMMM yyyy') # Time format
        current_time = datetime.datetime.now().strftime("%I:%M %p") # Return the current local date and time in a particular format
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)

        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):
        """
        :param camera_name: link of camera or usb camera
        :return:
        """
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name))
        else:
            self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self)  # Create Timer

        # Known face encoding and known face name list
        path = 'ImagesAttendance' # Here all the known images are stored.
        if not os.path.exists(path):
            os.mkdir(path)
        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []
        attendance_list = os.listdir(path)

        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0]) # Storing names of the image files without their extension in class_names list.
        
        # Here we are finding the encodings of the images and storing them in the encode_list list.
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converting BGR image format to RGB image format
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0] # storing face_encodings of all img in images,
            self.encode_list.append(encodes_cur_frame)                         # in encode_list list.

        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # Emit the timeout() signal at x=10ms

    def face_rec_(self, frame, encode_list_known, class_names):
        """
        :param frame: frame from camera
        :param encode_list_known: known face encoding
        :param class_names: known face names
        :return:
        """

        # Check in and save data
        # csv Tables save data
        def mark_attendance(name):
            """
            :param name: detected face known or unknown one
            :return:
            """ 
            # Clock-in process...
            if self.ClockInButton.isChecked(): # Checking if clock-in button is pressed or not.
                self.ClockInButton.setEnabled(False) # Disable the clock-in button when clock-in button is pressed once.
                with open('Attendance.csv', 'a') as f: # Opening the csv file in write mode
                        if (name != 'unknown'): # Check in judgment ： Whether it is a recognized face
                            buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Clocking In?' , # Making a mssg box when the user
                                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # clicked on check-in button.
                            if buttonReply == QMessageBox.Yes: # If the user clicked the yes button.

                                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Clock In') # Writing the name, date and time format and status in file.
                                self.ClockInButton.setChecked(False)

                                self.NameLabel.setText(name) # Set the Name label
                                self.StatusLabel.setText('Clocked In') # Set the Stauts Label
                                self.HoursLabel.setText('Measuring') # Set the Time Label as "measuring"
                                self.MinLabel.setText('')

                                self.Time1 = datetime.datetime.now()
                                self.ClockInButton.setEnabled(True) # As we have set the name, status and time label, so we are enabling the
                                                                    # clock-in button which we have disabled earlier.
                            else:
                                print('Not clicked.') # i.e. user pressed "No" in the MessageBox.
                                self.ClockInButton.setEnabled(True)
            # Similarly for Clock-out of the user, we will do the same process as we did for Clock-in of the user.
            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, 'Cheers ' + name, 'Are you Clocking Out?',
                                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if buttonReply == QMessageBox.Yes:
                                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Clock Out')
                                self.ClockOutButton.setChecked(False)

                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Clocked Out')
                                self.Time2 = datetime.datetime.now()

                                self.ElapseList(name) # Now we have to define this function...
                                self.TimeList2.append(datetime.datetime.now())
                                CheckInTime = self.TimeList1[-1]
                                CheckOutTime = self.TimeList2[-1]
                                self.ElapseHours = (CheckOutTime - CheckInTime)
                                self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60)%60) + 'm')
                                self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60**2)) + 'h')
                                self.ClockOutButton.setEnabled(True)
                            else:
                                print('Not clicked.')
                                self.ClockOutButton.setEnabled(True)

        # Face recognition part
        faces_cur_frame = face_recognition.face_locations(frame) # finding locations of the faces as multiple faces can be detected in the camera.
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)
        # finding the matches
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame): # It will grab the face locations of the images one by one along with
                                                                            # their encodings.
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50) # and here it will do the matching with the
                                                                                                  # known faces stored in the encode_list_known.
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace) # It will give us the distance from each of the known faces
                                                                                     # and the lowest distance will be our best match.
            name = "unknown"
            best_match_index = np.argmin(face_dis) # This will give us index of the lowest distance i.e. for the best match.

            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # rectangle for the original image of color green and thickness of 2.
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1) # Displaying name in a rectangle.
            mark_attendance(name) # Passing the parameter name to the function(this function marks the attendence in the Attendance.csv file).

        return frame

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # Check-in time calculation
    def ElapseList(self,name):
        with open('Attendance.csv', "r") as csv_file: # Openin our csv file in read mode.
            csv_reader = csv.reader(csv_file, delimiter=',') # Reading from the csv file.
            line_count = 2

            Time1 = datetime.datetime.now() # Initializing the Time1 and Time2 variable to the current date and time so that
            Time2 = datetime.datetime.now() # we will get the default format of date and time.
            for row in csv_reader: # for every row in csv_reader
                for field in row: # for every field in every row
                    if field in row: 
                        if field == 'Clock In': # If the user clocked-in
                            if row[0] == name: # Checking the name
                                Time1 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S')) # Setting the time of check-in as earlier
                                                                    # we have only defined the format of the date and time in the csv file.
                                self.TimeList1.append(Time1) # Storing the Time1 variable in the TimeList1 list.
                        if field == 'Clock Out': # If the user is clocked-out
                            if row[0] == name: # Checking the name
                                Time2 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S')) # Setting the time of Check-out
                                self.TimeList2.append(Time2) # Storing the Time2 variable in the TimeList2 list.

    # These two functions are for updating the frame and displaying the image(by setting the size, pixels, format and other functionalities
    # of the image) in the camera.
    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :param window: number of window
        :return:
        """
        image = cv2.resize(image, (640, 480))
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)