import sae
import seger

def app(environ, start_response):
  status = '200 OK'
  response_headers = [('Content-type', 'text/plain')]
  start_response(status, response_headers)
  return seger.run(environ['QUERY_STRING'])

application = sae.create_wsgi_app(app)
