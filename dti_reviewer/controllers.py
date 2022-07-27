import cherrypy
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PACKAGE_DIR_PATH = Path(__file__).parent
STATIC_DIR_PATH = PACKAGE_DIR_PATH / 'static'

env = Environment(loader=FileSystemLoader(str(PACKAGE_DIR_PATH / 'templates')))

config = {
  'global' : {
    'tools.proxy.on':True,
    'server.socket_host' : '0.0.0.0',
    'server.socket_port' : 8080,
    'server.thread_pool' : 8
  },
  '/' : {'tools.staticdir.root': str(STATIC_DIR_PATH)},
  '/css' : {
    'tools.staticdir.on'  : True,
    'tools.staticdir.dir' : str(STATIC_DIR_PATH / 'css')
  },
  '/fonts' : {
    'tools.staticdir.on'  : True,
    'tools.staticdir.dir' : str(STATIC_DIR_PATH / 'fonts')
  }
}
print(str(STATIC_DIR_PATH / 'css'))

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        template = env.get_template('index.html.j2')
        return template.render()

if __name__ == '__main__':
    cherrypy.quickstart(HelloWorld())