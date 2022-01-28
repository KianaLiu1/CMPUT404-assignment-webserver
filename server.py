#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

# Copyright 2022 Yuetong(Kiana) Liu

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

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
        # print ("Got a request of: %s\n" % self.data)
        # https://stackoverflow.com/questions/41918836/how-do-i-get-rid-of-the-b-prefix-in-a-string-in-python
        # https://www.w3schools.com/python/ref_string_split.asp
        method = self.data.split()[0].decode('utf-8')
        if method == "GET":
            # Getting the path specified
            path = self.data.splitlines()[0].split()[1].decode('utf-8')
            

            # The webserver can return index.html from directories (paths that end in /)
            if path[-1] == "/":
                # check if path is a parent directory of current 
                path = "www" + path                            
                if ".." in path and not self.path_validation(path):
                    self.not_found_404()
                else:
                    path = path + "index.html"
                    if not os.path.exists(path):
                        self.not_found_404()
                    else:
                        self.ok_200(path)

            # Get specified file
            elif ("html" in path or "css" in path) and path[-1] != "/":               
                path = "www" + path
                
                # https://stackoverflow.com/questions/3812849/how-to-check-whether-a-directory-is-a-sub-directory-of-another-directory
                if ".." in path and not self.path_validation(path):
                    self.not_found_404()

                elif not os.path.exists(path):
                    self.not_found_404()
                else:
                    self.ok_200(path)
            # use 301 to correct paths 
            elif path[-1] != "/":
                path = "www" + path + "/"
            
                if ".." in path and not self.path_validation(path):
                    self.not_found_404()

                elif not os.path.exists(path):
                    self.not_found_404()
                else:
                    self.redirect_301(path)
            # https://www.geeksforgeeks.org/python-os-path-exists-method/#:~:text=os.-,path.,open%20file%20descriptor%20or%20not.
            # If paths not found, serve 404 errors
            elif not os.path.exists("www" + path):
                self.not_found_404()
            else:
                self.ok_200("www" + path)
        else:
            self.method_not_allowed_405()

    
    def ok_200(self, path):
        content = self.get_content(path)
        # https://reqbin.com/Article/HttpGet#:~:text=GET%20is%20an%20HTTP%20method,on%20data%20on%20the%20server.
        server_response = "HTTP/1.1 200 OK\r\n"
        content_type = "Content-Type:"+self.get_content_type(path) + "\r\n"
        self.send_info(server_response, content, content_type)

    def not_found_404(self):
        # https://www.tutorialspoint.com/http/http_responses.htm
        content = "<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1>\
            <p>The requested URL /t.html was not found on this server.</p></body></html>"
        server_response = "HTTP/1.1 404 Not Found\r\n"
        content_type = "Content-Type:"+"html" + "\r\n"
        self.send_info(server_response, content, content_type)
    def redirect_301(self, path):
        # https://reqbin.com/Article/HttpGet#:~:text=GET%20is%20an%20HTTP%20method,on%20data%20on%20the%20server.
        server_response = "HTTP/1.1 301 Moved Permanently\r\n"
        content = "<html><head><title>301 Moved Permanently</title></head><body><h1>Not Found</h1>\
            <p>The requested URL /t.html was not found on this server.</p></body></html>"
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
        location = "Location: http://"+str(HOST)+str(PORT)+path+"\r\n"
        self.request.sendall(bytearray(server_response,'utf-8')) 
        self.request.sendall(bytearray("Server: What is this for??\r\n",'utf-8')) 
        self.request.sendall(bytearray("Content-Length:"+str(len(location))+"\r\n",'utf-8'))       
        self.request.sendall(bytearray("Connection: closed\r\n\r\n",'utf-8'))
        self.request.sendall(bytearray(location,'utf-8'))

    # Handling methods other than get
    def method_not_allowed_405(self):
        content = "<html><head><title>405 Method Not Allowed</title></head><body><h1>Not Found</h1>\
            <p>The requested method is not allowed on this server.</p></body></html>"
        server_response = "HTTP/1.1 405 Method Not Allowed\r\n"
        content_type = "Content-Type:"+"html" + "\r\n"
        self.send_info(server_response, content, content_type)
    
    # read file
    def get_content(self, path):
        file_pt = open(path, "r")
        content = ""
        for letter in file_pt:
            content += letter
        file_pt.close()
        return content
    
    def get_content_type(self,path):
        if "css" in path:
            return "text/css"
        else:
            return "text/html"
    
    def send_info(self,server_response, content, content_type):
        self.request.sendall(bytearray(server_response,'utf-8'))
        self.request.sendall(bytearray("Server: What is this for??\r\n",'utf-8')) 
        self.request.sendall(bytearray("Content-Length:"+str(len(content))+"\r\n",'utf-8')) 
        self.request.sendall(bytearray(content_type,'utf-8'))            
        self.request.sendall(bytearray("Connection: closed\r\n\r\n",'utf-8'))
        self.request.sendall(bytearray(content,'utf-8'))
    
    # https://stackoverflow.com/questions/3812849/how-to-check-whether-a-directory-is-a-sub-directory-of-another-directory
    def path_validation(self, path):
        path_absolute = os.path.abspath(path)
        current_absolue = os.path.abspath("www")
        if os.path.commonprefix([path_absolute, current_absolue]) != current_absolue:
            return False
        return True
        
 
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
