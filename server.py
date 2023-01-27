#  coding: utf-8 
import socketserver
import os.path

# Copyright 2023 Abram Hindle, Eddie Antonio Santos, Daryna Chernyavska
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# Other references include:
#
#    Author: Mozilla Coporation and individual contributors
#    Title: HTTP
#    Year: 2023
#    Resource: https://developer.mozilla.org/en-US/docs/Web/HTTP
#    Attributions and copyright licensing by Mozilla Contributors is licensed under CC-BY-SA 2.5.
#
#    Authors: nikhilaggarwal3
#    Author's Page:
#        https://auth.geeksforgeeks.org/user/nikhilaggarwal3/articles
#    Improved by: surajkr_gupta https://auth.geeksforgeeks.org/user/surajkr_gupta,
#                 maityashis766 https://auth.geeksforgeeks.org/user/maityashis766
#    Title: Python: Check if a File or Directory Exists
#    Year: 2023
#    Resource: https://www.geeksforgeeks.org/python-check-if-a-file-or-directory-exists-2/
#    This resource is under creativecommons.org under CCBY-SA license
#
#    Author: Python Pool
#    Title: 5 Ways to Convert bytes to string in Python
#    Year: 2023
#    Resource: https://www.pythonpool.com/python-bytes-to-string/
#
#    OS path - Common pathnames manipulation was referenced which is © Copyright 2001-2023, Python Software Foundation
#    https://docs.python.org/3/library/os.path.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        response = self.createResponse()
        self.request.sendall(bytearray(response,'utf-8'))
    
    def getPath(self):
        # parses the request to obtain the path provided and uses it to create the respective local path 
        strData = self.data.decode()
        path = strData[strData.index("/") : strData.index(" HTTP/")]
        localPath = os.getcwd() + "/www" + path 
        return path, localPath

    def checkIsSafePath(self, desired):
        # checks if the desired path is in the /www directory
        shallowest = os.getcwd() + "/www"
        if os.path.commonpath([shallowest, os.path.normpath(desired)]) == shallowest:
            return True
        else:
            return False

    def determineFileType(self, path):
        # checks the extension of the file and returns the appropriate line for content type for the HTTP header
        basename = os.path.basename(path)
        print("basename:", basename)
        if basename.find(".css") != -1:
            return "Content-Type: text/css; charset=utf-8\r\n"
        elif basename.find(".html") != -1:
            return "Content-Type: text/html; charset=utf-8\r\n"
        else:
            return ""

    def createResponse(self):
        # parses the request and returns an appropriate response 
        if self.data.startswith(b"GET "): 
            path, localPath = self.getPath()
            if not self.checkIsSafePath(localPath):
                response = "HTTP/1.1 404 Not Found\r\n"
            else:
                if os.path.isfile(localPath):
                    # handles an existing file
                    file = open(localPath, "r")
                    fileContent = file.read()
                    file.close()
                    contentType = self.determineFileType(path)
                    response = "HTTP/1.1 200 OK\r\n{}\n{}\r\n".format(contentType, fileContent)
                elif os.path.isdir(localPath):
                    # handles an existing directory
                    if localPath[len(localPath)-1] != "/": 
                        # handles a directory that exists but a correct path was not provided
                        response = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}/\r\n".format(path)
                    else:
                        # handles an existing directory with a correct path
                        try:
                            file = open(localPath+"index.html", "r")
                            fileContent = file.read()
                            file.close()
                            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\n{}\r\n".format(fileContent)
                        except OSError: # index.html file does not exist for this directory
                            response = "HTTP/1.1 404 Not Found\r\n"

                else: # no such file or directory
                    response = "HTTP/1.1 404 Not Found\r\n"
        else: # method not handled
            response = "HTTP/1.1 405 Method Not Allowed\r\n"
        
        return response


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
