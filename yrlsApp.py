from django.urls import path
# from mainApp import views
from .views import *

urlpatterns = [

    path("specification/", SpecificationOptions.as_view()),
    path('makecombination', MakeCombination.as_view()),
    path('addproduct', AddProduct.as_view()),
    path('updateproduct', UpdateProduct.as_view()),
    path('uploadmedia', UploadMedia.as_view()),
    path('getmedia', GetMedia.as_view()),
    path('getsetting/<str:name>', GetSetting.as_view()),
    path('savesettings', SaveSetting.as_view()),
    path('deleteproduct', DeleteProduct.as_view()),

]
