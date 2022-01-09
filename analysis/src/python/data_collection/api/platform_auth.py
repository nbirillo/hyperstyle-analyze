import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests


class OauthHandler(BaseHTTPRequestHandler):
    """ Handler process authorization code request and ask platform for access token."""

    def do_GET(self):  # noqa: N802
        path = urlparse(self.path)
        query = parse_qs(path.query)

        if 'code' not in query:
            self.send_response(404)

        code = query['code'][0]

        auth = requests.auth.HTTPBasicAuth(self.server.client_id, self.server.client_secret)
        response = requests.post(
            '{host}/oauth2/token/'.format(host=self.server.platform_host),
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:{port}'.format(port=self.server.port),
            },
            auth=auth,
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.server.platform_token = response.json()['access_token']
        self.wfile.write(response.json()['access_token'].encode())


class OauthServer(HTTPServer):
    """ Server initiate authorization process by opening authorization page
    and handling authorization request using OauthHandler."""

    def __init__(self, platform_host: str, client_id: str, client_secret: str, port: int):
        self.platform_host = platform_host
        self.platform_token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.port = port
        super().__init__(('', port), OauthHandler)

    def open_oauth_page(self):
        """ Open authorization page. """

        oauth_url = '{host}/oauth2/authorize/?response_type=code&client_id={client_id}'.format(
            host=self.platform_host,
            client_id=self.client_id)
        webbrowser.open(oauth_url)

    def get_token(self) -> Optional[str]:
        """ Execute token request. """

        self.handle_request()
        return self.platform_token
