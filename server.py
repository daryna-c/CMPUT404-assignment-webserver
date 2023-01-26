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
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        response = self.parseRequest()
        #self.request.sendall(bytearray("OK",'utf-8'))
        self.request.sendall(bytearray(response,'utf-8'))
        print("response:\n", response)
    
    def getPath(self):
        strData = self.data.decode()
        path = strData[strData.index("/") : strData.index(" HTTP/")]
        print("path:", path)
        #localPath = os.path.join(os.getcwd(), "/www"+path)
        localPath = os.getcwd() + "/www" + path 
        print("local path:", localPath)
        return path, localPath

    def checkIsSafePath(self, desired):
        # checks if the desired path is in the /www directory
        shallowest = os.getcwd() + "/www"
        if os.path.commonpath([shallowest, os.path.normpath(desired)]) == shallowest:
            return True
        else:
            return False

    def determineFileType(self, path):
        basename = os.path.basename(path)
        if basename.find(".css") != -1:
            return "Content Type: text/css; charset=utf-8\r\n"
        elif basename.find(".html") != -1:
            return "Content Type: text/html; charset=utf-8\r\n"
        else:
            return ""

    def parseRequest(self):
        response = "NO RESPONSE!!!"
        if self.data.startswith(b"GET ") or self.requestData.startswith(b"HEAD "):
            path, localPath = self.getPath()
            if not self.checkIsSafePath(localPath):
                response = "HTTP/1.1 404 Not Found\r\n"
            else:
                if os.path.isfile(localPath):
                    file = open(localPath, "r")
                    fileContent = file.read()
                    file.close()
                    contentType = self.determineFileType(path)
                    response = "HTTP/1.1 200 OK\r\n{}\n{}\r\n".format(contentType, fileContent)
                elif os.path.isdir(localPath):
                    if localPath[len(localPath)-1] != "/":
                        response = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}/\r\n".format(path)
                    else:
                        try:
                            file = open(localPath+"index.html", "r")
                            fileContent = file.read()
                            file.close()
                            response = "HTTP/1.1 200 OK\r\nContent Type: text/html; charset=utf-8\r\n\n{}\r\n".format(fileContent)
                        except OSError:
                            response = "HTTP/1.1 404 Not Found\r\n"

                else:
                    response = "HTTP/1.1 404 Not Found\r\n"
        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n"
        
        return response

"""     def parseRequest(self, requestData):
        if requestData.startswith(b"GET "):
            response = "HTTP/1.1 200 OK\r\n"
            pathStartIndex = requestData.index(b"/") + 1
            name = requestData[pathStartIndex : requestData.index(b" ", pathStartIndex, len(requestData))]
            print("pathname:", name)
            try:
                file = open(b"www/"+name, "r")
                fileContent = file.read()
                response = "HTTP/1.1 200 OK\r\nContent Type: text/html; charset=utf-8\r\n" + fileContent + "\r\n"
            except OSError:
                #file = open(b"www/"+name+"/index.html", "r")
                response = "HTTP/1.1 404 Not Found\r\n"

        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n"
        return response """



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
