""" This is an interface for testing """
import argparse
import re
import shutil
import os
import subprocess
from pathlib import Path

WORKING_DIR = os.getcwd()
MODULE_DIR = __file__

def get_parser():
    """ Specify the arguments"""
    parser = argparse.ArgumentParser(description='instant coding answers via the command line')
    parser.add_argument('simfilename', metavar='SIMFILENAME', type=str, nargs=1, help='the sim file to execute')
    parser.add_argument('-j', '--jobname', help='job name for slurm (<6 char)', default='job',  action='store')
    parser.add_argument('-N', '--nodes', help='number of nodes', default=None, action='store')
    parser.add_argument('-n', '--cpus', help='number of cpus', default=None, action='store')
    parser.add_argument('-l', '--nodelist', help='node list', default=None, action='store')
    parser.add_argument('-p', '--partition', help='partition name', default=None, action='store')
    parser.add_argument('-v', '--version', help='Starccm+ version', default='18.02', action='store')
    parser.add_argument('-r', '--runjava', help='specify javafile to run', default=None, action='store')
    parser.add_argument('-t', '--time', help='specify javafile to run', default=None, action='store')
    parser.add_argument('-i', '--interactive', help='interactive job?', default=0, action='store')


    return parser

def check_args(args, host):
    if len(args['jobname'])>7:
        print("The jobname is too long (char<7)")

    print(f"Executing pyAcqua on {host}")
    # Check Star ccm+ version
    if args['version'] == '18.02':
        args['star_path'] = "/home/yjouwang/18.02.008-R8/STAR-CCM+18.02.008-R8"
    elif args['version'] == '16.02':
        args['star_path'] = "/home/yjouwang/16.02.009-R8/STAR-CCM+16.02.009-R8" 
    elif args['version'] == '19.04':
        args['star_path'] = "/home/rbrew/STAR-CCM+/19.04.009-R8/STAR-CCM+19.04.009-R8"
    else:
        raise ValueError("Now the version only supports 15.06 & 16.02")

    print('Done checking')
    return args

def read_file(template_file_name):
    filepath = os.path.join(os.path.dirname(__file__), template_file_name)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def write_file(file_name, content):
    write_to = os.path.join(WORKING_DIR, file_name)
    with open(write_to, 'w', encoding='utf-8') as f:
        f.write(content)
    return

def find_java_title(java_file):
    kw = 'public class \w* extends StarMacro'
    title = re.findall(kw, java_file)[0]
    name = title.split(' ')[2]
    return name, title

def copy_java_file(java_file_name, jobname):
    # modify the java file name 
    with open(java_file_name, 'r') as f:
        java_file = f.read()
    java_name, title_line = find_java_title(java_file)
    java_file = java_file.replace(java_name, jobname)
    write_file(file_name='%s.java'%jobname, content=java_file)
    return
        

def prepare_java_file(jobname):
    content = read_file('simple_run.java')
    content_m = content.replace('JOBNAME', jobname)
    write_file(file_name='%s.java'%jobname, content=content_m)
    return

def prepare_slurm_file(host, simfilename, jobname, star_path, n_cpus):
    content = read_file('slurm.slurm')

    content_m = content.replace("SIM_FILE_NAME", simfilename)
    content_m = content_m.replace("JOB_NAME", jobname)
    content_m = content_m.replace("STAR_VERSION", star_path)

    if (int(n_cpus) % 32) != 0 :
        content_m = content_m.replace("N_CPUS_FOR_SIM", "$SLURM_NTASKS")
    else:
        content_m = content_m.replace("N_CPUS_FOR_SIM", "$SLURM_CPUS_ON_NODE")
    write_file(file_name='%s.slurm' % jobname, content=content_m)
    return

def prepare_shell_file(host, jobname, n_nodes, n_processors, partition, nodelist, time):

    if partition:
        info_node = f' -N {n_nodes}'
        # info_processors = f' -n {n_processors}'
        info_processors= f' --ntasks-per-node={n_processors}'

        if partition:
            info_part = f' -p {partition}'
        else:
            info_part = ''
        
        if time:
            time_part = f' -t {time}'
        else:
            time_part = ''
            
        if nodelist:
            nodelist_part = f' --nodelist={nodelist}'
        else:
            nodelist_part=''
        
        content = "sbatch" + info_node + info_processors + info_part + time_part + nodelist_part + f' {jobname}.slurm --exclude=node[122] --exclusive'
        print(content)
        write_file('%s.sh'%jobname, content)
    else:
        # It's interactive mode, copy all the slurm and run 
        filepath = f'{jobname}.slurm'
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        write_file('%s.sh'%jobname, content)

    return


def prepare_files(args, host):
    simfilename = args['simfilename'][0]
    jobname = args['jobname']
    n_nodes = args['nodes']
    n_cpus = args['cpus']
    nodelist = args['nodelist']
    partition = args['partition']
    star_path = args['star_path']
    time = args['time']
    # Prepare files
    if args['runjava'] is None:
        prepare_java_file(jobname)
    else:
        copy_java_file(args['runjava'], jobname)
    
    # compute total processors
    if args['cpus'] ==None:
        if args['partition'] in ['sched_mit_nse_r8', 'sched_mit_emiliob_r8']:
            n_cpus = 192
        elif args['partition'] in ['sched_mit_nse', 'sched_mit_emiliob']:
            n_cpus = 32
        elif args['partition'] in ['newnodes', 'sched_mit_hill']:
        	n_cpus = 16
        else:
            n_cpus = 32
    
    if args['partition'] != None:
        # n_processors = int(n_cpus)*int(n_nodes)
        n_processors = int(n_cpus)
    else:
        n_processors = None


    prepare_slurm_file(host, simfilename, jobname, star_path, n_cpus)
    prepare_shell_file(host, jobname, n_nodes, n_cpus, partition, nodelist, time)
    


def check_machine():
    hostname = subprocess.check_output("hostname", encoding='utf-8', shell=True)
    host = hostname.split('.')[0]
    return host

def submit_job(args):
    if args['interactive'] != 0:
        print('Interactive mode')
        slurm_file = "%s.slurm"%args['jobname']
        os.system('chmod 754 "%s"'%slurm_file)

        return
    else:
        bash_file = "%s.sh"%args['jobname']
        os.system('chmod 754 "%s"'%bash_file)
        os.system('./%s' % bash_file)


def command_line_runner():  # pylint: disable=too-many-return-statements,too-many-branches
    # Check machine

    # Get Parser
    parser = get_parser()
    args = vars(parser.parse_args()) # get dictionary pairs
    print(args)
    host = check_machine()
    args = check_args(args, host)
    prepare_files(args, host)
    submit_job(args)

