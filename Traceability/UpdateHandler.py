import pandas as pd
import numpy as np

from src.Traceability.Jira.JiraRequirements import JiraRequirementStore
from src.Traceability.PLM.PLMInterface import PLMInterface
from src.Traceability.Mapping import Mapping
from src.Traceability.Delta import Delta

class UpdateHandler:
    def __init__(self, jira_requirement_store: JiraRequirementStore, plm_interface: PLMInterface):
        assert not jira_requirement_store is None, 'jira_requirement_store must be of type JiraRequirementStore'
        assert isinstance(jira_requirement_store, JiraRequirementStore), 'jira_requirement_store must be of type JiraRequirementStore'
        assert not plm_interface is None, 'plm_interface must be of type PLMInterface'
        assert isinstance(plm_interface, PLMInterface), 'plm_interface must be of type PLMInterface'

        self._jira_requirement_store = jira_requirement_store
        self._plm_interface = plm_interface

    def __generate_delta__(self) -> None:
        
        source = self._plm_interface.specification_map
        current = self._jira_requirement_store.specification_map

        # Concatenate source and current mapping
        diff_mapping = pd.concat([source[['TRM_req','TRM_spec']], current[['TRM_req','TRM_spec']]],axis=0)
        
        # Remove all rows that appear more than once in the combined map
        diff_mapping = diff_mapping.groupby(['TRM_req','TRM_spec']).size().reset_index(name='count')
        diff_mapping = diff_mapping[diff_mapping['count'] == 1]

        # Extract a unique list of requirements to update
        requirements_to_update = diff_mapping['TRM_req']

        # Filter the source for all rows relating to the altered requirements
        target_mapping = source[source['TRM_req'].isin(requirements_to_update)]

        # Add any known Jira Keys from the current mapping (None where not known)
        current_jira_map = current[['TRM_req','JIRA_key']].drop_duplicates()
        target_mapping = target_mapping.merge(current_jira_map, how='left', on=['TRM_req'])
        target_mapping['JIRA_key_y'].replace({np.nan: None}, inplace=True)

        # Convert to Mapping object
        target_mapping = Mapping(
            TRM_req=target_mapping['TRM_req'].tolist(), 
            TRM_spec=target_mapping['TRM_spec'].tolist(), 
            JIRA_key=target_mapping['JIRA_key_y'].tolist())

        # Extract all items that appear in the list of changed requirements but not the incoming PLM mapping (orphans)
        orphaned_requirements = requirements_to_update[~requirements_to_update.isin(source['TRM_req'])].to_list()        

        # Store Delta object ready for processing
        self.delta = Delta(target_orphaned_requirements=orphaned_requirements, target_mapping=target_mapping)

    def __apply_delta__(self) -> None:
        self._jira_requirement_store.apply_delta(self.delta)

    def update(self):
        self._plm_interface.update_mapping()
        self.__generate_delta__()
        self.__apply_delta__()
