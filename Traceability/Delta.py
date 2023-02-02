import pandas as pd

from src.Traceability.Mapping import Mapping

class Delta:
    def __init__(self, target_orphaned_requirements:(list,tuple), target_mapping:Mapping):
        assert not target_orphaned_requirements is None, 'target_orphaned_requirements must be of type list or tuple'
        assert isinstance(target_orphaned_requirements, (list,tuple)), 'target_orphaned_requirements must be a list or tuple'
        assert not target_mapping is None, 'target_mapping must be an instance of Mapping class'
        assert isinstance(target_mapping, pd.DataFrame), 'target_mapping must be an instance of Mapping class'

        # Compare against mappings Column lists
        test_map = Mapping([], [], [])
        assert set(test_map.columns) == set(target_mapping.columns), 'target_mapping must match Mapping columns'

        self.target_orphaned_requirements = list(set(target_orphaned_requirements))
        self.target_mapping = target_mapping
    
    @property
    def orphaned_requirements(self) -> list:
        return self.target_orphaned_requirements
    
    @property
    def delta_map(self) -> Mapping:
        return self.target_mapping

