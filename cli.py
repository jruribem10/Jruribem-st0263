import os
import shutil
import cmd
import client

class FileManagerCLI(cmd.Cmd):
    intro = ''
    prompt = '(CLI) '
    base_url = "http://localhost:5000"

    def get_credentials(self):
        self.user = input('Enter username: ')
        self.password = input('Enter password: ')

    def do_get(self, file_name):
        client.get_file(self.base_url, file_name, self.user, self.password)
    
    def do_index(self):
        """Index available datanodes"""
        client.index(self.base_url)

    def do_ls(self, args):
        """List files and directories in the current directory."""
        items = os.listdir('.')
        for item in items:
            print(item)
    
    def do_cd(self, path):
        """Change to the specified directory: cd <directory>"""
        try:
            os.chdir(path)
            print(f"Directory changed to {os.getcwd()}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_put(self, filename):
        """Copy a file to the current directory: put <file_path>"""
        try:
            shutil.copy(filename, '.')
            print(f"File {filename} copied to the current directory.")
        except Exception as e:
            print(f"Error copying file: {e}")
    
    def do_copy(self, filename):
        """Copy a file from the current directory to a destination: get <file> <destination>"""
        try:
            source, dest = filename.split()
            shutil.copy(source, dest)
            print(f"File {source} copied to {dest}")
        except Exception as e:
            print(f"Error copying file: {e}")
    
    def do_mkdir(self, dirname):
        """Create a new directory: mkdir <directory>"""
        try:
            directory_name = input("Enter the name of the new directory: ")
            client.create_directory(self.base_url, directory_name)
        except Exception as e:
            print(f"Error creating directory: {e}")
    
    def do_rmdir(self, dirname):
        """Remove an empty directory: rmdir <directory>"""
        try:
            directory_name = input("Enter the name of the directory to remove: ")
            client.remove_directory(self.base_url, directory_name)
        except Exception as e:
            print(f"Error removing directory: {e}")
    
    def do_rm(self, filename):
        """Remove a file: rm <file>"""
        try:
            file_name = input("Enter the name of the file to remove: ")
            client.remove_file(self.base_url, file_name)
        except Exception as e:
            print(f"Error removing file: {e}")
    
    def do_exit(self, arg):
        """Exit the CLI."""
        print("Exiting...")
        return True
    
    def do_upload(self, file_name):
        """Upload a file to a datanode"""
        try :
            datanode = client.search(self.base_url)
            print('inside upload, filename: ', file_name)
            if len(datanode) == 0:
                print("No DataNodes available. Aborting upload.")
                return

            client.upload_file(datanode, file_name, f'{os.getcwd()}/{file_name}', self.user, self.password)
        except Exception:
            print("Error uploading. Try again")
    
    def do_welcome(self, args=None):
        print("Welcome to the CLI")
        print("------------------------------------------------------------")
        print("* Available commands: ")
        print("* cd - navigate through local directories")
        print('* ls - list files inside current dierctory')
        print('* upload <filename.ext - upload file to network')
        print('* get <filename.ext> - get a file you uploaded from network')
        print('* mkdir <dir> - create directory')
        print('* rm <file> - remove file')
        print('* welcome - prints welcome message')
        print('* exit - exits')
        

