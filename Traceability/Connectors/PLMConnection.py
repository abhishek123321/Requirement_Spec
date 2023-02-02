import json

from requests import Session
import pandas as pd

from src.config import get_config

# Disable warnings as not verifying ssl during requests
import urllib3
urllib3.disable_warnings()

class PLMConnection:

    def __init__(self):

        conf = get_config()       

        self.space_url = conf.PLMSPACEURL
        self.passport_url = conf.PLMPASSPORTURL
        self.headers = conf.PLMCONTEXT

        self.RESTSession = Session()

        try:
            url = self.passport_url +'/login?action=get_auth_params'
            response = self.RESTSession.get(url, verify=False)
            data = response.json()

            url = self.passport_url + '/login'
            params = {'lt': data['lt'], 'username': conf.PLMUSERNAME, 'password': conf.PLMPASSWORD}
            response = self.RESTSession.post(url, params=params, verify=False)        

            url = self.space_url + '/resources/v1/application/CSRF'
            response = self.RESTSession.get(url, headers=self.headers, verify=False)
            data = response.json()
            self.ENO_CSRF_TOKEN = data['csrf']['value']

        except Exception:
            raise Exception

    def get_related_object(self, type, name, rev, rel_type, rel_obj_type):

        assert not type is None, 'type must not be empty'
        assert isinstance(type, str), 'type must be a str'
        assert not name is None, 'name must not be empty'
        assert isinstance(name, str), 'name must be a str'
        assert not rev is None, 'rev must not be empty'
        assert isinstance(rev, str), 'rev must be a str'
        assert not rel_type is None, 'rel_type must not be empty'
        assert isinstance(rel_type, str), 'rel_type must be a str'
        assert not rel_obj_type is None, 'rel_obj_type must not be empty'
        assert isinstance(rel_obj_type, str), 'rel_obj_type must be a str'

        url = self.space_url + '/resources/StructureDataModeler/StructureData'
        headers = self.headers
        headers['ENO_CSRF_TOKEN'] = self.ENO_CSRF_TOKEN
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        body = json.dumps({
            "Type": type,
            "Name": name,
            "Revision": rev,
            "Level": "0",
            "ObjectAttrList": "",
            "ObjectRelList": "",
            "RelAttrList": "",
            "RootNodeAttrList": "",
            "RelNameList": rel_type,
            "RelObjTypeList": rel_obj_type,
            "PartLineageInformation": "No"})

        try:
            response = self.RESTSession.post(url, headers=self.headers, data=body, verify=False)
        except Exception:
            raise Exception

        data = response.json()

        return data

    def get_all_requirement_sepecifications(self):

        url = self.space_url + '/resources/v1/modeler/dsreq/dsreq:RequirementSpecification'
        try:
            response = self.RESTSession.get(url, headers=self.headers, verify=False)
        except Exception:
            raise Exception
            
        data = response.json(strict=False)
        data = pd.json_normalize(data, record_path=['member'])
        data = data.drop(data[data.state == 'Obsolete'].index)
        data = data.drop(data[data.type != 'SSA Requirement Specification'].index)      

        return data

    def get_all_objects_of_type(self, type, name_pattern='*', where_clause='', object_select=''):

        assert not type is None, 'type must not be empty'
        assert isinstance(type, str), 'type must be a str'
        assert not name_pattern is None, 'name_pattern must not be empty'
        assert isinstance(name_pattern, str), 'name_pattern must be a str'
        assert not where_clause is None, 'where_clause must not be empty'
        assert isinstance(where_clause, str), 'where_clause must be a str'
        assert not object_select is None, 'object_select must not be empty'
        assert isinstance(object_select, str), 'object_select must be a str'

        url = self.space_url + '/resources/ADKWebservicesModeler/Objects'

        headers = self.headers
        headers['ENO_CSRF_TOKEN'] = self.ENO_CSRF_TOKEN
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        body = json.dumps({
            "Type_Pattern": type,
            "Name_Pattern": name_pattern,
            "Revision_Pattern": "",
            "Owner_Pattern": "",
            "Vault_Pattern": "",
            "Object_Where": where_clause,
            "Expand_Type": "",
            "Object_Selects": object_select})

        try:
            response = self.RESTSession.post(url, headers=self.headers, data=body, verify=False)
        except Exception:
            raise Exception

        data = response.json()

        return data