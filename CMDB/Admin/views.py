#coding:utf-8
from django.shortcuts import render
from forms import Register
from models import User
from django.http import JsonResponse
import hashlib
from PIL import Image
from django.http import HttpResponseRedirect


def phoneValid(request):
    result = {"statue":"error","data":""}
    if request.method == "GET": #判断是否get请求
        phoneNum = request.GET.get("phone_num") #获取传递过来的电话号
        if phoneNum: #判断电话号是不为空
            try:
                u = User.objects.get(phone = phoneNum) #判断数据库当中是否有该电话号
            except: #数据库当中没有该电话号
                result["statue"] = "success"
                result["data"] = "该手机号可以使用"
            else: #数据当中有该电话号
                result["data"] = "该手机号可以使用"
        else: #判断电话号是为空
            result["data"] = ""
    else: #不是get请求
        result["data"] = "请求发送错误"
    return JsonResponse(result)

def getmd5(password):
    md5 = hashlib.md5()
    md5.update(password)
    return md5.hexdigest()

def loginValid(fun):
    def inner(request,*args,**kwargs):
        cookie = request.COOKIES
        c_phone = cookie.get("phone")
        s_phone = request.session.get("phone")
        if c_phone and c_phone == s_phone :
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/login")
    return inner
def login(request):
    if request.method == "POST":
        data = request.POST
        phone = data.get("phone")
        password = data.get("password")
        valid_remember = data.get("remember")
        cookie_remember = request.COOKIES.get("key")
        if valid_remember == cookie_remember:
            try:
                u = User.objects.get(phone = phone)
            except:
                return HttpResponseRedirect("/login")
            else:
                post_password = getmd5(password)
                if post_password == u.password:
                    response = HttpResponseRedirect("/index")
                    response.set_cookie("phone",u.phone)
                    request.session["phone"] = u.phone
                    request.session["user_id"] = u.id
                    return response
                else:
                    return HttpResponseRedirect("/login")
        else:
            return HttpResponseRedirect("/login")
    else:
        return HttpResponseRedirect("/login")

def logout(request):
    pass

def user_list(request):
    register = Register()
    if request.method == "POST":
        data = request.POST
        img = request.FILES

        username = data.get("username")
        password = data.get("password")
        phone = data.get("phone")
        email = data.get("email")

        photo = img.get("photo")

        name = "static/img"+photo.name
        img = Image.open(photo)
        img.save(name)


        user = User()
        user.username = username
        user.password = getmd5(password)
        user.phone = phone
        user.email = email
        user.photo = "img/"+photo.name
        user.save()
    return render(request,"userList.html",locals())

def user_alter(request):
    pass

def user_drop(request):
    pass

# Create your views here.
