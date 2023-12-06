from django.shortcuts import render
from .resume_parser import ResumeParser
from .site_extractors import get_projects

from asgiref.sync import async_to_sync


from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework import status
import json

# from .models import PDFDocument
# from .serializers import PDFDocumentSerializer

@api_view(['POST'])
@parser_classes([FileUploadParser])
def pdf_upload_view(request, *args, **kwargs):
    pdf_file = request.data['file']
    r =  ResumeParser(pdf_file)

    data = dict()

    data['profile'] = json.loads(r.get_content())
    data['skills'] = json.loads(r.get_skills())
    
    return Response(data=data, status=status.HTTP_201_CREATED)



def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):

    return render(request, "chat/room.html", {"room_name": room_name})


@api_view(['GET'])
def get_github_info(request, *args, **kwargs):

    username = kwargs.get('username')

    result = async_to_sync(get_projects)(username)

    return Response(data=result, status=status.HTTP_200_OK)










