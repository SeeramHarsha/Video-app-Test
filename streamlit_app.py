import streamlit as st
import requests
import base64
from PIL import Image
import io

st.title("AI Annotation Assistant")

topic = st.text_input("Enter Topic:")
image_file = st.file_uploader("Upload Image:", type=["png", "jpg", "jpeg"])

if image_file is not None:
    image = Image.open(image_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

    if st.button("Generate Annotations"):
        files = {"image": image_file.getvalue()}
        response = requests.post(
            "http://localhost:5000/generate_annotations",
            data={"topic": topic},
            files=files
        )

        if response.status_code == 200:
            annotations = response.json()["annotations"]
            st.subheader("Suggested Annotations:")
            for annotation in annotations:
                st.write(annotation)
        else:
            st.error("Error generating annotations.")