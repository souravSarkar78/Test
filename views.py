from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# from django.db.models import Q
from mainApp.models import *
from django.core.files import File
from django.conf import settings
from decimal import *
# from .models import *
import datetime
from PIL import Image
from io import BytesIO
import json
import itertools
import glob
import uuid
from rest_framework.permissions import IsAuthenticated
from intriosBackend.CustomPermissions import IsSuperUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.storage import default_storage
from intriosBackend import database


JWT = JWTAuthentication()


# Create your views here.

# Database collections 
Products = database.Products
AppSetting = database.AppSetting

current_time = datetime.datetime.now()
current_time = current_time.strftime("%d/%m/%Y %H:%M:%S")

def compress_image(image, size=(1000, 1000), format="webp"):
    img = Image.open(image)
    if img.mode in ("RGBA", "P"):
        img = img.convert('RGB')
    w, h = img.size
    if w > size[0] or h > size[1]:
        img.thumbnail(size)
    thumb_io = BytesIO()
    img_name = image.name
    splitted = img_name.rsplit('.', 1)  # split only in two parts
    # im_format = 'JPEG'
    # img.save(thumb_io, im_format, quality=70)
    # thumbnail = File(thumb_io, name=splitted[0]+'.jpg')
    im_format = format
    img.save(thumb_io, im_format)
    thumbnail = File(thumb_io, name=splitted[0]+'.'+format)
    return thumbnail

def rand_slug():
    return str(uuid.uuid4()).replace('-','')


class MakeCombination(APIView):
    permission_classes = (IsSuperUser, )
    def post(self, request):
        arr = request.data
        # print(arr)
        return Response(list(itertools.product(*arr)), status=status.HTTP_200_OK)

        
    
class SpecificationOptions(APIView):
    def get(self, request):
        options = Specification_Type.objects.all()

        data = [option.product_specification_type for option in options]

        return Response(data, status = status.HTTP_200_OK)
    
    def post(self, request):
        # print(request.data)
        option = Specification_Type(product_specification_type = request.data["specification"])
        
        option.save()
        return Response(status = status.HTTP_201_CREATED)



class AddProduct(APIView):
    permission_classes = (IsSuperUser, )
    def post(self, request):

        finalData = {}
        data = request.data

        


        finalData.update({"_id": json.loads(data['product_info'])['slug']})

        for d in data:
            try:
                # print("try: ")
                # print(type(data[d]))
                finalData.update({d : json.loads(data[d])})
            except:
                # print("except")
                finalData.update({d : data[d]})


        finalData.update({"opened": 0})
        finalData.update({"favorites": 0})
        finalData.update({"created_at": current_time})
        finalData.update({"updated_at": current_time})
        
        
        Products.insert_one(finalData)


        return Response(status = status.HTTP_201_CREATED) 


class UpdateProduct(APIView):
    permission_classes = (IsSuperUser, )
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
    def post(self, request):
        # print(request.headers)
        updated_fields = {}
        finalData = {}
        data = request.data
        
        product_info = {}
        product_id = json.loads(data['product_info'])['slug']
        old_product = Products.find_one({"_id": product_id})

        for d in data:
            try:

                if not (old_product[d] == json.loads(data[d])):
                    # print("changed  ", d)
                    updated_fields[d] = json.loads(data[d])
                
            except:
                
                if not (old_product[d] == data[d]):

                    updated_fields[d] = data[d]
        
        current_time = datetime.datetime.now()
        current_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
        updated_fields["updated_at"]= current_time
        finalData.update({"updated_at": current_time})
        # print(updated_fields)

        Products.update_one({'_id': product_id}, {'$set' : updated_fields})



        return Response(status = status.HTTP_201_CREATED) 

class DeleteProduct(APIView):
    permission_classes = (IsSuperUser, )
    def delete(self, request):
        # print(request.user)
        Products.delete_one({"_id": 'fhgh-27a01b5a-ae9a-45fa-9968-50d8d31e9d7c'})
        return Response(status=status.HTTP_200_OK)

class UploadMedia(APIView):
    permission_classes = (IsSuperUser, )
    def post(self, request):
        # print(request.data)
        data = request.data

        for i in data:
            img = compress_image(data[i])
            f_name = settings.MEDIA_URL+"/products/images/"+img.name
            # f_name = img.name
            file_name = default_storage.save(f_name, img)
            # default_storage.delete("Screenshot from 2021-09-02 23-37-56.webp")
            # print(default_storage.listdir("/"))
            # default_storage.url("Screenshot from 2021-09-28 21-24-19.webp")

        # print(database.Products.find_one({"name": "sourav", "score": 2}))
        return Response(status = status.HTTP_201_CREATED) 


class GetMedia(APIView):

    def get(self, request):
        images_path = settings.MEDIA_URL+"/products/images"
        images = default_storage.listdir(images_path)
        media = images[1]

        # for i in media:
        #     print("i= ",i)
        return Response(media, status=status.HTTP_200_OK)



class GetSetting(APIView):

    def get(self, request, name):
        if name == 'all':
            data = list(AppSetting.find({}))

        else:
            data = AppSetting.find_one({"_id": name})

        return Response(data, status=status.HTTP_200_OK)


class SaveSetting(APIView):
    permission_classes = (IsSuperUser, )
    
    def post(self, request):
        response = JWT.authenticate(request)
        # print(response['User'])
        # for i in response:
        #     print(i)
        # print(request.user)
        updated_fields={}
        data = request.data
        # print(request.headers)
        settings = AppSetting.find_one({'_id': 'basic-settings'})


        for d in data:
            if not (settings[d] == data[d]):
                updated_fields[d] = data[d]

        AppSetting.update_one({'_id': 'basic-settings'}, {'$set' : updated_fields})

        return Response(data, status=status.HTTP_200_OK)
