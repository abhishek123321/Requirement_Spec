from src.Traceability.Connectors.PLMConnection import PLMConnection
from src.Traceability.Mapping import Mapping

class PLMInterface():
    def __init__(self):
        self._cache = {}
        self._plm_conn = PLMConnection()

    @property
    def specification_map(self) -> Mapping: 

        req_list = self._cache.get('Requirements',[])

        flat_list = [item for sublist in req_list for item in sublist]
        reqspecs = [item[0] for item in flat_list]
        reqs = [item[1] for item in flat_list]

        mapping = Mapping(TRM_req=reqs, TRM_spec=reqspecs)

        return mapping

    def update_mapping(self):
        self._get_requirement_specfications()
        self._get_requirements_for_requirement_specfications()

    def _get_requirement_specfications(self):

        data = self._plm_conn.get_all_objects_of_type(
            type='iPLMSSARequirementSpecification',
            where_clause='current==InWork OR current==Frozen OR current==Private OR current==Released')
        self._cache['RequirementSpecificaitons'] = data

    def _get_requirements_for_requirement_specfications(self):

        reqspecs = self._cache['RequirementSpecificaitons']

        mapping_list = []

        for reqspec in reqspecs:            
            data = self._plm_conn.get_related_object(
                type='iPLMSSARequirementSpecification',
                name=reqspec['name'],
                rev=reqspec['revision'],
                rel_type='Specification Structure',
                rel_obj_type='iPLMSSARequirement,Chapter'
            )

            if data[1:]:
                mapping_list.append([[reqspec['name'], x['name']] for x in data[1:] if x['type'] == 'iPLMSSARequirement'])

        self._cache['Requirements'] = mapping_list