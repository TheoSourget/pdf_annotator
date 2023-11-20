import pandas as pd
import streamlit as st
import bcrypt
import os
import glob
import shutil

st.set_page_config(
    page_title="PDF Annotator",
    page_icon="📄",
)

#Loading project part
st.title("Get project labels")
projects_info = pd.read_csv("./data/projects_info.csv")
st.write("Load project")
col1,col2 = st.columns(2)

with col1:
    project_name = st.selectbox("Project name",projects_info["name"].unique(),index=None,label_visibility="collapsed")
with col2:
    load_project_button = st.button("Load")

if load_project_button:
    if not project_name:
        st.error("Select a project")
    else:
        shutil.make_archive(f'./data/{project_name.replace(" ","")}/{project_name.replace(" ","")}_annotations', 'zip', f'./data/{project_name.replace(" ","")}/annotations')
        with open(f'./data/{project_name.replace(" ","")}/{project_name.replace(" ","")}_annotations.zip', "rb") as fp:
            btn = st.download_button(
                label="Download Annotations",
                data=fp,
                file_name=f'{project_name.replace(" ","")}_annotations.zip',
                mime="application/zip"
            )
        os.remove(f'./data/{project_name.replace(" ","")}/{project_name.replace(" ","")}_annotations.zip')
