import cv2
import mediapipe as mp 
import threading

class NoseTracker:
    def __init__(self):
        self.noseY = None # storing current nose Y position
        self.baseNoseY = None
        self.running = True # flag to control the thread
# https://www.geeksforgeeks.org/multithreading-python-set-1/ 
        self.thread = threading.Thread(target=self.trackNose, daemon=True)
        self.thread.start()
        self.senstivity = 2

# https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector/python

    def trackNose(self):
        capture = cv2.VideoCapture(0) # initialize webcam capture
        mpFaceMesh = mp.solutions.face_mesh # loads face mesh module
        faceMesh = mpFaceMesh.FaceMesh() # initializes face mesh detector

        while self.running:
# gets current camera frame, outputs tuple: (boolean indicating success, frame)
            success, frame = capture.read() 
            if not success:
                continue
            
            frame = cv2.flip(frame, 1) # mirrors the frame horizontally
            # convert to RGB for mediapipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
            # process the frame to find face landmarks

#https://colab.research.google.com/drive/1FCxIsJS9i58uAsgsLFqDwFmiPO14Z2Hd 

            results = faceMesh.process(image) 
            # if face landmarks are detected
            if results.multi_face_landmarks: 
                #for each detected face in facial landmarks by mediapipe
                for faceLandmarks in results.multi_face_landmarks:
                    # tuple of (height, width, channels) 
                    height, width, shape = frame.shape 
                    # Nose tip landmark index [1]

#https://github.com/tensorflow/tfjs-models/blob/master/
# face-landmarks-detection/mesh_map.jpg 

                    nose = faceLandmarks.landmark[1] 
                    rawY = int(nose.y * height) 

                    if self.baseNoseY is None:
                        self.baseNoseY = rawY

                # Calculate the nose Y position relative to the base position
                    delta = rawY - self.baseNoseY
                    amplifiedY = self.baseNoseY + int(delta * self.senstivity)
                    self.noseY = amplifiedY
        capture.release()
        cv2.destroyAllWindows()
        faceMesh.close()

    def getNoseY(self):
        return self.noseY
    
# https://www.geeksforgeeks.org/multithreading-python-set-1/ 

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)  # Give it up to 1 second to clean up

