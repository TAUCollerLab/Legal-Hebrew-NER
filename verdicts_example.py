import configparser
import os
import docx2txt
# import textract
# we will use configparser to work with out configuration ini file for requests and data location

config = configparser.ConfigParser()
config.read('conf.ini')

def iter_word_documents(directory: str) -> str:
    """
    created a generator object that read each doc/docx document at a time and converts to string
    """
    for root, dirs, files in os.walk(directory):
        for fname in filter(lambda fname: fname.endswith('.docx'), files):
            document = docx2txt.process(os.path.join(root, fname))

    yield document