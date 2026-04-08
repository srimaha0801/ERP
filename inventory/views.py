from django.shortcuts import render
from .models import  Branch
from .serializers import BranchSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

