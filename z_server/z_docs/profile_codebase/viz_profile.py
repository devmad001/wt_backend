import os
import sys
import codecs
import json
import re
import time
import threading

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

root_dir=LOCAL_PATH+"../../../"

# Gather all .py files into a list
py_files = []
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.py'):
            py_files.append(os.path.join(root, file))

# Write file paths to a temporary file
with open('file_list.txt', 'w') as f:
    for item in py_files:
        # change \ slashes to /
        item=item.replace("\\","/")
        f.write("%s\n" % item)

# Construct and run the Pyan command

cmd='python -m pyan file_list.txt --output mygraph.svg'
print ("> "+str(cmd))
os.system(cmd)

"""

NOTES for visualizing and profiling codebase

pip install pyan==1.1.1
https://graphviz.org/download/  (for dot)

python -m pyan *.py --dot > simple.dot

dot -Tsvg mymodule_uses.dot > mymodule_uses.svg

dot -Gnewrank=true -Tsvg mymodule_uses.dot > mymodule_uses.svg


RUN ON WINDOWS ALL FILES:
    **also seems like a good way to check for syntax errors across all code
Get-ChildItem . -Recurse -Filter *.py | Foreach-Object { python -m pyan $_.FullName --output mygraph.svg }


"""


"""
 INSPECT/Trace  ROUTINE
- cProfile (+SnakeViz to view), py-spay profile, pycallgraph to view, 
- pyan for static., code2flow, 


For static profile use:
- pyan

===========
For real profile use:
https://github.com/gak/pycallgraph/blob/master/docs/index.rst

(1)
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

with PyCallGraph(output=GraphvizOutput()):
    code_to_profile()
(2)
pycallgraph graphviz -- ./mypythonscript.py

python -m pyan *.py */*.py */*/*.py */*/*/*.py */*/*/*/*.py --dot > simple.dot

modvis **/*.py --dot > graph.dot


"""
