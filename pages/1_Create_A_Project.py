import base64
import pandas as pd
import streamlit as st
import bcrypt
import os
from streamlit_tags import st_tags

st.set_page_config(
    page_title="PDF Annotator",
    page_icon="📄",
)

st.title("Create a project")

#Project name part

#Get existing projects name
taken_names = pd.read_csv("./data/projects_info.csv")
project_name = st.text_input("Project name")
project_name_without_space = project_name.replace(" ","")
valid_name = False
if project_name:
    if not project_name_without_space.isalnum():
        st.error("Special character are not allowed in project name")
    elif project_name_without_space in taken_names["name"].apply(lambda x:x.replace(" ","")).unique():
        st.error("Name already used")
    else:
        st.success("Valide name")
        valid_name = True
else:
    st.info("Input a name")


#Files upload part
uploaded_files = st.file_uploader("Import your pdf files",type=["pdf"],accept_multiple_files=True)
lst_pdfs = []
for uploaded_file in uploaded_files:
    filename = uploaded_file.name.removesuffix(".pdf")
    bytes_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    lst_pdfs.append((filename,base64_pdf))
lst_pdfs = sorted(lst_pdfs)
#Group (fold) upload part
group_file = st.file_uploader("(Optional) Import your group file",type=["csv"],accept_multiple_files=False)
if group_file:
    folds = pd.read_csv(group_file)
else:
    folds = None
 
guide = st.file_uploader("Import your annotation guide",type=["pdf"],accept_multiple_files=False)

#Label part 
labels1 = st_tags(label='Input your first labels',text='Type a label and press enter')
labels2 = st_tags(label='(Optional) Input your second labels',text='Type a label and press enter')
additional_info = st.text_area(label='Additional information',value="")
save = st.button("save")
if save:
    if not lst_pdfs:
        st.info("No pdf files uploaded")
    elif not valid_name:
        st.info("Project name not valid")
    elif not labels1:
        st.info("No labels input")
    else:
        if not additional_info:
            additional_info = "No additional_info"
        else:
            additional_info = additional_info.replace('"','""')
            additional_info = additional_info.replace('\n','\\n')

        with open("./data/projects_info.csv","a") as name_file:
            name_file.write(f'\n{project_name},"{",".join(labels1)}","{",".join(labels2)}","{additional_info}"')
        os.mkdir(f"./data/{project_name_without_space}")
        os.mkdir(f"./data/{project_name_without_space}/pdfs")
        os.mkdir(f"./data/{project_name_without_space}/annotations")
        with open(f"./data/{project_name_without_space}/papers_info.csv","w") as paper_info_file:
            paper_info_file.write(f"index,filename,folds")
            for i,pdf in enumerate(lst_pdfs):
                with open(f"./data/{project_name_without_space}/pdfs/file_{i}","w") as b64_pdf_file:
                    b64_pdf_file.write(pdf[1])
                if folds is not None: 
                    if (folds["pdf_name"].isin([pdf[0]])).any():
                        fold_id = folds[folds["pdf_name"] == pdf[0]]["fold_id"].values[0]
                    else:
                        fold_id = None
                else:
                    fold_id = 0
                paper_info_file.write(f"\n{i},{pdf[0]},{fold_id}")
        if guide:
            with open(f"./data/{project_name_without_space}/guide.pdf","wb") as guide_file:
                guide_file.write(guide.getvalue())
        st.success("Project created! You can start the labeling in 'Label a project' section")