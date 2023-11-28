import pandas as pd
import streamlit as st
import bcrypt
import os
import glob

st.set_page_config( 
    page_title="PDF Annotator",
    page_icon="📄",
)

if "project_loaded" not in st.session_state:
        st.session_state.project_loaded = False

#Loading project part
st.title("Label a project")
projects_info = pd.read_csv("./data/projects_info.csv")
st.write("Load project")
col1, col2, col3 = st.columns(3)
with col1:
    project_name = st.selectbox("Project name",projects_info["name"].unique(),index=None,label_visibility="collapsed")
with col2:
    username = st.text_input("Your username",label_visibility="collapsed",placeholder="Your username")
    if username and not username.isalpha():
        username = None
        st.error("Username not valid, please only use alpha character")
with col3:
    load_project_button = st.button("Load")

if load_project_button or st.session_state.project_loaded:
    if not project_name:
        st.error("Select a project")
    elif not username:
        st.error("Input an username")
    else:
        st.session_state.project_loaded = True        
        project_papers_info = pd.read_csv(f'./data/{project_name.replace(" ","")}/papers_info.csv').dropna(subset='folds')
        folds = project_papers_info["folds"].unique()
        folds.sort()
        fold = st.selectbox("Fold",folds)
        
        #Try to load previous annotations
        if not os.path.exists(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv'):
            st.info("New user for this project")
            with open(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv',"w+") as annotation_file:
                annotation_file.write("doc_id,doc_name,label1,label2,value,comments")
        old_annotations = pd.read_csv(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv')


        #Render PDF part
        papers = project_papers_info[project_papers_info["folds"] == fold]
        base_path = f'./data/{project_name.replace(" ","")}/pdfs/'
        index = st.number_input("Document id",min_value=0,max_value=len(papers)-1,value=st.session_state.get(f"{project_name}{username}{fold}",0),step=1,disabled=True)

        doc_id = papers.iloc[index]["index"]
        pdf_path = f"{base_path}file_{str(doc_id)}"  
        with open(pdf_path) as pdf_file:
            base64_pdf = pdf_file.read()
            pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}#navpanes=0&scrollbar=0" width=100% height=700 type="application/pdf"></iframe>'
        pdf_display = st.markdown(pdf_display, unsafe_allow_html=True)

        if (old_annotations["doc_id"].isin([doc_id])).any():
            st.info("You've annotated this paper")
            labels1 = old_annotations[old_annotations["doc_id"] == doc_id]["label1"].unique()
        else:
            labels1= projects_info[projects_info["name"] == project_name]["labels1"].values[0].split(",")
        labels2 = projects_info[projects_info["name"] == project_name]["labels2"].values[0]
        if not pd.isna(labels2):
            labels2 = labels2.split(",")
        
            columns = ["label1"]
            columns.extend(labels2)
            lst_row = []
            for label in labels1:
                row = [label]
                for c in labels2:
                    if (old_annotations["doc_id"].isin([doc_id])).any():
                        old_value = old_annotations[old_annotations["doc_id"].isin([doc_id])]\
                            [(old_annotations["label1"].isin([label])) & (old_annotations["label2"].isin([c]))]["value"].values[0]
                        row.append(old_value)
                    else:
                        row.append(False)
                lst_row.append(row)
            
            annotations = pd.DataFrame(lst_row,columns=columns)
            annotations = annotations.sort_values(by=["label1"])
            annotations = annotations.set_index("label1")
            
            column_config={
                "label1": st.column_config.TextColumn("label1", default="")
            }
            for c in labels2:
                column_config[c]=st.column_config.CheckboxColumn(c,default=False)

            annotations = st.data_editor(annotations,num_rows="dynamic",column_config=column_config,use_container_width=True,hide_index=False)

            if (old_annotations["doc_id"].isin([doc_id])).any():
                text_save = "Update"
            else:
                text_save = "Save"
            
            col4,col5,col6 = st.columns(3)
            with col4:
                if index == 0:
                    disabled_previous = True
                else:
                    disabled_previous = False
                previous_button = st.button("Previous",disabled= disabled_previous)
            
            with col5:
                save_button = st.button(text_save)
            
            with col6:
                if index == len(papers)-1:
                    disabled_next = True
                else:
                    disabled_next = False
                next_button = st.button("Next",disabled= disabled_next)
                
            if save_button:
                #Remove old annotation:
                old_annotations = old_annotations[~old_annotations["doc_id"].isin([doc_id])]
                with open(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv',"w") as annotation_user_file: 
                    annotation_user_file.write("doc_id,doc_name,label1,label2,value")
                    doc_title = papers.iloc[index]["filename"]
                    for row in annotations.iterrows():
                        row_values = row[1]
                        for label2 in labels2:
                            line = f'\n{doc_id},{doc_title},{row[0]},{label2},{row_values[label2]}'
                            annotation_user_file.write(line)
                    annotation_user_file.write("\n")
                old_annotations[~old_annotations["doc_id"].isin([doc_id])].to_csv(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv',mode="a",index=False,header=False)
                st.success("Annotation saved!")
                st.rerun()


            if next_button:
                st.session_state[f"{project_name}{username}{fold}"] = index + 1
                index = index + 1
                st.rerun()
            
            if previous_button:
                st.session_state[f"{project_name}{username}{fold}"] = index - 1
                index = index + 1
                st.rerun()
        
        else:
            columns = ["label1","selected"]
            lst_row = []
            if (old_annotations["doc_id"].isin([doc_id])).any():
                for label in labels1:
                    old_value = old_annotations[old_annotations["doc_id"].isin([doc_id])][(old_annotations["label1"].isin([label]))]["selected"].values[0]
                    row = [label,old_value]
                    lst_row.append(row)
            else:
                for label in labels1:
                    row = [label,False]
                    lst_row.append(row)
            
            annotations = pd.DataFrame(lst_row,columns=columns)
            annotations = annotations.sort_values(by=["label1"])
            annotations = annotations.set_index("label1")

            column_config={
                "label1": st.column_config.TextColumn("Label", default=""),
                "selected": st.column_config.CheckboxColumn("Selected",default=False),
            }
            annotations = st.data_editor(annotations,num_rows="dynamic",column_config=column_config,use_container_width=True,hide_index=True)
            if (old_annotations["doc_id"].isin([doc_id])).any():
                text_save = "Update"
            else:
                text_save = "Save"
            
            col4,col5,col6 = st.columns(3)
            with col4:
                if index == 0:
                    disabled_previous = True
                else:
                    disabled_previous = False
                previous_button = st.button("Previous",disabled= disabled_previous)
            
            with col5:
                save_button = st.button(text_save)
            
            with col6:
                if index == len(papers)-1:
                    disabled_next = True
                else:
                    disabled_next = False
                next_button = st.button("Next",disabled= disabled_next)
            
            if save_button:
                #Remove old annotation:
                old_annotations = old_annotations[~old_annotations["doc_id"].isin([doc_id])]
                with open(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv',"w") as annotation_user_file: 
                    annotation_user_file.write("doc_id,doc_name,label1,selected")
                    doc_title = papers.iloc[index]["filename"]
                    for row in annotations.iterrows():
                        row_values = row[1]
                        line = f'\n{doc_id},{doc_title},{row[0]},{row_values["selected"]}'
                        annotation_user_file.write(line)
                    annotation_user_file.write("\n")
                old_annotations[~old_annotations["doc_id"].isin([doc_id])].to_csv(f'./data/{project_name.replace(" ","")}/annotations/{username}.csv',mode="a",index=False,header=False)
                st.success("Annotation saved")
                st.rerun()
            
            if next_button:
                st.session_state[f"{project_name}{username}{fold}"] = index + 1
                index = index + 1
                st.rerun()
            
            if previous_button:
                st.session_state[f"{project_name}{username}{fold}"] = index - 1
                index = index + 1
                st.rerun()