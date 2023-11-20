import streamlit as st

st.set_page_config(
    page_title="PDF Annotator",
    page_icon="📄",
)

st.title('Welcome to PDF Annotator! 👋')
st.write("PDF annotator is a tool to annotate collection of pdf")
st.markdown('---')


st.subheader("Create a project")
st.write("In this module, create your project by importing your list of pdf and choose a name")
st.markdown('---')
st.subheader("Label a project")
st.write("In this module, load a project and labelize the list of pdf. The annotation are linked to an username so it can be loaded for change or completion later")
st.markdown('---')
st.subheader("Extract labels")
st.write("In this module, download all the annotations made by users. You'll get a zip archive containing a csv file per user")


