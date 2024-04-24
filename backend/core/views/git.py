from rest_framework.response import Response
from rest_framework.views import APIView
import subprocess
import requests 

class GitAPIView(APIView):
    def get(self, request):
        #version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
        #request on https://api.github.com/repos/linea-it/pzserver_app/releases/latest
        project = 'pzserver_app'
        response = requests.get(f"https://api.github.com/repos/linea-it/{project}/releases/latest")
        data = response.json() 
        return Response({"version": data['name']})
    




