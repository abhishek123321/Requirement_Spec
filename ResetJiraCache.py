from src.Traceability.Jira.JiraRequirements import JiraRequirementStore

def main():

    j = JiraRequirementStore()

    j.flush_cache()

if __name__ == '__main__': # pragma: no cover
    main()