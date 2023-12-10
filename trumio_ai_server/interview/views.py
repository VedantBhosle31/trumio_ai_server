import os
import json
import uuid

import torch
from asgiref.sync import async_to_sync
from django.shortcuts import render
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import store, subgraphers
from .resume_parser import ResumeParser
from .site_extractors import github_get_projects, codeforce_get_info


@api_view(['POST'])
def pdf_upload_view(request, *args, **kwargs):
    """
    Upload a PDF file and parse its content.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing parsed data or error message
    """

    try:

        pdf_url = request.data['url']
        uid = request.data['sid']
        r =  ResumeParser(pdf_url)

        data = dict()

        resume_content = r.get_content()

        data['profile'] = json.loads(resume_content)
        data['skills'] = json.loads(r.get_skills())

        store.add_to_profile(uid, resume_content)


        return Response(data=data, status=status.HTTP_200_OK)


    except KeyError as e:
        return Response(data=dict({"error":f"Missing key : {str(e)}"}), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def index(request):
    """
    Render the index page.

    Parameters:
    - request: Django request object

    Returns:
    - Response: Rendered HTML page
    """
    return render(request, "chat/index.html")


def room(request, room_name):
    """
    Render the chat room.

    Parameters:
    - request: Django request object
    - room_name: Name of the chat room

    Returns:
    - Response: Rendered HTML page with the specified chat room
    """
    return render(request, "chat/room.html", {"room_name": room_name})


@api_view(['GET'])
def get_github_info(request, *args, **kwargs):
    """
    Get GitHub project information for a given username.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing GitHub project information
    """

    username = kwargs.get('username')
    result = async_to_sync(github_get_projects)(username)

    return Response(data=result, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_codefore_info(request, *args, **kwargs):
    """
    Get Codeforces information for a given username.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing Codeforces information
    """

    try:
        username = kwargs.get('username')

        if not username:
            return Response({'error': 'Missing username parameter'}, status=status.HTTP_400_BAD_REQUEST)

        result = codeforce_get_info(username)

        return Response(data=result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def create_team(request, *args, **kwargs):
    """
    Create a team with the specified members, team ID, and project ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: HTTP response indicating success or failure
    """

    try:
        sids = request.data['sids']
        team_id = request.data['id']
        project_id = request.data['proj_id']

        store.add_to_teams(sids, team_id, project_id)

        return Response(status=status.HTTP_200_OK)

    except KeyError as e:
        return Response(data=dict({"error":f"Missing key : {str(e)}"}), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
def get_relevant_profile(request, *args, **kwargs):
    """
    Get relevant profiles for a given project ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing relevant profile information
    """
    
    try:
        pid = kwargs['pid']

        if not pid:
            return Response({'error': 'Missing project id parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        collection = store.get_collection("projects")

        pr = collection.get(ids=[pid], include=['embeddings'])

        if len(pr['embeddings'])==0:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


        preferred_profiles = store.get_collection("profiles").query(query_embeddings=pr['embeddings'][0], n_results=3)

        data = dict(zip(preferred_profiles['ids'][0], preferred_projects['distances'][0]))

        return Response(data=data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
def get_relevant_projects(request, *args, **kwargs):
    """
    Get relevant projects for a given profile ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing relevant project information
    """
    try:
        sid = kwargs['sid']  

        if not sid:
            return Response({'error': 'Missing sid parameter'}, status=status.HTTP_400_BAD_REQUEST)

        collection = store.get_collection("profiles")

        sp = collection.get(ids=[sid], include=['embeddings'])

        if len(sp['embeddings'])==0:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        preferred_projects = store.get_collection("projects").query(query_embeddings=sp['embeddings'][0], n_results=15, include=['distances'])
        
        data = dict(zip(preferred_projects['ids'][0], preferred_projects['distances'][0]))

        return Response(data=data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
def get_relevant_projects_for_team(request, *args, **kwargs):
    """
    Get relevant projects for a given team ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing relevant project information
    """
    try:
        tid = kwargs['tid']  

        if not tid:
            return Response({'error': 'Missing team id parameter'}, status=status.HTTP_400_BAD_REQUEST)

        collection = store.get_collection("teams")

        tp = collection.get(ids=[tid], include=['embeddings'])

        if len(tp['embeddings'])==0:
            return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

        preferred_projects = store.get_collection("projects").query(query_embeddings=tp['embeddings'][0], n_results=15, include=['distances'])
        data = dict(zip(preferred_projects['ids'][0], preferred_projects['distances'][0]))

        return Response(data=data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
def get_relevant_teams(request, *args, **kwargs):
    """
    Get relevant teams for a given project ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing relevant team information
    """    
    try:
        pid = kwargs['pid']
        
        if not pid:
            return Response({'error': 'Missing project id parameter'}, status=status.HTTP_400_BAD_REQUEST)

        collection = store.get_collection("projects")

        pr = collection.get(ids=[pid], include=['embeddings'])

        if len(pr['embeddings'])==0:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        preferred_teams = store.get_collection("teams").query(query_embeddings=pr['embeddings'][0], n_results=15, where={"project_id":pid})
        data = dict(zip(preferred_teams['ids'][0], preferred_teams['distances'][0]))

        return Response(data=data,status=status.HTTP_200_OK)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    




@api_view(['POST'])
def get_scores(request, *args, **kwargs):
    """
    Get proficiency scores for a student in various domains.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: JSON response containing proficiency scores
    """
    try:
        sid = request.data['sid']

        student_embed = store.get_collection("profiles").get(ids=[sid], include=['embeddings'])['embeddings']

        
        if not student_embed:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


        data = dict()

        for domain in request.data['domains']:
            subgraph = subgraphers[domain].get_subgraph(torch.tensor(student_embed))
            data[domain] =  subgraph


        return Response(data=data, status=status.HTTP_200_OK)

    except KeyError as e:
        return Response(data=dict({"error":f"Missing key : {str(e)}"}), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def create_project(request, *args, **kwargs):
    """
    Create a project with the specified project description and ID.

    Parameters:
    - request: Django request object
    - args: Additional positional arguments
    - kwargs: Additional keyword arguments

    Returns:
    - Response: HTTP response indicating success or failure
    """
    try:
        proj_desc = request.data['desc']
        pid = request.data['pid']

        store.add_to_projects(pid, proj_desc)

        return Response(status=status.HTTP_200_OK)

    except KeyError as e:
        return Response(data=dict({"error":f"Missing key : {str(e)}"}), status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(data=dict({'error': f'Something went wrong: {str(e)}'}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



