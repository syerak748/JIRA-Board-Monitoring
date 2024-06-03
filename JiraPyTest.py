from jira import JIRA
import requests
from requests.auth import HTTPBasicAuth

def jiraTestModule():#for my santushti
    jira_url = "https://evidenkshitij748.atlassian.net"
    jira_user = "kshitij.gupta.external@eviden.com"
    jira_api_token = "jiraapitoken"

    jira = JIRA(server=jira_url, basic_auth=(jira_user, jira_api_token))

    projects = jira.projects()
    for pro in projects:
        print(pro.key, pro.name)


def testAPIConnection(): #while this is true, main prog should keep running
    jira_url = 'https://evidenkshitij748.atlassian.net'
    api_endpoint = '/rest/api/3/project'  
    auth = HTTPBasicAuth('kshitij.gupta.external@eviden.com', 'ATATT3xFfGF0iavlcXQDdkh5gxr0HKtdRy9-P1_HXe4ORTxPSsjRPXeh_gVnOS73p8obMcltmWV5bm21hJF9QMkw4lSPkqlz4C1fOr-qg-7dM6mLCyvYny4wAcRkEHmXQKWIOR_YBJPovDbWWSinS0PuYvCAqHBb9GEkpg5PxURBPB9GNovvbjo=A76CD4C8')
    response = requests.get(jira_url + api_endpoint, auth=auth)
    if response.status_code == 200:
        print("Successfully connected to jira api")
        from pprint import pprint
        #pprint(response.json())
        return True
    else:
        print(f'Failed to connect to jira api: {response.status_code}')
        #print(response.text)
        return False