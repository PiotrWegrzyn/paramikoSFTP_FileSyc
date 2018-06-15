import paramiko
import os


def find_file(file_list, search_file):
    for remoteFile in file_list:
        if remoteFile.filename == search_file:
            return remoteFile
    return None


def is_ignored(ignored_extenions, extension):
    for ignored_extension in ignored_extenions:
        if ignored_extension == extension:
            return True
    return False


class FileSender:
    def __init__(self, mode, ignored_extensions):
        self.mode = mode
        self.ssh = None
        self.sftp = None
        self.socket = None
        self.ignored_extensions = ignored_extensions


    def connect(self, username, password, hostname, port):
        self.ssh = paramiko.Transport(hostname, port)
        self.ssh.connect(username=username, password=password)
        self.sftp = paramiko.SFTP.from_transport(self.ssh)

    def synchronize(self, local_path, remote_path):
        sent = []
        remote_folder = self.sftp.listdir_attr(remote_path)
        local_folder = [file for file in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, file))] #generator expressions

        for localFile in local_folder:
            filename, file_extension = os.path.splitext(localFile)
            #print(filename + file_extension)
            if is_ignored(self.ignored_extensions, file_extension):
                continue
            if self.mode == "override":
                local_file_path = os.path.join(local_path, localFile)
                #print(local_file_path)
                remote_file_path = remote_path + "/" + localFile
                self.sftp.put(local_file_path,remote_file_path)
                sent.append(localFile)
            elif self.mode == "update":
                remote_file = find_file(remote_folder, localFile)
                if remote_file is None:
                    continue
                else:
                    file_stat = os.stat(os.path.join(local_path, localFile))
                    if file_stat.st_mtime > remote_file.st_mtime:
                        local_file_path = os.path.join(local_path, localFile)
                        remote_file_path = remote_path + "/" + localFile
                        self.sftp.put(local_file_path, remote_file_path)
                        sent.append(localFile)
                    else:
                        continue

            elif self.mode == "add_non_existing":
                remote_file = find_file(remote_folder, localFile)
                if remote_file is None:
                    local_file_path = os.path.join(local_path, localFile)
                    remote_file_path = remote_path + "/" + localFile
                    self.sftp.put(local_file_path, remote_file_path)
                    sent.append(localFile)
                else:
                    continue
        return sent

    def moveFromServer(self, local_path, remote_path, date):
        sent = []
        remote_folder = self.sftp.listdir_attr(remote_path)

        for remoteFile in remote_folder:
            # filename, file_extension = os.path.splitext(remoteFile)
            # file_stat = os.stat(os.path.join(local_path, remoteFile))
            if date > remoteFile.st_mtime:
                local_file_path = local_path + "\\" + remoteFile.filename  # os.path.join(local_path, remoteFile)
                remote_file_path = remote_path + "/" + remoteFile.filename
                self.sftp.get(remote_file_path, local_file_path)
                self.sftp.remove(remote_file_path)
                sent.append(remoteFile)
            else:
                continue
        return sent

    def disonnect(self):
        self.sftp.close()
        self.ssh.close()

