from loguru import logger
import subprocess

from modules import config
from modules.exceptions import AbsentPackageException, ErrorInstallingException, ErrorUninstallingException, NotEnoughSpaceException
import os


def install(new_apk_path):
    cmd = '"{}" install -r "{}"'.format(config.ADB_PATH, new_apk_path)
    try:
        out = request_pipe(cmd)
    except Exception as e:
        if 'not enough space' in str(e):
            raise NotEnoughSpaceException()
        raise ErrorInstallingException
    if 'Exception occurred while dumping' in out:
        raise ErrorUninstallingException


def uninstall(package):
    cmd = '"{}" uninstall "{}"'.format(config.ADB_PATH, package)
    try:
        request_pipe(cmd)
    except Exception:
        raise ErrorUninstallingException


def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err

    if pipe.returncode > 0 :
        raise Exception("----------------------------------------------------\n\
Out: %s\nError: %s" % (out, err))

    return res.decode('utf-8')


def start_activity_explicitly(package_name, activity_name):
    # adb shell am start -n com.package.name/com.package.name.ActivityName
    logger.debug("Starting activity [%s] of the package [%s]..." % (activity_name, package_name))

    run_string = package_name + '/' + activity_name
    cmd = "{0} shell am start -n {1}".format(config.ADB_PATH, run_string)
    request_pipe(cmd)

def clean_log():
    cmd = "{0} logcat -c".format(config.ADB_PATH)
    request_pipe(cmd)

def dump_log(path):
    cmd = "{0} logcat -d *:E > {1}".format(config.ADB_PATH, path)
    request_pipe(cmd)

def save_log(logs_dir, app):
    file_path = os.path.join(logs_dir, "{}.txt".format(app))
    dump_log(file_path)
    return file_path


def read_log(path):
    with open(path, 'r') as file:
        data = file.read()
        return data

def get_api_level():
    cmd = "{} shell getprop ro.build.version.sdk".format(config.ADB_PATH)
    api_level = int(request_pipe(cmd))
    return api_level


def run_monkey(package, seed, throttle, event_num):
    cmd = 'adb shell monkey -p {} -s {} --throttle {} {}'
    request_pipe(cmd.format(package, seed, throttle, event_num))
