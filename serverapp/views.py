from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from asgiref.sync import sync_to_async
import json
from .dbgetset import *
import subprocess
import ast
from subprocess import PIPE
import datetime
import importlib
import os

f = open('logs/config.json')
config = json.load(f)

logger = logging.getLogger(__name__)
logging.config.dictConfig(config)

@csrf_exempt
@sync_to_async
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file') and request.headers.get('test') and request.headers.get('code'):
        uploaded_file = request.FILES['file']
        test = request.headers['test']
        code = request.headers['code']
        all_code = get_all_withcode(code=code)
        if all_code and all_code["expire_date"]:
            if datetime.datetime.strptime(all_code["expire_date"], "%Y-%m-%d %H:%M:%S.%f") >= datetime.datetime.now():
                user_id = all_code["user_id"]
                logging.info(f"GOOD_DATE: {user_id}")
                filename = user_id+".py"
                with open("files/"+filename, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                logging.info(f"FILE_UPLOADED: {filename} user: {user_id}")
                check_file = importlib.import_module("files." + filename[:-3])

                info_test = get_info_test(test)
                docker_start_command = [
                    "docker", "run", "-e", "PYTHONUNBUFFERED=1","-e", "PYTHONIOENCODING=UTF-8","-i",
                    "--name", user_id, "--detach", "python"
                ]
                try:
                    tests = info_test["tests"].split(",")
                except TypeError:
                    logging.error(f"TEST_NOT_FOUND: {test} user: {user_id}")
                    return JsonResponse({'status': 'TEST_NOT_FOUND', 'user_id': str(user_id)}, status=400)
                
                id_of_container = subprocess.run(args=docker_start_command, stdout=PIPE).stdout
                id_of_container_str = id_of_container.decode().replace("\n","")
                logging.debug(f"Docker has started: {id_of_container_str} for {user_id}")
                
                docker_cp_command = ["docker", "cp", "/app/files/"+filename, id_of_container_str+f":/task.py"]
                subprocess.run(args=docker_cp_command)

                docker_cp_start_command = ["docker", "cp", "/app/start.py", id_of_container_str+f":/start.py"]
                subprocess.run(args=docker_cp_start_command)

                docker_start_file_command = ["docker", "exec", id_of_container_str, "python", "-u", f"start.py"] + tests
                docker_delete_command = ["docker", "rm", id_of_container_str]
                docker_stop_command = ["docker", "kill", id_of_container_str]
                res_of_tests = subprocess.run(args=docker_start_file_command, stdout=PIPE).stdout
                
                main_res = str(str(res_of_tests.decode()[3:-11]).split("\\n")).replace("'","")
                main_res = ast.literal_eval(main_res)
                subprocess.run(args=docker_stop_command)
                subprocess.run(args=docker_delete_command)
                logging.debug(f"Docker has stoped: {id_of_container_str} for {user_id}")
                os.remove("files/"+filename)
                res = get_all_fromtests(user_id, test)

                try:
                    list_of_result = res["result"]
                except:
                    list_of_result = None

                try:
                    count = int(res["count"])
                except:
                    count = 0

                if set(ast.literal_eval(info_test["answer"])) == set(main_res):
                    text = "Правильно:" if list_of_result == None else list_of_result + "Правильно:"
                    status = "CORRECT"
                else:
                    text = "Не Правильно:" if list_of_result == None else list_of_result + "Не Правильно:"
                    status = "PASS"
                del check_file
                all = get_all_fromclasses(user_id)

                if test in str(res):
                    update_tests_fromtests(str(user_id), str(test), text, str(count + 1), str(datetime.datetime.now()), str(all["name"]))
                    logging.info(f"{status}: {str(user_id)}")
                    return JsonResponse({'status': status, 'user_id': str(user_id), 'test': str(test)}, status=200)
                else:
                    insert_tests_fromtests(str(user_id), str(test), text, str(count + 1), str(datetime.datetime.now()), str(all["name"]))
                    logging.info(f"{status}: {str(user_id)}")
                    return JsonResponse({'status': status, 'user_id': str(user_id), 'test': str(test)}, status=200)
            else:
                logging.error(f"BAD_DATE: {all_code['expire_date']} user: {user_id}")
                return JsonResponse({'status': 'BAD_DATE', 'user_id': str(user_id)}, status=400)
        else:
            logging.error(f"NOT_FOUND_CODE: {code}")
            return JsonResponse({'status': 'NOT_FOUND_CODE'}, status=400)
    else:
        logging.error("NOT_ALL_ELEMENTS")
        return JsonResponse({'status': 'NOT_ALL_ELEMENTS'}, status=400)
    