import typing as t

from elasticsearch import Elasticsearch

from src.config import get_config
class ElasticConnection():
    def __init__(self):
        conf = get_config()
        elastic_args = {
            'hosts':conf.ELASTICURL, 
            'basic_auth': (conf.ELASTICUSERNAME, conf.ELASTICPASSWORD), 
            'verify_certs': False}
        
        self._conn = Elasticsearch(**elastic_args)

# Index APIs
    def exists_index(self, index: str):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'

        try:
            resp = self._conn.indices.exists(index=index)
        except Exception:
            raise Exception

        return resp.body

    def create_index(self, 
        index: str, 
        mappings: t.Optional[t.Mapping[str, t.Any]] = None, 
        master_timeout: t.Optional[t.Union["t.Literal[-1]", "t.Literal[0]", str]] = None,
        settings: t.Optional[t.Mapping[str, t.Any]] = None,
        timeout: t.Optional[t.Union["t.Literal[-1]", "t.Literal[0]", str]] = None,
        wait_for_active_shards: t.Optional[t.Union[int, t.Union["t.Literal['all', 'index-setting']", str]]] = None):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'

        args = {'index': index}

        if mappings is not None:
            args['mappings'] = mappings
        if master_timeout is not None:
            args['master_timeout'] = master_timeout
        if settings is not None:
            args['settings'] = settings
        if timeout is not None:
            args['timeout'] = timeout
        if wait_for_active_shards is not None:
            args['wait_for_active_shards'] = wait_for_active_shards

        try:
            resp = self._conn.indices.create(**args)
        except Exception:
            raise Exception

        return resp

    def get_index(self, index: str):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'

        try:
            resp = self._conn.indices.get(index=index)
        except Exception:
            raise Exception

        if index in resp.body:
            return resp.body[index]
        else:
            return None

    def delete_index(self, index: str):
        
        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'

        try:
            resp = self._conn.indices.delete(index=index)
        except Exception:
            raise Exception

        return resp
    
# Document APIs
    def exists_document(self, index: str, id: str):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'
        assert not id is None, 'id must not be empty'
        assert isinstance(id, str), 'id must be a str'

        try:
            resp = self._conn.exists(index=index, id=id)
        except Exception:
            raise Exception

        return resp.body

    def add_document(self, 
        index: str, 
        document: t.Mapping[str, t.Any],
        id: t.Optional[str] = None):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'
        assert not document is None, 'document must not be empty'

        args = {'index': index, 'document': document}

        if id is not None:
            assert isinstance(id, str), 'id must be a str'
            args['id'] = id

        try:
            resp = self._conn.index(**args)
        except Exception:
            raise Exception

        return resp

    def get_all_documents(self, index: str) -> list:

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'

        try:
            resp = self._conn.search(index=index,scroll='1s',size=10000)
            hits = resp['hits']['hits']
            if hits:
                scroll_id = resp['_scroll_id']
                while len(resp['hits']['hits']) > 0:
                    resp = self._conn.scroll(scroll_id=scroll_id,scroll='1s')
                    hits = hits + resp['hits']['hits']

        except Exception:
            raise Exception

        return hits

    def get_document(self, index: str, id: str):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'
        assert not id is None, 'id must not be empty'
        assert isinstance(id, str), 'id must be a str'

        try:
            resp = self._conn.get(index=index, id=id)
        except Exception:
            raise Exception

        return resp.body

    def delete_document(self, index: str, id: str):

        assert not index is None, 'index must not be empty'
        assert isinstance(index, str), 'index must be a str'
        assert not id is None, 'id must not be empty'
        assert isinstance(id, str), 'id must be a str'

        try:
            resp = self._conn.delete(index=index, id=id)
        except Exception:
            raise Exception

        return resp
