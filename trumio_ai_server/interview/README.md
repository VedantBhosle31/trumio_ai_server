# Endpoints for Resume parser
```bash
/api/resume
```

Added additional Headers
```JSON
{"Content-Disposition":"attachment; filename=resume.pdf"}
```
In the Body add a the File

# Endpoint for Interview
```bash
ws://localhost:8000/ws/chat/
```

## Send this msg to Get the Agent Running
```json

{
    "type": "topic",
    "topic": "backend",
    "subtopics": ["python", "flask"]
}
```
## Listen to onmessage event to get the Questions


## Send User Response in following format
```JSON
{
    "type": "chat",
    "message": "Message String"
}
```

# APIs



## Parse Resume
```bash
    /api/student/resume
```

```JSON
{
    'url':<url of s3 bucket>,
    'sid':<student ID>
}
```


## Get breadth,depth,recommended skills and subgraph for a student
```bash
    /api/profile/get_scores/<str:sid>
```
Note: sid is the id of the student.



## API to get the summary of github
```bash
    /api/student/github_info/<str:username>
```
Note: sid is the id of the student



## API to get the summary of codeforces
```bash
    /api/student/codeforce_info/<str:username>
```
Note: sid is the id of the student






## API to get relevant projects for a student.
```bash
    /api/student/get_rel_projects/<sid>
```
Note: sid is the id of the student



## API to create team
```bash
    /api/create
```

```JSON
{
    "sids":[<uids of the students>],
    "id":<team id>
}
```



## API to get relevant teams for a project
```bash
    /api/get_rel_teams
```

```JSON
{
    "sids":[<uids of the students>],
    "id":<team id>
}
```




## API to add a project.
```bash
    /api/project/create
```

```JSON
{
    "desc":<project description>,
    "pid":<projectID>
}
```

