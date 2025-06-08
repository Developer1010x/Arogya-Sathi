import streamlit as st
from ultralytics import YOLO
import random
import PIL
from PIL import Image, ImageOps
import numpy as np
import torchvision
import torch
import os

# Set page config at the very beginning
st.set_page_config(
    page_title=" X-ray Fracture Detection",
    page_icon="🩺",
    layout="wide"
)

from sidebar import Sidebar
import rcnnres, vgg
# hide deprication warnings which directly don't affect the working of the application
import warnings
warnings.filterwarnings("ignore")



# Sidebar
sb = Sidebar()


model = sb.model_name
conf_threshold = sb.confidence_threshold



#Main Page

st.title("🩺 Xray Detection")
st.write("The Application provides Bone Fracture Detection using multiple state-of-the-art computer vision models such as Yolo V8, ResNet, AlexNet, and CNN. To learn more about the app - Try it now!")

st.markdown("""
<style>

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 2px 2px 2px 2px;
        gap: 8px;
        padding-left: 10px;
        padding-right: 10px;
        padding-top: 8px;
        padding-bottom: 8px;
    }

    .stTabs [aria-selected="true"] {
          background-color: #7f91ad;
    }

</style>""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Test", "Overview"])

with tab2:
   st.markdown("### Overview")
   st.text_area(
    "Holistic Health care using AI",
    "",
    )
   
   
   
   st.markdown("#### Models Used")
   st.markdown("##### YoloV8")
   st.text_area(
       "Description",
       "YOLO (You Only Look Once) v8 is a state-of-the-art object detection model that offers excellent speed and accuracy. It processes the entire image in a single forward pass, making it ideal for real-time bone fracture detection in X-ray images.",
    )
   
   st.markdown("##### FasterRCNN with ResNet")
   st.text_area(
       "Description",
       "Faster R-CNN combined with ResNet backbone provides powerful feature extraction capabilities. This model excels at detecting varied sizes of fractures with high precision, using a region proposal network to identify areas of interest in X-ray images.",
       height=100,
    )
   
   st.markdown("##### SSD with VGG16")
   st.text_area(
       "Description",
       "Single Shot MultiBox Detector (SSD) with VGG16 backbone offers a good balance between speed and accuracy. This architecture is particularly effective at detecting multiple fractures of different sizes in a single X-ray image.",
    )

   
   
   
   
   
#weights
yolo_path = os.path.join("weights", "yolov8.pt")

   
with tab1:
    st.markdown("### Upload & Test")
    #Image Uploading Button
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    def set_clicked():
        st.session_state.clicked = True

    st.button('Upload Image', on_click=set_clicked)
    if st.session_state.clicked:
        image = st.file_uploader("", type=["jpg", "png"])
        
        
        if image is not None:
            st.write("You selected the file:", image.name)
            
            if model == 'YoloV8':
                try:
                    yolo_detection_model = YOLO(yolo_path)
                    yolo_detection_model.load()
                except Exception as ex:
                    st.error(f"Unable to load model. Check the specified path: {yolo_path}")
                    st.error(ex)
                
                col1, col2 = st.columns(2)

                with col1:
                    uploaded_image = PIL.Image.open(image)
                        
                    st.image(
                        image=image,
                        caption="Uploaded Image",
                        use_container_width=True
                    )

                    if uploaded_image:
                        if st.button("Execution"):
                            with st.spinner("Running..."):
                                res = yolo_detection_model.predict(uploaded_image,
                                                    conf=conf_threshold, augment=True, max_det=1)
                                boxes = res[0].boxes
                                res_plotted = res[0].plot()[:, :, ::-1]
                                
                                if len(boxes)==1:
                                
                                    names = yolo_detection_model.names
                                    probs = boxes.conf[0].item()
                                    
                                        
                                    for r in res:
                                        for c in r.boxes.cls:
                                            pred_class_label = names[int(c)]

                                    with col2:
                                        st.image(res_plotted,
                                                caption="Detected Image",
                                                use_container_width=True)
                                        try:
                                            with st.expander("Detection Results"):
                                                for box in boxes:
                                                    st.write(pred_class_label)
                                                    st.write(probs)
                                                    st.write(box.xywh)
                                        except Exception as ex:
                                            st.write("No image is uploaded yet!")
                                            st.write(ex)
                                
                                else:
                                    with col2:
                                        st.image(res_plotted,
                                                caption="Detected Image",
                                                use_container_width=True)
                                        try:
                                            with st.expander("Detection Results"):
                                                st.write("No Detection")
                                            #st.write(output[2])
                                        except Exception as ex:
                                            st.write("No Detection")
                                            st.write(ex)
                                    
                                        
            elif model == 'FastRCNN with ResNet':
                resnet_model = rcnnres.get_model()
                device = torch.device('cpu')
                resnet_model.to(device)

                
                col1, col2 = st.columns(2)

                with col1:
                    uploaded_image = PIL.Image.open(image)
                        
                    st.image(
                        image=image,
                        caption="Uploaded Image",
                        use_container_width=True
                    )
                    
                    content = Image.open(image).convert("RGB")
                    to_tensor = torchvision.transforms.ToTensor()
                    content = to_tensor(content).unsqueeze(0)
                    content.half()

                    if uploaded_image:
                        if st.button("Execution"):
                            with st.spinner("Running..."):
                                output = rcnnres.make_prediction(resnet_model, content, conf_threshold)
                                
                                print(output[0])

                                fig, _ax, class_name = rcnnres.plot_image_from_output(content[0].detach(), output[0])

                                with col2:
                                    st.image(rcnnres.figure_to_array(fig),
                                            caption="Detected Image",
                                            use_container_width=True)
                                    try:
                                        with st.expander("Detection Results"):
                                            st.write(class_name)
                                            st.write(output)
                                            #st.write(output[2])
                                    except Exception as ex:
                                        st.write("No image is uploaded yet!")
                                        st.write(ex)

            elif model == 'VGG16':
                vgg_model = vgg.get_vgg_model()
                device = torch.device('cpu')
                vgg_model.to(device)
                
                col1, col2 = st.columns(2)

                with col1:
                    uploaded_image = PIL.Image.open(image)
                        
                    st.image(
                        image=image,
                        caption="Uploaded Image",
                        use_container_width=True
                    )
                    
                    content = Image.open(image).convert("RGB")
                    to_tensor = torchvision.transforms.ToTensor()
                    content = to_tensor(content).unsqueeze(0)
                    content.half()

                    if uploaded_image:
                        if st.button("Execution"):
                            with st.spinner("Running..."):
                                output = rcnnres.make_prediction(vgg_model, content, conf_threshold)
                                
                                print(output[0])

                                fig, _ax, class_name = rcnnres.plot_image_from_output(content[0].detach(), output[0])

                                with col2:
                                    st.image(rcnnres.figure_to_array(fig),
                                            caption="Detected Image",
                                            use_container_width=True)
                                    try:
                                        with st.expander("Detection Results"):
                                            st.write(class_name)
                                            st.write(output)
                                            #st.write(output[2])
                                    except Exception as ex:
                                        st.write("No image is uploaded yet!")
                                        st.write(ex)

        
    else:
        st.write("Please upload an image to test")
