import os
import base64
import streamlit as st


def display_logo_title(image_path='logo.png', title_text="FindinGeo", image_height_em=1.2):
    """
    Displays a logo image inline with a title using st.markdown and Base64 encoding.
    Falls back to a simple st.title if the image file is not found or encoding fails.
    """
   
    encoded_string = None
    if not os.path.exists(image_path):
        pass
    else:
        try:
            with open(image_path, "rb") as image_file: # read in the binary mode
                encoded_string = base64.b64encode(image_file.read()).decode() # encode the image data to base64

        except Exception as e:
            st.error(f"Error encoding image: {e}")
            encoded_string = None

    
    if encoded_string:
        image_base64_url = f"data:image/png;base64,{encoded_string}"

        # Construct the HTML string
        html_title = f"""
        <h1>
            <img src="{image_base64_url}" style="height: {image_height_em}em; vertical-align: middle;"> FindinGeo
        </h1>
        """

        st.markdown(html_title, unsafe_allow_html=True) # render HTML tags

    else:
        st.title(title_text)
