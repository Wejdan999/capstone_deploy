
import streamlit as st
try:
    import cv2
except ImportError as e:
    st.error(f"Error importing cv2: {e}")
import numpy as np
from PIL import Image
from ultralytics import YOLO
from paddleocr import PaddleOCR
import http.client
import json
import tempfile
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Driver Behavior Detection System")

# Load YOLO and OCR models
model_path = "/workspaces/capstone_deploy/best (1).pt"
ocr_model = PaddleOCR(use_angle_cls=True, lang='en')

if os.path.exists(model_path):
    yolo_model = YOLO(model_path)
else:
    st.error("Model file not found. Please check the path.")





# Create a sidebar for input type selection
st.sidebar.title("Driver Behavior Detection System")
input_option = st.sidebar.selectbox("Select Detection Type", ("Image Processing", "Video Processing", "Camera Processing"))

# Function to send SMS after behavior detection
def send_sms(custom_message):
        conn = http.client.HTTPSConnection("9klkx3.api.infobip.com")
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to": "966508056428"}],
                    "from": "447491163443",
                    "text": custom_message
                }
            ]
        })
        headers = {
            'Authorization': 'App 86cde8061a25db1d5d0ec2b667c11951-0df99321-d263-444f-abb5-879f95519e9d',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        
        response_json = json.loads(data)
        if response_json.get("messages"):
            message_status = response_json["messages"][0]["status"]["name"]
            if message_status == "PENDING_ACCEPTED":
                return "Message sent successfully!"
            else:
                return f"Failed to send message: {message_status}"
        return "Failed to send message"

# Function for model detection
def model_detection():
    if input_option == "Image Processing":
        st.subheader("Choose an image")
        image_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="image_file_uploader")
        if image_file is not None:
            img = Image.open(image_file)
            img_array = np.array(img)
            st.image(img, caption="Original Image", use_column_width=True)

            yolo_result = yolo_model(img_array)
            annotated_frame = yolo_result[0].plot() if len(yolo_result) > 0 else img_array
            st.image(annotated_frame, caption="Image after YOLO Application", use_column_width=True)

            ocr_result = ocr_model.ocr(img_array, cls=True)
            extracted_text = "\n".join([line[1][0] for line in ocr_result[0]]) if ocr_result else "No text found."
            st.subheader("Extracted Text")
            st.write(extracted_text)

            detected_behaviors = []
            EATING_AND_DRINKING = 1
            USING_PHONE = 2
            for result in yolo_result[0].boxes.data.tolist():
                class_id = int(result[5])
                if class_id in (EATING_AND_DRINKING, USING_PHONE):
                    detected_behaviors.append("Dear driver, please pay attention to your driving.")
            
            if detected_behaviors:
                custom_message = " | ".join(detected_behaviors)
                with st.spinner("Sending message..."):
                    response = send_sms(custom_message)
                st.success(response)

    elif input_option == "Video Processing":
        st.subheader("Choose a video")
        video_file = st.file_uploader("", type=["mp4", "avi", "mov"])
        if video_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(video_file.read())
            vid = cv2.VideoCapture(tfile.name)

            stframe = st.empty()

            text_detected = False
            behaviors_detected = False

            while vid.isOpened():
                ret, frame = vid.read()
                if not ret:
                    break

                yolo_result = yolo_model(frame)
                annotated_frame = yolo_result[0].plot() if len(yolo_result) > 0 else frame

                if not text_detected:
                    ocr_result = ocr_model.ocr(frame, cls=True)
                    if ocr_result:
                        detected_text = "\n".join([line[1][0] for line in ocr_result[0]])
                        text_detected = True
                        st.write(f"Extracted text: {detected_text}")
                
                detected_behaviors = []
                for result in yolo_result[0].boxes.data.tolist():
                    class_id = int(result[5])
                    if class_id in (EATING_AND_DRINKING, USING_PHONE):
                        detected_behaviors.append("Dear driver, please pay attention to your driving.")
                
                if detected_behaviors and not behaviors_detected:
                    custom_message = " | ".join(detected_behaviors)
                    with st.spinner("Sending message..."):
                        response = send_sms(custom_message)
                    st.success(response)
                    behaviors_detected = True
                
                stframe.image(annotated_frame, channels="BGR")

            vid.release()

    elif input_option == "Camera Processing":
        st.subheader("Camera Processing")
        
        if 'camera_open' not in st.session_state:
            st.session_state.camera_open = False
        
        if st.button("Open/Close Camera", key="toggle_camera"):
            st.session_state.camera_open = not st.session_state.camera_open
            
            if st.session_state.camera_open:
                cap = cv2.VideoCapture(0)
                stframe = st.empty()
                st.write("Camera is open. Click 'Open/Close Camera' to close.")

                behaviors_detected = False

                while st.session_state.camera_open:
                    ret, frame = cap.read()
                    if not ret:
                        st.write("Failed to capture frame.")
                        break

                    yolo_result = yolo_model(frame)
                    annotated_frame = yolo_result[0].plot() if len(yolo_result) > 0 else frame

                    stframe.image(annotated_frame, channels="BGR")

                    detected_behaviors = []
                    for result in yolo_result[0].boxes.data.tolist():
                        class_id = int(result[5])
                        if class_id in (EATING_AND_DRINKING, USING_PHONE):
                            detected_behaviors.append("Dear driver, please pay attention to your driving.")
                    
                    if detected_behaviors and not behaviors_detected:
                        custom_message = " | ".join(detected_behaviors)
                        with st.spinner("Sending message..."):
                            response = send_sms(custom_message)
                        st.success(response)
                        behaviors_detected = True

                cap.release()
                st.write("Camera closed.")

# Render the model detection functionality
model_detection()

confidence_threshold = st.sidebar.slider(
    'Confidence Threshold',
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.01  # Optional: Adjust the step for finer control
)

st.sidebar.subheader("Driver Statistics")

# Pie Chart 1: Mobile Users While Driving
st.sidebar.subheader("Mobile Users While Driving")
labels1 = ['Using', 'Not Using']
sizes1 = [53.6, 46.4]
colors1 = ['#ff9999', '#66b3ff']
explode1 = (0.1, 0)

fig1, ax1 = plt.subplots()
fig1.patch.set_facecolor('none')  # Set figure background color to transparent
ax1.pie(sizes1, explode=explode1, labels=labels1, colors=colors1,
        autopct='%1.1f%%', shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.sidebar.pyplot(fig1)

# Pie Chart 2: Drivers Who Had Accidents While Using the Phone
st.sidebar.subheader("Drivers Who Had Accidents While Using the Phone")
labels2 = ['Had', 'Hadn\'t']
sizes2 = [32.1, 67.9]
colors2 = ['#ffcc99', '#99ff99']
explode2 = (0.1, 0)

fig2, ax2 = plt.subplots()
fig2.patch.set_facecolor('none')  # Set figure background color to transparent
ax2.pie(sizes2, explode=explode2, labels=labels2, colors=colors2,
        autopct='%1.1f%%', shadow=True, startangle=90)
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
st.sidebar.pyplot(fig2)
