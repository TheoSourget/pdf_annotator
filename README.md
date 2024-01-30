# pdf_annotator

## Presentation
This tool allows to annotate PDF file with multiple users.

Once the software is installed on a local server, a user can create an annotation project by uploading the PDFs and choosing up to two initial sets of labels. While the second set of labels is fixed, the first one is not and new values can be added at any point during the labelling.

We also wanted to ease the annotation by multiple users. At the creation of the project, the owner can upload a file containing the division of the papers into different groups. This way, users can find the papers they were assigned to by selecting the right group on the annotation page.
Finally, when the annotations are downloaded from the server, a file per person is obtained allowing more data processing afterwards.

## Installation
To install the tool on a local server, use the following commands:

```
git clone https://github.com/TheoSourget/pdf_annotator.git
docker build . -t streamlit
docker run -d -v .:/app -p 8501:8501 streamlit
```
Then the tool will be available either on http://localhost:8501/ if you used it on your machine or at your server address also on the port 8501

## User guide
Soon