import os
import sys
import tarfile
import subprocess


if __name__ == '__main__':
    filename = sys.argv[1]
    out_dir = sys.argv[2]

    tar = tarfile.open(filename)
    files_info = []
    file_info = {'name': '', 'offset': 0, 'size': 0, 'type': ''}

    for files in tar.getmembers():
        # check file 
        if files.isdir():
            file_info['name'] = files.name
            file_info['type'] = 'dir'
        elif files.isfile():
            # get the fd from tarfile
            file_info['name'] = files.name
            file_info['offset'] = files.offset + 512
            file_info['size'] = files.size
            file_info['type'] = 'file'
        files_info.append(file_info)
        file_info = {}
    # according the files info copy and truncate file
    # TODO:
    # pay attention to the file offset in the list is from small to large
    fd = open(filename, 'r+')
    fd.seek(0)
    transbype = 0
    trans_block = 1024000
    for info in files_info:
        if info['type'] == 'dir':
            out_path = out_dir + '/' + info['name']
            if not os.path.exists(out_path):
                os.makedirs(out_path)
        elif info['type'] == 'file':
            file_path = out_dir + '/' + info['name']
            out_fd = open(file_path, 'w')
            last = info['size'] % trans_block
            counts = int(info['size'] / trans_block)
            current_offset = info['offset']
            if counts:
                for i in range(0, counts):
                    current_offset = info['offset'] + i * trans_blockk
                    fd.seek(current_offset, 0)
                    buf = fd.read(trans_block)
                    out_fd.write(buf)
                    command = 'fallocate -c -o %s -l %s %s' % (str(current_offset), trans_block, filename)
                    out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            if last:
                fd.seek(current_offset, 0)
                buf = fd.read(last)
                out_fd.write(buf)
                command = 'fallocate -c -o %sKiB -l %sKiB %s' % (str(current_offset), last, filename)
                out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

