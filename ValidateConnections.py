import requests

from argparse import ArgumentParser

from src.config import get_config

class ValidateConnections():
    def __init__(self, fail_immediately:bool=True):
        assert isinstance(fail_immediately, bool), 'fail_immediately MUST be a boolean'

        errs = []
        self.conf = get_config()

        try:
            print('Trying Jira Connection')
            self.validate_jira_connection()
            print('Successfully connected to Jira')
        except Exception as e:
            print('Failed Jira Connection')

            if fail_immediately:
                raise e
            else:
                errs.append(e)

        try:
            print('Trying Elastic Connection')
            self.validate_elastic_connection()
            print('Successfully connected to Elastic')
        except Exception as e:
            print('Failed Elastic Connection')

            if fail_immediately:
                raise e
            else:
                errs.append(e)

        try:
            print('Trying 3DX Connection')
            self.validate_plm_connection()
            print('Successfully connected to 3DX')
        except Exception as e:
            print('Failed 3DX Connection')

            if fail_immediately:
                raise e
            else:
                errs.append(e)

        if errs:
            raise Exception(errs)

    def validate_jira_connection(self):
        url = self.conf.JIRAURL + '/rest/api/2/serverInfo'
        try:
            if self.conf.JIRATOKEN:
                requests.get(url, 
                    headers={'Authorization': 'access_token '+self.conf.JIRATOKEN},
                    proxies = self.conf.JIRAPROXY)
            elif self.conf.JIRAUSERNAME and self.conf.JIRAPASSWORD:
                requests.get(url, 
                    auth=(self.conf.JIRAUSERNAME,self.conf.JIRAPASSWORD),
                    proxies = self.conf.JIRAPROXY)
            else:
                raise Exception("No Valid Credentials in Configuration")
        except Exception as err:
            if str(err) == "No Valid Credentials in Configuration":
                raise err
            else:
                raise Exception("Unable to connect to Jira for the current environment")

    def validate_elastic_connection(self):
        try:
            requests.get(self.conf.ELASTICURL, 
                auth=(self.conf.ELASTICUSERNAME,self.conf.ELASTICPASSWORD),
                verify=False)
        except Exception:
            raise(Exception("Unable to connect to Elastic for the current environment"))

    def validate_plm_connection(self):
        try:
            requests.get(self.conf.PLMPASSPORTURL + '/login?action=get_auth_params', 
                verify=False)
        except Exception:
            raise(Exception("Unable to connect to PLM for the current environment"))

if __name__ == '__main__': # pragma: no cover
    # Set up the Argument Parser
    parser = ArgumentParser()
    parser.add_argument("-t", "--tryall",	dest="failimmediately",	default=True, action='store_false', help="Return immediately on first failure")

    # Parse the command line arguments sent
    args = parser.parse_args()

    ValidateConnections(fail_immediately=args.failimmediately)