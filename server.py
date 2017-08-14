import sys
import os
import BaseHTTPServer
import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import clientsvgparser as cp
import clientelement as celm
import segment as sgm
import classify as clf
import svgparser as sp
import connect as cn
import tikzdraw as td


# -------------------------------------------------------------------------------

class baseCase(object):
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'

# -------------------------------------------------------------------------------

class case_no_file(baseCase):
    # File or directory does not exist.

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

# -------------------------------------------------------------------------------

class case_cgi_file(baseCase):

    def run_cgi(self, handler):
        cmd = "python " + handler.full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        handler.send_content(data)

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)

# -------------------------------------------------------------------------------

class case_existing_file(baseCase):
    # File exists.

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)

# -------------------------------------------------------------------------------

class case_directory_index_file(baseCase):
    # Serve index.html page for a directory.

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

# -------------------------------------------------------------------------------

class case_directory_no_index_file(baseCase):
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''

    def list_dir(self, handler, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            handler.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            handler.handle_error(msg)

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.list_dir(handler, handler.full_path)
# -------------------------------------------------------------------------------

class case_always_fail(baseCase):
    # Base case if nothing else worked.

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))
# -------------------------------------------------------------------------------

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # If the requested path maps to a file, that file is served.
    # If anything goes wrong, an error page is constructed.
    Cases = [case_no_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_directory_no_index_file(),
             case_always_fail()]

    # How to display an error.
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def _writeheaders(self):
        print "path" + self.path
        print self.headers
        print "_writeheaders"
        self.send_response(200);
        self.send_header('Content-type', 'text/html');
        self.end_headers()

    # Classify and handle request.
    def do_GET(self):

        try:
            # Figure out what exactly is being requested.
            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    def do_POST(self):
        self._writeheaders()
        length = self.headers.getheader('content-length')
        nbytes = int(length)
        data = self.rfile.read(nbytes)

        result_data = self.handle_data(data)
        self.wfile.write(result_data)
        # self.wfile.write("\nit works well\n")

    # dataObject: post_data (JSONString) client -> server
    # return: response_data (JSONString) server -> client
    def handle_data(self, data_object):
        # parse JSON data
        client_data = json.loads(data_object)
        filenames = ['circle0.svg','circle1.svg','circle2.svg','circle3.svg','morphism0.svg','morphism1.svg','morphism2.svg']
        labels = [1,1,1,1,-1,-1,-1]
        nodeclf = clf.trainSVM(filenames,labels,1,1)
        paths_str = client_data[u'pathdata'].split('\n')[1:]
        pathlist = [celm.path(cp.parseStroke(path_str)) for path_str in paths_str]
        hypotheses = sgm.segmentPath(pathlist,train=False)
        [corr_pathlist,intersect] = sgm.correctPathlist(pathlist)        
        normal = clf.predict(hypotheses,nodeclf)
        if corr_pathlist!=None:
            correction = clf.predict(corr_pathlist,nodeclf)
        else:
            correction = None           
        [wirelist,dotlist,morphismlist] = cn.findWinner(normal,correction,intersect)
        tree = sp.loadFile('blank.svg')
        cn.drawOutput(tree,wirelist,dotlist,morphismlist)
        try:
            latex_command = td.create_diagram(dotlist,morphismlist,wirelist)
        except:
            pass
        response_data = json.dumps(latex_command)
        return response_data

    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    # Send actual content.
    def send_content(self, content, status=200):
        print "sentContent"
        self.send_response(status)

        content_type = "text/html"

        if "js" in str(self.path):
            content_type = "text/javascript"
        if "css" in str(self.path):
            content_type = "text/css"
        if "woff?v=4.7.0" in str(self.path):
            content_type = "application/font-woff"
        if "ttf?v=4.7.0" in str(self.path):
            content_type = "application/font-ttf"            
        if "woff?v=4.7.0" in str(self.path):
        #if self.path.endswith("woff2?v=4.7.0"):
            content_type = "application/font-woff2"

        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

# -------------------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
