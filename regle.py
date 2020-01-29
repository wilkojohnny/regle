#!/usr/local/bin/python3.7

# regle -- perpetually gle a file, so we don't need to keep on running the gle command

import argparse  # to get the command line arguments
import subprocess  # to run the shell command for gle
import datetime  # to print current date and time
import os  # for watching files
import sys  # for counting how many arguments there are


def main():
    """
    when regle [file name] is called, watch the file and re-run gle if the file is changed.
    :return: 0 if successful, 1 if not
    """
    try:
        # get command line arguments
        parser = argparse.ArgumentParser(description='ReGLE -- Run GLE for a file every time its changed.')
        parser.add_argument("gle_file", help="Location of the GLE file to run perpetually", nargs='*')
        parser.add_argument("--pdf", action="store_true", help="run gle in PDF making mode")
        parser.add_argument("--nogv", action="store_true", help="don't run gv")

        arguments = parser.parse_args()
        if len(sys.argv) == 1:
            # if no arguments parsed, complain
            parser.print_help()
            exit()
        gle_files = arguments.gle_file
        pdf_mode = arguments.pdf
        no_gv = arguments.nogv

        last_gle = [0 for i in range(0, len(gle_files))]  # stores when the last GLEification happened
        gle_success = [0 for i in range(0, len(gle_files))]  # stores whether the last GLE was successful

        # run gle command on files initially
        for i in range(0, len(gle_files)):
            last_gle[i], gle_success[i] = regle(gle_files[i], last_gle[i], gle_success[i], pdf_mode, no_gv)

        # each second, for each file, if they haven't been GLEed then GLE them
        while True:
            for i in range(0, len(gle_files)):
                if last_gle[i] < os.stat(gle_files[i]).st_mtime:
                    last_gle[i], gle_success[i] = regle(gle_files[i], last_gle[i], gle_success[i], pdf_mode, no_gv)

    except KeyboardInterrupt:
        print('Bye...')
    except FileNotFoundError:
        print('Cant find one of the GLE files. Bye...')
    finally:
        pass

    return 0


def regle(gle_file, last_gle, gle_success, pdf_mode, no_gv):
    gle_out = run_gle(gle_file, pdf_mode)
    gle_success_now = not gle_out
    if not no_gv:
        # if GLE was successful for the first time, launch gv
        if gle_success != gle_success_now:
            gv_success = run_gv(file_name=gle_file)
    if gle_success_now:
        gle_success = True

    # print out the timestamp even if gle not successful... nothing will change until the file is updated!
    now = datetime.datetime.now()
    last_gle = now.timestamp()

    # return if successful and the timestamp
    return last_gle, gle_success


def run_gle(file_name, pdf_mode):
    """
    run GLE command and print the output if not OK
    :param file_name: file name of the .gle file
    :param pdf_mode: run GLE in pdf-making mode
    :return: 0 if successful, 1 if not
    """

    if pdf_mode:
        gle_device_pdf = '--device pdf '
    else:
        gle_device_pdf = ''
    # run command
    gle_process = subprocess.run('gle ' + gle_device_pdf + file_name, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, shell=True)
    gle_return_code = gle_process.returncode
    # if successful:
    if gle_return_code == 0:
        now = datetime.datetime.now()
        print('GLE command last successfully run on ' + file_name + ' at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
        return 0
    else:
        print('GLE ERROR:')
        print(gle_process.stdout)
        return 1


def run_gv(file_name):
    # run gv in background -- can't know if its successful or not as it runs continuously...

    # if file_name ends in gle, change it to eps (or pdf)
    output_filename = os.path.splitext(file_name)[0]+'.eps'
    if not os.path.exists(output_filename):
        output_filename = os.path.splitext(file_name)[0] + '.pdf'
        if not os.path.exists(output_filename):
            print('Could not find output file.')
            output_filename = ''
    subprocess.Popen('gv ' + output_filename + ' --watch &', shell=True)
    return 0


if __name__ == '__main__':
    main()
