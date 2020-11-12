import psycopg2

from xml.etree import ElementTree


class PipelineError(Exception):
    pass


class Pipeline:
    def __init__(self, xml, db, nlp):
        self.xml_content = xml
        self._db = db
        self._cur = self._db.cursor()
        self.metadata = {}
        self._nlp = nlp
        self._nes = None
        self._patent_id = None

    def get_metadata(self):
        doc = ElementTree.fromstring(self.xml_content)
        self.filename = doc.get('file')
        # Get doc-number
        numberElement = doc.find('bibliographic-data/application-reference/document-id/doc-number')
        self.metadata['doc_number'] = numberElement.text

        # Get year
        dateElement = doc.find('bibliographic-data/application-reference/document-id/date')
        self.metadata['year'] = dateElement.text.strip()[:4]

        # Get title
        titleElement = doc.find('bibliographic-data/invention-title')
        self.metadata['title'] = titleElement.text

        # Get abstract
        abstractElement = doc.find('abstract')
        if abstractElement:
            self.metadata['abstract'] = "".join(abstractElement.itertext())
        else:
            self.metadata['abstract'] = ""

        # Get description
        descElement = doc.find('description')
        if descElement:
            self.metadata['description'] = "".join(descElement.itertext())
        else:
            self.metadata['description'] = ""

    def save_metadata(self):
        sql = """INSERT INTO patent(title, doc_number, application_year, abstract, description, named_entities) values (%s, %s, %s, %s, %s, %s);"""
        self._cur.execute(sql, (self.metadata['title'], self.metadata['doc_number'], int(self.metadata['year']),
                          self.metadata['abstract'], self.metadata['description'], list(self._nes)))

    def run_NER(self):
        doc = self._nlp(self.metadata['abstract'])
        nes_abstract = [ent.text for ent in doc.ents]

        doc = self._nlp(self.metadata['description'])
        nes_description = [ent.text for ent in doc.ents]

        self._nes = set(nes_abstract + nes_description)

    def save_NE(self):
        sql = """UPDATE patent set named_entities = %s WHERE id = %s;"""
        self._cur.execute(sql, (list(self._nes), self._patent_id))

    def run(self):
        try:
            self.get_metadata()
            self.run_NER()
            self.save_metadata()
        except psycopg2.InterfaceError as error:
            raise error
        except psycopg2.DatabaseError as error:
            raise PipelineError("PipelineError '{}' processing {} doc_number = {}".format(error, self.filename,
                                                                                          self.metadata['doc_number']))

        # close the communication with the PostgreSQL
        self._cur.close()
