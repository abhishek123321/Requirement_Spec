import pandas as pd

class Mapping(pd.DataFrame):

    def __init__(self, TRM_req:list, TRM_spec:list, JIRA_key:list=None):
        assert isinstance(TRM_req, (list,tuple)), 'TRM_req must be of type list or tuple'
        assert isinstance(TRM_spec, (list,tuple)), 'TRM_spec must be of type list or tuple'
        assert len(TRM_req)==len(TRM_spec), 'TRM_req and TRM_spec must be the same size'

        if JIRA_key:
            assert isinstance(JIRA_key, (list,tuple)), 'JIRA_key must be of type list or tuple'

        super(Mapping, self).__init__(data={'TRM_req':TRM_req, 'TRM_spec':TRM_spec, 'JIRA_key':JIRA_key})