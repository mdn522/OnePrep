from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from questions.api.api_v1 import router as questions_router
from users.api.api_v1 import router as users_router

from ninja import NinjaAPI

# app_name = 'api'

api_v1 = NinjaAPI(version='1.0.0', urls_namespace='api_v1')


# @api.get('/hello')
# def hello(request):
#     return {'message': 'Hello from V1'}
#
#
# @api.get("/add")
# def add(request, a: int, b: int):
#     return {"result": a + b}


api_v1.add_router("/questions/", questions_router)
api_v1.add_router("/users/", users_router)
# Exam

urlpatterns = [
    path('v1/', api_v1.urls, name='api_v1'),
]
