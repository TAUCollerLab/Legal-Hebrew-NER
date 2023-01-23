import os
import docx2txt  # could also use textract(process) method but return type is byte-coded.
import json


def iter_word_documents(directory: str) -> str:

    """
    function that returns a generator object that read each doc/docx document at a time
    and returns it as a string.
    """
    for root, dirs, files in os.walk(directory):
        for fname in filter(lambda file: file.endswith('.docx'), files):
            document = docx2txt.process(os.path.join(root, fname))  # process method returns str type
            yield document


#  The splitting criteria based only on few examples Ariel sent and will not stay like it( based on "מעבר").

gen_of_docs = iter_word_documents('verdicts_documents')
list_of_paragraphs = []

for doc in gen_of_docs:
    docs_paragraphs = doc.split('=========================== מעבר =========================')
    list_of_paragraphs = list_of_paragraphs + docs_paragraphs

#  Creating json file for the paragraphs that should be tagged
with open('json_verdict_examples.json', 'w') as output_file:  # dumps method writes as json string first
    #  dict([(k, v) for k, v in enumerate(list_of_paragraphs)])
    output_file.write(json.dumps([{"id": k, "content": v} for k, v in enumerate(list_of_paragraphs)]))

