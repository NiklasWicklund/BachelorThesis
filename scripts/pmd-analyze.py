
import re
import subprocess
import os
import pickle
from tqdm import tqdm
from optparse import OptionParser



#Returns list of tuples with information about all student repos in specific directory.
def get_all_student_files(directory):
    files = []
    students = [ (f.path,f.name) for f in os.scandir(directory) if f.is_dir() ]
    for t in students:
        student = t[1]
        _files = [ (f.path,f.name) for f in os.scandir(t[0]) if f.is_dir() ] # (student,path,dirname,task)
        for f in _files:
            task = re.search(f"{student}-(.*)",f[1])
            if task is not None:
                files.append((student,f[0],f[1],task.group(1)))
    
    return files
        




def analyze(directory,output_folder,ruleset,one_task,prefix,student_group_path):

    infile = open(student_group_path, 'rb')
    student_ta = pickle.load(infile) #(task)(student) = (pushed,passed)
    infile.close()
    repos = get_all_student_files(directory) # All repos in tuple (student,path,filename,task)

    print("Running ruleset: ",ruleset)
    print("Fething repos from: ",directory)
    print("Outputting to: ",output_folder)
    print("Found",len(repos),"repos")
    print("Found",len(student_ta), "students in student-groups.bin")


    students = 0
    for student in student_ta:
        if student_ta[student][1] == "B" or student_ta[student][1] == "R":
            students+=1
    print("Will run on",students,"students")
    
    os.makedirs(f"{output_folder}", exist_ok=True)
    skipped = 0
    ran = 0
    for dir in tqdm(repos):
        student = dir[0]
        task = dir[3]

        if one_task is not None and task != one_task:
            continue
        if task == "quicksort":
            task = f"{prefix}-19"
        
        path = dir[1]
        os.makedirs(f"{output_folder}{task}", exist_ok=True)
        command = (
            f"~/pmd-bin-*/bin/run.sh pmd "
            f"-d {path} "
            f"-f json "
            f"-R {ruleset}"
        )
        
        if student_ta[student][1] == "B" or student_ta[student][1] == "R":
            file_name = f"{student}-{task}"
            path_o = f"{output_folder}{task}/{file_name}"
            if not os.path.exists(path_o):
                with open(path_o, "w") as outfile:
                    subprocess.run(command,stdout=outfile,shell=True,stderr=subprocess.PIPE )
                ran+=1
        
    
    print("Would have skipped: ", skipped)
    print("Ran ", ran ,"repos")

parser = OptionParser()
parser.add_option("-d", "--directory", dest="sourcedir",default='.',
                  help="directory of violations", metavar="DIR")
parser.add_option("-o", "--output", dest="outputdir",
                  help="directory to save results in", metavar="DIR",default='./result-pmd/')
parser.add_option("-r", "--ruleset", dest="ruleset",
                  help="path to ruleset used when mining, if present, gives another layer of data", metavar="FILE",default='rulesets/internal/all-java.xml')
parser.add_option("-a", "--task", dest="task",
                  help="specific task")
parser.add_option("-g", "--sg", dest="student_group_path",
                  help="path to binary file describing student groups")  
parser.add_option("-f", "--prefix", dest="prefix",help="prefix-xx", default="task")             
(options, args) = parser.parse_args()

if options.student_group_path is None:
    quit("Needs path to binary file for student groups.")

analyze(options.sourcedir,options.outputdir,options.ruleset,options.task,options.prefix,options.student_group_path)



