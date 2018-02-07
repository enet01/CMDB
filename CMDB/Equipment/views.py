#coding:utf-8
import chardet
import paramiko
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from models import *
from WhileCMDB.views import getpage
from django.shortcuts import HttpResponseRedirect
def eq_add(request):
    pass

def eq_drop(request):
    pass

def eq_alter(request):
    pass


def eq_list(request):
    if request.method == "GET":
        requestData = request.GET
        page = requestData.get("page")
        num = requestData.get("num")
        sql = "select * from Equipment_equipment"
        if page and num:
            result = getpage(sql = sql,page = page,num = num)
        elif page :
            result = getpage(sql=sql, page=page)
        else:
            result = {
                "page_data": "",
                "page_range": ""
            }
    else:
        result = {
            "page_data": "",
            "page_range": ""
        }
    return JsonResponse(result)


def eq_list_page(request):
    eq_List = Equipment.objects.all()
    return render(request,"equipmentList.html",locals())

def eq_connect(request):
    """
    connect 方法实现 远程登录
    connect 方法实现 脚本上传
    connect 方法实现 脚本远程执行
    :param request:
    :return:
    """
    result = {"state":"error","data":""}
    if request.method == "POST":
        data = request.POST
        ip = data.get("ip")
        port = data.get("port")
        username = data.get("username")
        password = data.get("password")
        if ip and port and username and password:
            equpment = Equipment()
            equpment.IP = ip
            equpment.user = username
            equpment.Password = password
            try:
                trans = paramiko.Transport(ip,port)
                trans.connect(username = username,password = password)

                sftp = paramiko.SFTPClient.from_transport(trans) #用于文件的上传和下载的sftp服务
                ssh = paramiko.SSHClient() #远程执行命令的服务
                ssh._transport = trans
                #创建目录
                stdin,stdout,stderr = ssh.exec_command("mkdir CMDBClient")
                #上传文件
                sftp.put("sftpDir/getData.py","/root/CMDBClient/getData.py")
                sftp.put("sftpDir/sendData.py", "/root/CMDBClient/sendData.py")
                sftp.put("sftpDir/main.py", "/root/CMDBClient/main.py")
                #调用脚本
                stdin, stdout, stderr = ssh.exec_command("python /root/CMDBClient/main.py")
                trans.close()
                equpment.Statue = "True"
            except:
                equpment.Statue = "False"
            finally:
                equpment.save()
        else:
            pass
    else:
        pass

    return JsonResponse(result)


@csrf_exempt
def eq_save(request):
    ip = request.META["REMOTE_ADDR"]
    if request.method == "POST":
        data = request.POST
        hostname = data.get("get_hostname")
        system = data.get("get_system")
        mac = data.get("get_mac")

        equpment = Equipment.objects.get(IP = ip)
        equpment.hostname = hostname
        equpment.System = system
        equpment.Mac = mac
        equpment.save()

    return JsonResponse({"state":"this only a test"})


terminal_dict = {}

def shell(request):
    if request.method == "GET":
        id = request.GET["id"]
        if id:
            equipment = Equipment.objects.get(id = int(id))
            ip = equipment.IP
            username = equipment.user
            password = equipment.Password
            if ip and username and password:
                try:
                    result = {"status":"success","ip":ip,}
                    trans = paramiko.Transport(sock = (ip,22))
                    trans.connect(
                        username = username,
                        password = password
                    )
                    ssh = paramiko.SSHClient()
                    ssh._transport = trans
                    terminal = ssh.invoke_shell()
                    terminal.settimeout(2)
                    terminal.send("\n")
                    login_data = ""
                    while True:
                        try:
                            recv = terminal.recv(9999)
                            if recv:
                                login_data += recv
                            else:
                                continue
                        except:
                            break
                    result["data"] = login_data.replace("\r\n","<br>")
                    terminal_dict[ip] = terminal
                    response = render(request, "shell.html", locals())
                    response.set_cookie("ip",ip)
                    return response
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect("/eq/")
def command(request):
    ip = request.COOKIES.get("ip")
    if ip:
        if request.method == "GET":
            cmd = request.GET.get("command")
            if cmd:
                terminal = terminal_dict[ip]
                terminal.send(cmd+"\n")
                login_data = ""
                while True:
                    try:
                        recv = terminal.recv(9999)
                        if recv:
                            line_list = recv.split("\r\n")
                            result_list= []
                            for line in line_list:
                                l = line.replace(u"\u001B","").replace("[01;34m","").replace("[0m","").replace("[01;32m","")
                                result_list.append(l)
                            login_data = "<br>".join(result_list)

                        else:
                            continue
                    except:
                        break
                result = {"result":login_data}
                return JsonResponse(result)
            else:
                return HttpResponseRedirect("/eq/")
        else:
            return HttpResponseRedirect("/eq/")
    else:
        return HttpResponseRedirect("/eq/")

# import random

# def add_eq(request):
#     for i in range(100):
#         e = Equipment()
#         e.hostname = "localhost_%s"%i
#         e.IP = "192.168.1.%s"%(i+2)
#         e.System = random.choice(["win7_32","win7_64","centos.6_32","centos.7",])
#         e.Statue = random.choice(["True","False"])
#         e.Mac = random.choice(["00:0c:29:92:85:4e","00:0c:29:5b:2a:a1"])
#         e.user = "root"
#         e.Password = "123"
#         e.save()
#     return JsonResponse({"statue":"ahh"})


# Create your views here.
