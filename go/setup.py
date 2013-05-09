import subprocess
import sys
import os
import setup_util

def start(args):
  goenv = os.environ.copy
  goenv['GOROOT'] = os.getcwd() + "/installs/go"
  goenv['GOPATH'] = os.getcwd() + "/go"
  goenv['PATH'] = goenv['GOROOT'] + "/bin:" + goenv['PATH']
  setup_util.replace_text("go/src/hello/hello.go", "tcp\(.*:3306\)", "tcp(" + args.database_host + ":3306)")
  subprocess.call("go get ./...", shell=True, cwd="go" env=goenv) 
  subprocess.Popen("go run src/hello/hello.go".rsplit(" "), cwd="go" env=goenv)
  return 0

def stop():
  p = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
  out, err = p.communicate()
  for line in out.splitlines():
    if 'hello' in line:
      pid = int(line.split(None, 2)[1])
      os.kill(pid, 9)
  return 0
