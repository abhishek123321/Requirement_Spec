from os import environ as env

class Config():
    JIRAUSERNAME = None
    JIRAPASSWORD = None
    JIRATOKEN = None
    JIRAURL = None
    JIRAPROXY = {}
    JIRACUSTOMFIELDSELECTION = None # Selection for duplicates. dict in form of {name:cf_id}

    ELASTICUSERNAME = None
    ELASTICPASSWORD = None
    ELASTICURL = None
    ELASTICCACHEINDEX = None
    ELASTICLOGSINDEX = None

    PLMUSERNAME = None
    PLMPASSWORD = None
    PLMSPACEURL = None
    PLMPASSPORTURL = None
    PLMCONTEXT = None
    
    def __init__(self):
        pass

class DevelopmentConfig(Config):
    JIRAUSERNAME = 
    JIRAPASSWORD = 
    JIRAURL = 
    JIRAPROXY = 

    ELASTICUSERNAME = 
    ELASTICPASSWORD = 
    ELASTICURL = 
    ELASTICCACHEINDEX = 
    ELASTICLOGSINDEX = 
	
    PLMUSERNAME = 
    PLMPASSWORD = 
    PLMSPACEURL = 
    PLMPASSPORTURL = 
    PLMCONTEXT = 

class PreProductionConfig(Config):
    JIRAUSERNAME = 
    JIRAPASSWORD = 
    JIRAURL = 
    JIRAPROXY = 

    ELASTICUSERNAME = 
    ELASTICPASSWORD = 
    ELASTICURL = 
    ELASTICCACHEINDEX = 
    ELASTICLOGSINDEX = 

    PLMUSERNAME = 
    PLMPASSWORD = 
    PLMSPACEURL = 
    PLMPASSPORTURL = 
    PLMCONTEXT = 

class ProductionConfig(Config):
    JIRAUSERNAME = 
    JIRATOKEN = 
    JIRAURL = 
    JIRAPROXY = 

    ELASTICUSERNAME = None
    ELASTICPASSWORD = None
    ELASTICURL = None
    ELASTICCACHEINDEX = None
    ELASTICLOGSINDEX = None

    PLMUSERNAME = None
    PLMPASSWORD = None
    PLMSPACEURL = None
    PLMPASSPORTURL = None
    PLMCONTEXT = None

   
def get_config():
    config_name = env['TRACEABILITYENVIRONMENT']
    if config_name:
        try:
            return eval(config_name)
        except:
            raise(Exception("Environment variable TRACEABILITYENVIRONMENT is not a valid environment"))

    raise(Exception("Environment variable TRACEABILITYENVIRONMENT is not set"))
    
