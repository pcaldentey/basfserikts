import spacy
import os

from xml.etree import ElementTree


DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')


class Pipeline:
    def __init__(self, xml):
        self.xml_content = xml
        self.metadata = {}

    def get_metadata(self):
        doc = ElementTree.fromstring(self.xml_content)
        # Get doc-number
        numberElement = doc.find('bibliographic-data/application-reference/document-id/doc-number')
        self.metadata['docn_number'] = numberElement.text

        # Get year
        dateElement = doc.find('bibliographic-data/application-reference/document-id/date')
        self.metadata['year'] = dateElement.text.strip()[:4]

        # Get title
        titleElement = doc.find('bibliographic-data/invention-title')
        self.metadata['title'] = titleElement.text

        # Get abstract
        abstractElement = doc.find('abstract')
        self.metadata['abstract'] = "".join(abstractElement.itertext())

        # Get description
        descElement = doc.find('description')
        self.metadata['description'] = "".join(descElement.itertext())

    def save_metadata(self):
        pass

    def run_NER(self):
        pass

    def save_NE(self):
        pass

    def run(self):
        metadata = self.get_metadata()
        #self.save_metadata()
        #self.run_NER()
        #self.save_NE()
