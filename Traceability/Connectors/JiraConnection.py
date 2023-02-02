from jira import JIRA, JIRAError
from jira.resources import Issue
from time import sleep
from collections import defaultdict

from src.config import get_config

class JiraConnection:
    def __init__(self):
        self.conf = get_config()
        jira_args = {'server':self.conf.JIRAURL, 'proxies':self.conf.JIRAPROXY}
        if self.conf.JIRATOKEN:
            jira_args['token_auth'] = self.conf.JIRATOKEN
        elif self.conf.JIRAUSERNAME and self.conf.JIRAPASSWORD:
            jira_args['basic_auth'] = (self.conf.JIRAUSERNAME, self.conf.JIRAPASSWORD)
        else:
            raise(Exception("No Valid Credentials in Configuration"))

        self._conn = JIRA(**jira_args)
        self._cf_name_map = None

    @property
    def _field_mappings(self) -> dict:
        if self._cf_name_map:
            return self._cf_name_map
        else:
            self._cf_name_map = self._get_field_ids()
            return self._cf_name_map

    def get_issues(self,jql:str,fields:list=None,max_results:int=None) -> Issue:
        
        if not isinstance(jql, str):
            raise TypeError("JQL search must be a string")

        if fields:
            if not isinstance(fields, list):
                raise TypeError("fields must be a list")
            if not all(map(lambda x: isinstance(x, str), fields)):
                raise TypeError("fields must be a list of strings")
            fields = self.get_custom_field_ids(fields)
            fields = list(fields.values())

        if max_results:
            if not isinstance(max_results,int):
                raise TypeError("max_results must be int")
        else:
            max_results = False

        last_wait_time = 1
        wait_time = 2
        while True:
            try:
                return self._conn.search_issues(jql,fields=fields,maxResults=max_results)
            except JIRAError as err:
                if err.status_code == 429:
                    # logging.warn("Request was rate limited. Waiting " + str(wait_time) + " sec before retry")
                    sleep(wait_time)
                    new_wait_time = wait_time + last_wait_time
                    last_wait_time = wait_time
                    wait_time = new_wait_time
                else:
                    raise
    
    def get_issue(self, issuekey:str, fields:list=None) -> Issue:
        
        if not isinstance(issuekey, str):
            raise TypeError("issuekey must be string")

        if fields:
            if not isinstance(fields, list):
                raise TypeError("fields must be a list")
            if not all(map(lambda x: isinstance(x, str), fields)):
                raise TypeError("fields must be a list of strings")
            fields = self.get_custom_field_ids(fields)
            fields = list(fields.values())

        last_wait_time = 1
        wait_time = 2
        while True:
            try:
                return self._conn.issue(id=issuekey, fields=fields)
            except JIRAError as err:
                if err.status_code == 429:
                    # logging.warn("Request was rate limited. Waiting " + str(wait_time) + " sec before retry")
                    sleep(wait_time)
                    new_wait_time = wait_time + last_wait_time
                    last_wait_time = wait_time
                    wait_time = new_wait_time
                else:
                    raise err
 
    def update_issue_fields(self, issue:Issue, fields:dict) -> None:

        if not callable(getattr(issue,'update',None)):
            raise TypeError("issue must be a valid Jira Issue Object")
        
        if not isinstance(fields, dict):
            raise TypeError("fields must be a dictionary of format fieldname:value")
        
        cf_ids = self.get_custom_field_ids(list(fields.keys()))

        field_updates = {cf_ids[str(update)]: fields[update] for update in fields.keys()}
        
        last_wait_time = 1
        wait_time = 2
        rate_limited = True
        while rate_limited == True:
            try:
                issue.update(fields=field_updates)
                rate_limited = False
            except JIRAError as err:
                if err.status_code == 429:
                    # logging.warn("Request was rate limited. Waiting " + str(wait_time) + " sec before retry")
                    sleep(wait_time)
                    new_wait_time = wait_time + last_wait_time
                    last_wait_time = wait_time
                    wait_time = new_wait_time
                else:
                    raise err
    
    def get_custom_field_ids(self,fields:list) -> dict:
        
        assert isinstance(fields,list), "fields parameter must be of type list"
        assert len(fields) > 0, "fields can not be zero length"

        found_ids = dict((key,self._field_mappings[key]) for key in fields if key in self._field_mappings)
        
        if len(found_ids) == 0:
            missing_fields = fields
        else:
            missing_fields = list(set(fields)-set(list(found_ids.keys())))
        
        assert len(missing_fields) == 0, "The field(s) named '" + "','".join(missing_fields) + "' do not exist in this Jira Instance within users permissions"

        repeated_fields = dict()
        for key in found_ids.keys():
            if len(found_ids[key]) > 1:
                repeated_fields[key] = found_ids[key]
        
        assert len(repeated_fields) == 0, """There are multiple fields in this jira instance with some of your requested field names.
            Please outline which one you wish to use in the config file.\n\n Duplicate keys: \n""" + str(repeated_fields)

        found_ids = dict((key,found_ids[key][0]) for key in found_ids.keys())

        return found_ids
    
    def _get_field_ids(self) -> dict:
        all_fields = self._conn.fields()
        cf_map = defaultdict()
        for field in all_fields:
            if field['name'] in cf_map.keys():
                cf_map[field['name']].append(field['id'])
            else:
                cf_map[field['name']] = list([field['id']])

        # Filter any duplicate keys from config
        custom_field_selection = self.conf.JIRACUSTOMFIELDSELECTION
        if custom_field_selection:
            for field in custom_field_selection.keys():
                if field in cf_map.keys():
                    assert custom_field_selection[field] in cf_map[field], "Custom field " + \
                        custom_field_selection[field] + \
                        " defined in config is not valid on this jira instance for field name '" + \
                        field + "'\n\n Valid options:\n" + str(cf_map[field])
                    cf_map[field] = [custom_field_selection[field]]

        return cf_map