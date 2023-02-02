from src.Traceability.Jira.JiraRequirements import JiraRequirementStore
from src.Traceability.PLM.PLMInterface import PLMInterface
from src.Traceability.UpdateHandler import UpdateHandler
from src.ValidateConnections import ValidateConnections

def main():
    ValidateConnections()

    jira_requirement_store = JiraRequirementStore()
    plm_interface = PLMInterface()

    update_handler = UpdateHandler(jira_requirement_store,plm_interface)

    update_handler.update()

if __name__ == '__main__': # pragma: no cover
    main()