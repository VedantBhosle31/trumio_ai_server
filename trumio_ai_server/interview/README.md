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
    /api/students/resume
```

```JSON
{
    'url':<url of s3 bucket>,
    'sid':<student ID>
}
```

Output

```JSON
{
    "profile":{
        "Education": [{"institute":<instituteName>, "course":<courseName>, "grade":<grade>}],
    "WorkEx":[{"companyName":<companyName>, "position":<position>, "duration":<duration>, "description":<description>}],
    "Projects:[{"projectName":<projectName>, "description":<description>}],
    "Languages/Frameworks":[<lang/framework>, <lang/framework>]
    },
    "skills:{
        "<domain>":1/0
    }
}
```



## Get breadth,depth,recommended skills and subgraph for a student
```bash
    /api/students/get_scores
```
Note: sid is the id of the student.


```JSON
{  
    'sid':<sid>
    'domains:[<domain>,]
}
```


```

{
    "nodes": [
        {
            "id": "1",
            "skill": "Frontend Development Foundations"
        },
        {
            "id": "3",
            "skill": "CSS"
        },
        {
            "id": "6",
            "skill": "Responsive Design"
        },
        {
            "id": "7",
            "skill": "CSS Preprocessing"
        },
        {
            "id": "8",
            "skill": "CSS Frameworks"
        },
        {
            "id": "9",
            "skill": "JavaScript ES6+"
        },
        {
            "id": "10",
            "skill": "JavaScript Frameworks/Libraries"
        },
        {
            "id": "11",
            "skill": "React.js"
        },
        {
            "id": "12",
            "skill": "Vue.js"
        },
        {
            "id": "13",
            "skill": "Angular"
        },
        {
            "id": "17",
            "skill": "Vuex"
        },
        {
            "id": "20",
            "skill": "Webpack"
        },
        {
            "id": "29",
            "skill": "Accessibility"
        },
        {
            "id": "35",
            "skill": "Web Components"
        },
        {
            "id": "40",
            "skill": "CSS Animation"
        },
        {
            "id": "44",
            "skill": "Browser Developer Tools"
        }
    ],
    "edges": [
        {
            "source": "1",
            "target": "3"
        },
        {
            "source": "3",
            "target": "6"
        },
        {
            "source": "3",
            "target": "7"
        },
        {
            "source": "7",
            "target": "8"
        },
        {
            "source": "10",
            "target": "11"
        },
        {
            "source": "10",
            "target": "12"
        },
        {
            "source": "10",
            "target": "13"
        },
        {
            "source": "12",
            "target": "17"
        },
        {
            "source": "3",
            "target": "29"
        }
    ],
    "recommended": [
        {
            "id": "2",
            "skill": "HTML"
        },
        {
            "id": "4",
            "skill": "JavaScript"
        }
    ],
    "breadth": "1",
    "depth":"0.5",
    "proficiency": {
        "HTML": [
            "DOM Manipulation"
        ],
        "JavaScript": [
            "JavaScript ES6+",
            "JavaScript Frameworks/Libraries",
            "Webpack",
            "Package Managers",
            "Testing Frameworks",
            "Web APIs",
            "PWA",
            "Web Components",
            "Frontend Security",
            "Version Control Systems",
            "Browser Developer Tools",
            "Command Line Tools",
            "GraphQL Client-Side"
        ]
    }
}



## API to get the summary of github
```bash
    /api/students/github_info/<str:username>
```
Note: sid is the id of the student



## API to get the summary of codeforces
```bash
    /api/students/codeforce_info/<str:username>
```
Note: sid is the id of the student



## API to get relevant projects for a student.
```bash
    /api/students/get_rel_projects/<sid>
```
Note: sid is the id of the student

```JSON
{
    <id>:<score>,
    <id>:<score>
}
```



## API to create team
```bash
    /api/teams/create
```

```JSON
{
    "sids":[<uids of the students>],
    "id":<team id>,
    "proj_id":<project id>
}
```



## API to get relevant projects for a team
```bash
    /api/teams/get_relevant_projects/<teamid>
```

Response
```JSON
{
    <id>:<score>,
    <id>:<score>
}
```






## API to add a project.
```bash
    /api/projects/create
```
input
```JSON
{
    "desc":<project description>,
    "pid":<projectID>
}
```


## API to get relevant teams for a project
```bash
    /api/projects/get_rel_teams/<project id>
```

Response
```JSON
{
    <id>:<score>,
    <id>:<score>
}
```
