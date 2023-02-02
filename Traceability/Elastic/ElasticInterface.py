import pandas as pd

from json import loads, dumps

from src.Traceability.Connectors.ElasticConnection import ElasticConnection
from src.Traceability.Mapping import Mapping

from src.config import get_config

class ElasticInterface():
    def __init__(self):
        # Instatiate connection
        self.elastic = ElasticConnection()
        self.conf = get_config()

    @property
    def get_cache(self) -> Mapping:
        try:
            trm_req = []
            trm_spec = []
            jira_key = []

            for elastic_doc_response in self.elastic.get_all_documents(index=self.conf.ELASTICCACHEINDEX):
                if '_source' in elastic_doc_response:
                    elastic_body = elastic_doc_response['_source']
                    doc = elastic_doc_response['_id']

                    new_trm_req = [doc] * len(elastic_body['TRM_spec'])
                    trm_req = trm_req + new_trm_req

                    trm_spec = trm_spec + elastic_body['TRM_spec']

                    new_jira_key = [elastic_body['JIRA_key']] * len(elastic_body['TRM_spec'])
                    jira_key = jira_key + new_jira_key

            elastic_cache = Mapping(
                TRM_req=trm_req,
                TRM_spec=trm_spec,
                JIRA_key=jira_key)

            return elastic_cache
        except Exception as e:
            raise e

    def update_cache(self, TRM_specs:(list,tuple), TRM_req:str, JIRA_key:str) -> bool:
        assert not TRM_specs is None, 'TRM_specs must not be empty'
        assert isinstance(TRM_specs, (list,tuple)), 'TRM_specs must be a list or tuple'
        assert not TRM_req is None, 'TRM_req must not be empty'
        assert isinstance(TRM_req, str), 'TRM_req must be a string'
        assert not JIRA_key is None, 'JIRA_key must not be empty'
        assert isinstance(JIRA_key, str), 'JIRA_key must be a string'

        try:
            if self.elastic.add_document(index=self.conf.ELASTICCACHEINDEX, id=TRM_req, document={'JIRA_key':JIRA_key, 'TRM_spec':list(TRM_specs)}):
                return True
            else:
                return False
        except:
            return False

    def delete_requirement(self, TRM_req:str):
        assert not TRM_req is None, 'TRM_req must not be empty'
        assert isinstance(TRM_req, str), 'TRM_req must be a string'

        try:
            if self.elastic.delete_document(index=self.conf.ELASTICCACHEINDEX, id=TRM_req):
                return True
            else:
                return False
        except Exception as e:
            raise e

    def flush_cache(self) -> None:
        for elastic_doc_response in self.elastic.get_all_documents(index=self.conf.ELASTICCACHEINDEX):
            try:
                doc = elastic_doc_response['_id']
                self.delete_requirement(TRM_req=doc)
            except Exception as e:
                raise e