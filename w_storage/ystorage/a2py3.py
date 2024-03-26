import os


#0v2# JC Jan 14, 2022   Use with database migration ** see ystorage_handler db migration
#0v1# JC May  1, 2019   Setup py2 to py3 interface


#https://stackoverflow.com/questions/27863832/calling-python-2-script-from-python-3


def call_python_version(Version, Module, Function, ArgumentList,workon=''):
    import execnet #<-- pip install execnet
    python_path="C:/Users/jon/Envs/mitm_py36/Scripts/python"
    gw      = execnet.makegateway("popen//python="+python_path)

    #gw      = execnet.makegateway("popen//python=python%s" % Version)

    channel = gw.remote_exec("""
        from %s import %s as the_function
        channel.send(the_function(*channel.receive()))
    """ % (Module, Function))
    channel.send(ArgumentList)
    #** optional channel.close()
    return channel.receive()


def dev1():
    workon_python="C:/Users/jon/Envs/mitm_py36/Scripts/python"
    
    phrase='job postings'

    if False:  #Not required always
        workon_dir="C:/Users/jon/Envs/mitm_py36"
        org_PYTHON_PATH=os.environ['PYTHONPATH']
        org_PATH=os.environ['PATH']
    
        os.environ['VIRTUAL_ENV']=workon_dir
        os.environ['PATH']=workon_dir+";"+org_PATH
        #?    os.environ['PYTHONHOME']=""

    argumentlist=[phrase]
    results=call_python_version('3','GoogleScraperCustom.do_search','realtime_search_interface',argumentlist)
    print ("GOT RESULTS: "+str(results))

    return

def ystorage_migration():
    workon_python="C:/Users/jon/Envs/mitm_py36/Scripts/python"
    argumentlist=[phrase]
    results=call_python_version('3','GoogleScraperCustom.do_search','realtime_search_interface',argumentlist)
    print ("GOT RESULTS: "+str(results))
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['ystorage_migration']
    for b in branches:
        globals()[b]()


"""
for reuse or terminate

>>> import execnet
>>> group = execnet.Group()
>>> gw = group.makegateway("popen//id=sleeper")
>>> ch = gw.remote_exec("import time ; time.sleep(2.0)")
>>> group
<Group ['sleeper']>
>>> group.terminate(timeout=1.0)
>>> group
<Group []>
"""

