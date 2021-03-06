from django.shortcuts import render,redirect
from .forms import *
from .models import ImageData
from django.utils import timezone
import joblib
import numpy as np
import os.path
from collections import Counter

def index(request):
    print(request.session.session_key)
    #새로운 브라우저에서 세션 정보 안담기면 강제로 저장
    if not request.session.session_key:
        request.session.save()
    print(request.session.session_key)
    return render(request,"index.html")

def information(request):
    return render(request,"information.html")

def imageUpload(request):
    if request.method == 'POST': 
        image_form = ImageForm(request.POST,request.FILES)
        if image_form.is_valid():
            try :
                imgForm = image_form.save(commit = False)
            except:
                return render(request,"index.html",{'err':5})
            imgForm.upload_date = timezone.now() 
            try :
                imgForm.sessionData = request.session.session_key
            except:
                return render(request,"information.html",{'err':2})
            print("세션확인 --")
            print("imgForm.sessionData",imgForm.sessionData ) 
            print("request.session.session_key",request.session.session_key) 
            try :
                imgForm.save()
                return redirect("colorSelect1",imgForm.id)
            except :
                return render(request,"information.html",{'err':4})

    else:
        image_form = ImageForm()
        return render(request,'imageUpload.html',{'form':image_form})

def colorSelect1(request,imageId):

    try :
        image=ImageData.objects.get(id= imageId)
    except:
        return render(request,"index.html",{'err':7})
    # 만약 세션이 맞지 않다면 데이터 접근 못하게
    if image.sessionData != request.session.session_key :
        return render(request,"index.html",{'err':1})
    
    else :
        if request.method == "POST":
            print("request.POST['color0']",request.POST.getlist('color'))
            image.c1=request.POST.getlist('color')[0]
            image.c2=request.POST.getlist('color')[1]
            try :
                image.save()
                return redirect("colorSelect2",imageId)
            except :
                return render(request,"information.html",{'err':4})
        else : 
            context = {}
            context['imageContents'] = image
            context['imageId'] = imageId
            context['order'] = 1
            return render(request,"colorSelect.html",context)

def colorSelect2(request,imageId):

    try :
        image=ImageData.objects.get(id= imageId)
    except:
        return render(request,"index.html",{'err':7})

    if image.sessionData != request.session.session_key :
        return render(request,"index.html",{'err':1})
    
    else :
        if request.method == "POST":
            print("request.POST['color0']",request.POST.getlist('color'))
            image.c3=request.POST.getlist('color')[0]
            image.c4=request.POST.getlist('color')[1]
            try :
                image.save()
                return redirect("colorSelect3",imageId)
            except :
                return render(request,"information.html",{'err':4})
        else : 
            context = {}
            context['imageContents'] = image
            context['imageId'] = imageId
            context['order'] = 2
            return render(request,"colorSelect.html",context)

def colorSelect3(request,imageId):
    
    try :
        image=ImageData.objects.get(id= imageId)
    except:
        return render(request,"index.html",{'err':7})
    if image.sessionData != request.session.session_key :
        return render(request,"index.html",{'err':1})
    
    else :  
        if request.method == "POST":
            print("request.POST['color0']",request.POST.getlist('color')[0])
            print("request.POST['color1']",request.POST.getlist('color')[1])
            image.c5=request.POST.getlist('color')[0]
            image.c6=request.POST.getlist('color')[1]
            try :
                image.save()
                return redirect("colorSelect4",imageId)
            except :
                return render(request,"information.html",{'err':4})
        else : 
            context = {}
            context['imageContents'] = image
            context['imageId'] = imageId
            context['order'] = 3
            return render(request,"colorSelect.html",context)

def colorSelect4(request,imageId):
    
    try :
        image=ImageData.objects.get(id= imageId)
    except:
        return render(request,"index.html",{'err':7})

    if image.sessionData != request.session.session_key :
        return render(request,"index.html",{'err':1})
    
    else :
        if request.method == "POST":
            print("request.POST['color0']",request.POST.getlist('color')[0])
            print("request.POST['color1']",request.POST.getlist('color')[1])
            image.c7=request.POST.getlist('color')[0]
            image.c8=request.POST.getlist('color')[1]
            try :
                image.save()
                return redirect("loading",imageId)
            except :
                return render(request,"information.html",{'err':4})
            
        else : 
            context = {}
            context['imageContents'] = image
            context['imageId'] = imageId
            context['order'] = 4
            return render(request,"colorSelect.html",context)

def loading(request,imageId):
   
    try:
        try :
            image=ImageData.objects.get(id= imageId)
        except:
            return render(request,"index.html",{'err':7})
        rgbResult=[] #머신러닝으로 최종으로 보낼 이중리스트
        
        rgbList=[]
        rgbList.append(image.c1)
        rgbList.append(image.c2)
        rgbList.append(image.c3)
        rgbList.append(image.c4)
        rgbList.append(image.c5)
        rgbList.append(image.c6)
        rgbList.append(image.c7)
        rgbList.append(image.c8)

        for value in rgbList:
            value = value.lstrip('rgb(')
            value = value.rstrip(')')
            color = value.strip().split(',')
            color_list=[] #각리스트
            for i in color :
                color_list.append(int(i))

            print(color_list)
            rgbResult.append(color_list)
            
        print("=========",rgbResult,"==========")
        try:
            #머신러닝 작동
            scriptpath = os.path.dirname(__file__)
            filename = os.path.join(scriptpath, 'optimized_peanut_knn_model.pkl')
            model = joblib.load(filename)
            test = np.array(rgbResult)
            res = model.predict(test)
            #최빈값 
            count = Counter(res)
            most = count.most_common(1)
            print(most[0][0])#최종데이터
            return render(request, "loading.html",{'result_val':most[0][0]})
        except :
            return render(request,"information.html",{'err':6})
    except :
        return render(request,"information.html",{'err':0})

def result(request,result_val):
    try:
        print("@@@@@@@@최종결과값",result_val)
        return render(request,"result.html",{'result_val':result_val})
    except :
        return render(request,"information.html",{'err':3})