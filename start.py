import sys
import subprocess
from subprocess import PIPE
args = sys.argv[1:]
command = ["python", "task.py"]

ready_arg = '\n'.join(args).strip()
res = subprocess.Popen(args=command, stdin=PIPE, stdout=PIPE)
res_of_tests = res.communicate(input=str.encode(ready_arg))

print(res_of_tests)