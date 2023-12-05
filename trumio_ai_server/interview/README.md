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

