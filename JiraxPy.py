from jira import JIRA
from JiraPyTest import testAPIConnection
import logging
import time
from subprocess import run
import os
import sys
import signal

keep_running = True
jira_email = "kshitij.gupta.external@eviden.com"
jira_api_token = "jiraapitoken"
jira = JIRA(server="https://evidenkshitij748.atlassian.net", basic_auth=(jira_email, jira_api_token))
projectID = 'TES748'
JQLquery = f"project = '{projectID}' AND status = 'To Do'"
JQLQueryComments = f"project = '{projectID}'"
lastSeenComments = {} #global var containing prev comments timestamps
logfile = 'commentLogs.txt'

#new_issue = jira.create_issue(project='KAN', summary='New issue from jira-python',description='Look into this one', issuetype={'name': 'Task'})
#issue = jira.issue('KAN-1')

def getBoardIssues(jira, jql): #get boards issues
    issues = jira.search_issues(jql)
    return {issue.key : issue for issue in issues}

def downloadFiles(jira, file, dir = 'downloads'): #download file and return their path
    if not os.path.exists(dir):
        os.makedirs(dir)
    filePath = os.path.join(dir, file.filename)

    file_content = jira._session.get(file.content).content #gets as binary file
    with open(filePath, 'wb') as file: #converting binary to actual cnt
        file.write(file_content)
    
    return filePath
    
def monitorBoard(jira, jql, prevIssues): #checks board for new issues
    currentIssues = getBoardIssues(jira, jql)
    currentAllIssues = getBoardIssues(jira, JQLQueryComments)
    #Delete all tasks in previssues which are not in backlog anymore,i.e, moved into a different status
    prevIssues = {key: prevIssues[key] for key in prevIssues.keys() if key in currentIssues.keys()}
    newIssues = set(currentIssues)-set(prevIssues)
    i = 0
    for issue in newIssues:
        print(f"Found new issue added : {issue}")
        i += 1
        handleNewIssue(jira, currentIssues[issue])
    if i == 0:
        print(f"Found no new issues : {newIssues}")
    
    detectNewComments(jira, currentAllIssues)

    return currentIssues


def handleNewIssue(jira, issue): #downloads all files and triggers external script
    files = issue.fields.attachment
    downloadFileLocations = []
    for file in files:
        filePath = downloadFiles(jira, file)
        downloadFileLocations.append(filePath)
    externalArgs = ['python3','testExternal.py']+downloadFileLocations
    run(externalArgs)     

def detectNewComments(jira, issues):#compares the last commenttimestamp in every issue
    global lastSeenComments
    i = 0
    for issueKey, issue in issues.items():
        try:
            comments = jira.comments(issue)
            prevCommentTime = lastSeenComments.get(issueKey)
            
            for comment in comments:
                commentTime = comment.created
                if not prevCommentTime or commentTime>prevCommentTime:
                    i += 1
                    print(f"New comment detected on {issueKey} and logged")
                    with open(logfile, 'a') as f:
                        f.write(f"{issueKey}({commentTime}) by {comment.author} : {comment.body} \n")
                    lastSeenComments[issueKey] = commentTime
            
        except Exception as e:
            print(f"Error fetching comments for {issueKey} : {e}")
    if i == 0:
        print("No new comment detected")

#global
prevTasksScrum = getBoardIssues(jira, JQLquery)
prevTasksKanban = getBoardIssues(jira, JQLquery)


def mainfn(): #the main function
    global prevTasksKanban, prevTasksScrum
    boardType = 'Kanban'
    
    
    if boardType == 'Scrum':
        prevTasksScrum = monitorBoard(jira, JQLquery, prevTasksScrum)
        return prevTasksScrum
        '''time.sleep(45)
        currentTasksScrum = monitorBoard(jira, JQLquery, prevTasksScrum)# TESTER'''
    elif boardType == 'Kanban':
        prevTasksKanban = monitorBoard(jira, JQLquery, prevTasksKanban)
        '''time.sleep(45)
        currentTasksScrum = monitorBoard(jira, JQLquery, prevTasksScrum)# TESTER'''
        return prevTasksKanban
    else:
        raise ValueError("Invalid Board Type")
    

def killSwitch(sig, frame):#kill switch and will delete all contents from log... can be removed as per convenience
    global keep_running
    print("Kill Switch Activated : Shutting Down")
    open(logfile, 'w').close()
    keep_running = False

#schedule.every(20).seconds.do(mainfn) #schedule a function call of mainfn every 5 minutes

def runProg():#run the main function and incorporates the kill switch
    global keep_running
    signal.signal(signal.SIGINT, killSwitch)
    signal.signal(signal.SIGTERM, killSwitch)

    try:
        start = time.time()
        while testAPIConnection and keep_running:#main loop will run mainfn
            mainfn()
            time.sleep(45) #5 min checks : 300
            checktime = time.time()
            print(f"TimeElapsed = {checktime-start} seconds")
    except Exception as e:
        print(f"Error -> {e}")
        keep_running = False
    
    print("Shutdown Complete")

if __name__ == "__main__":#in case a terminal run
    print('Press Control + C to kill the program')
    runProg()


#detect additional/new comments in new/old issues
