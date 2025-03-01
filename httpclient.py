#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def get_port(self, url):
        parsed_url = urllib.parse.urlparse(url)
        port = parsed_url.port

        if port:
            return port
        
        else: #port doesn't exist so we make it based off of scheme
            scheme = parsed_url.scheme
            if scheme == 'https':
                port = 443

            else:
                port = 80

            return port

    def get_code(self, data):
        """
            Returns the code of the HTTP response from the host
            code is returned as an int
        """
        # quick way to get code is that second element in list returned will be code
        # print("DATA: ", data)
        code = data.split(' ')[1]

        return int(code)

    def get_headers(self,data):
        '''
            Useless function
        '''
        # don't need for anything
        return None

    def get_body(self, data):
        # response header and body separated by two lines (one is empty white space)
        body = data.split("\r\n\r\n")[1] # the body will be after the spacing

        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.hostname
        port = self.get_port(url)

        if not path:
            path = '/'

        self.connect(host, port)

        request = f"GET {path}?{query} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "User-Agent: me\r\n"
        request += "Connection: close\r\n\r\n"
        request += ""

        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        #print("Start\n")
        #print(request)
        #print("\nend\n")
        self.socket.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        # if no args passed, encode as an empty string
        if not args:
            args = ""
        
        args = urllib.parse.urlencode(args)
        path = parsed_url.path
        host = parsed_url.hostname
        port = self.get_port(url)

        if not path:
            path = '/'

        self.connect(host, port)

        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {len(args)}\r\n"
        request += "Connection: close\r\n\r\n"
        request += args

        self.sendall(request)
        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)
        
        self.socket.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
