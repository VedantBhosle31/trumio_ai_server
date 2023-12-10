from django.shortcuts import render
from .resume_parser import ResumeParser
from .site_extractors import github_get_projects, codeforce_get_info
from .models import store, subgraphers
import uuid
import torch
from asgiref.sync import async_to_sync
import os


from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import json



@api_view(['POST'])
def pdf_upload_view(request, *args, **kwargs):

    pdf_url = request.data['url']
    uid = request.data['sid']

    print(uid)
    # print(pdf_file)
    r =  ResumeParser(pdf_url)

    data = dict()

    resume_content = r.get_content()

    data['profile'] = json.loads(resume_content)
    data['skills'] = json.loads(r.get_skills())

    print(data['profile'])

    print(os.getcwd())

    # store.add_to_profile(uid, resume_content)

    return Response(data=data, status=status.HTTP_200_OK)
    # return Response(data=data, status=status.HTTP_201_CREATED)


def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


@api_view(['GET'])
def get_github_info(request, *args, **kwargs):

    username = kwargs.get('username')
    result = async_to_sync(github_get_projects)(username)

    return Response(data=result, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_codefore_info(request, *args, **kwargs):

    username = kwargs.get('username')

    result = codeforce_get_info(username)

    return Response(data=result, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_team(request, *args, **kwargs):

    sids = request.data['sids']
    team_id = request.data['id']
    project_id = request.data['proj_id']

    store.add_to_teams(sids, team_id, project_id)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_relevant_profile(request, *args, **kwargs):
    
    pid = kwargs['pid']

    collection = store.get_collection("projects")

    pr = collection.get(ids=[pid], include=['embeddings'])

    preferred_profiles = store.get_collection("profiles").query(query_embeddings=pr['embeddings'][0], n_results=3)

    data = dict(zip(preferred_profiles['ids'][0], preferred_projects['distances'][0]))


    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_relevant_projects(request, *args, **kwargs):
    
    sid = kwargs['sid']  
    collection = store.get_collection("profiles")

    sp = collection.get(ids=[sid], include=['embeddings'])

    preferred_projects = store.get_collection("projects").query(query_embeddings=sp['embeddings'][0], n_results=15, include=['distances'])
    
    data = dict(zip(preferred_projects['ids'][0], preferred_projects['distances'][0]))

    return Response(data=data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_relevant_projects_for_team(request, *args, **kwargs):
    
    tid = kwargs['tid']  
    collection = store.get_collection("teams")

    tp = collection.get(ids=[tid], include=['embeddings'])

    print(tp)

    preferred_projects = store.get_collection("projects").query(query_embeddings=tp['embeddings'][0], n_results=15, include=['distances'])
    
    data = dict(zip(preferred_projects['ids'][0], preferred_projects['distances'][0]))

    return Response(data=data, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_relevant_teams(request, *args, **kwargs):
        
    pid = kwargs['pid']

    collection = store.get_collection("projects")

    pr = collection.get(ids=[pid], include=['embeddings'])

    preferred_teams = store.get_collection("teams").query(query_embeddings=pr['embeddings'][0], n_results=15, where={"project_id":pid})
    
    data = dict(zip(preferred_teams['ids'][0], preferred_teams['distances'][0]))

    return Response(data=data,status=status.HTTP_200_OK)
    




@api_view(['GET'])
def get_scores(request, *args, **kwargs):

    # graphs = dict({
    #     'AI/ML':'ai.json',
    #     'backend':'backend.json',
    #     'frontend':'frontend.json'
    # })

    sid = request.data['sid']

    student_embed = store.get_collection("profiles").get(ids=[sid], include=['embeddings'])['embeddings']

    data = dict()

    print(request.data)

    for domain in request.data['domains']:

        subgraph = subgraphers[domain].get_subgraph(torch.tensor(student_embed))
        data[domain] =  subgraph

    print(data)

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_project(request, *args, **kwargs):

    proj_desc = request.data['desc']
    pid = request.data['pid']

    store.add_to_projects(pid, proj_desc)

    return Response(status=status.HTTP_200_OK)


