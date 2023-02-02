import pandas as pd
import numpy as np

from logging import exception
from src.Traceability.Mapping import Mapping
from src.Traceability.Delta import Delta
from src.Traceability.Elastic.ElasticInterface import ElasticInterface
from src.Traceability.Connectors.JiraConnection import JiraConnection

class JiraRequirementStore():
    def __init__(self):
        self._cache = ElasticInterface()
        self._jira_conn = JiraConnection()

    @property   
    def specification_map(self) -> Mapping :
        return self._cache.get_cache

    def flush_cache(self) -> None:
        jql_query = "project = RRP and 'Requirement Traceability' is not EMPTY"
        issue_list = self._jira_conn.get_issues(jql_query, max_results=False,fields=['Key','3DX Name','Requirement Traceability'])
        cf_fields = self._jira_conn.get_custom_field_ids(['Key','3DX Name','Requirement Traceability'])

        self._cache.flush_cache()

        for issue in issue_list:
            spec_str = getattr(issue.fields, cf_fields['Requirement Traceability'])
            trm_specs = spec_str.split(',')
            trm_req = getattr(issue.fields, cf_fields['3DX Name'])

            self._cache.update_cache(TRM_specs=trm_specs, TRM_req=trm_req, JIRA_key=issue.key)

    def apply_delta(self, delta:Delta) -> None:

        if not isinstance(delta,Delta):
            raise TypeError('delta must be a Delta object')

        target_orphaned_requirements = delta.orphaned_requirements
        target_mapping = delta.delta_map        

        for req in target_orphaned_requirements:
            self._orphan_requirement(req)

        target_mapping = self._match_trm_jira_req(target_mapping)

        unique_target_reqs = set(target_mapping['TRM_req'])    
    
        for req in unique_target_reqs:
            specifications = target_mapping.loc[target_mapping['TRM_req'] == req, 'TRM_spec'].tolist()
            jira_key = target_mapping.loc[target_mapping['TRM_req'] == req, 'JIRA_key'].iloc[0]
            self._update_requirement(req,specifications, jira_key)

    def _update_requirement(self, trm_id:str, specifications:list, issuekey:str) -> None:
        
        fields=['Key','3DX Name','Requirement Traceability']
        cf_fields = self._jira_conn.get_custom_field_ids(fields)

        issue = self._jira_conn.get_issue(issuekey, fields=fields)

        current_specs = getattr(issue.fields, cf_fields['Requirement Traceability'])
        if current_specs:
            current_specs = current_specs.split(',')
        else:
            current_specs = []

        try:
            specfications_str = ','.join(specifications)

            if set(current_specs) != set(specifications):
                self._jira_conn.update_issue_fields(issue,fields={'Requirement Traceability': specfications_str})
            
            self._cache.update_cache(TRM_specs=specifications, TRM_req=trm_id, JIRA_key=issuekey)
        except Exception as e:
            #TODO Failure logging and continue. How are we reporting failures outside of the pipeline?
            raise e

    def _orphan_requirement(self,trm_id:str) -> None:
        
        fields=['Key','Requirement Traceability']
    
        jql_query = 'project = RRP AND issuetype = Requirement AND "3DX Name" ~ "' + trm_id + '"'
        issue_list = self._jira_conn.get_issues(jql_query,fields=fields)
        assert len(issue_list) > 0, "No jira issue found for TRM id " + trm_id
        issue = issue_list[0]
        
        try:
            self._jira_conn.update_issue_fields(issue, fields={'Requirement Traceability': None})
            self._cache.delete_requirement(trm_id)
        except Exception as e:
            #TODO Failure logging and continue. How are we reporting failures outside of the pipeline?
            raise e
    
    def _match_trm_jira_req(self, target_mapping:Mapping) -> Mapping:

        # Get unique mapping
        known_mapping = self._cache.get_cache
        known_mapping = known_mapping.drop('TRM_spec',axis=1)
        known_mapping = known_mapping.drop_duplicates()

        # Update target mapping with known Jira Keys
        target_mapping = target_mapping.drop('JIRA_key',axis=1)
        target_mapping = pd.merge(target_mapping, known_mapping, 
            how='left', on='TRM_req')
        target_mapping['JIRA_key'].replace({np.nan: None}, inplace=True)

        # For blanks in mapping find Jira IDs
        unknown_trm_ids = target_mapping.loc[target_mapping['JIRA_key'].isnull(), 'TRM_req']
        unknown_trm_ids = list(set(unknown_trm_ids.tolist()))

        if len(unknown_trm_ids) > 0:
            new_mapping = self._get_jirakey_from_trmid(unknown_trm_ids)
            new_mapping = new_mapping.drop_duplicates()

            known_mapping = pd.concat([known_mapping, new_mapping])

            # Re-merge the target mapping to complete the key list
            target_mapping = target_mapping.drop('JIRA_key', axis=1)
            target_mapping = pd.merge(target_mapping, known_mapping, 
                how='left', on='TRM_req')

        target_mapping = target_mapping[target_mapping['JIRA_key'].notna()]

        return target_mapping

    def _get_jirakey_from_trmid(self, trm_ids:list) -> pd.DataFrame:

        base_jql = "Project = RRP AND ("
        current_id_count = 0
        found_issues = []
        this_jql = base_jql

        while current_id_count < len(trm_ids):
            
            if this_jql == base_jql:
                new_jql = this_jql + "'3DX Name'~'" + trm_ids[current_id_count] + "'"
            else:
                new_jql = this_jql + " OR '3DX Name'~'" + trm_ids[current_id_count] + "'"
            
            if len(new_jql) > 5999 or current_id_count == len(trm_ids)-1:
                if current_id_count == len(trm_ids)-1:
                    this_jql = new_jql
                    current_id_count = current_id_count + 1

                new_issues = self._jira_conn.get_issues(this_jql+")",fields=['Key','3DX Name'])
                
                found_issues = found_issues + new_issues

                # Reset jql
                this_jql = base_jql
            else:
                # Assign new Jql as current and add one to counter
                this_jql = new_jql
                current_id_count = current_id_count + 1
        
        cf_fields = self._jira_conn.get_custom_field_ids(['Key','3DX Name'])
        trm_reqs = []
        jira_keys = []
        for issue in found_issues:
            trm_reqs.append(getattr(issue.fields, cf_fields['3DX Name']))
            jira_keys.append(issue.key)
        
        return pd.DataFrame(data={'TRM_req':trm_reqs, 'JIRA_key':jira_keys})