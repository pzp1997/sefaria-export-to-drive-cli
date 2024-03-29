from __future__ import unicode_literals

import StringIO

import requests
from oauth2client import client
from oauth2client import tools
import httplib2
import apiclient


def sefaria_sheet_api(endpoint):
    """Makes request to Sheet API `endpoint` and returns JSON data"""
    return requests.get('http://www.sefaria.org/api/sheets/{}'.format(
        endpoint)).json()


def create_html_string(sheet):
    """Makes an html string from the JSON formatted sheet"""
    html = ''

    title = unicode(sheet.get('title', '')).strip()
    html += '{}<br>'.format(title)

    # author = ''
    # html += '<em>Source Sheet by <a href="{}">{}</a><em>'

    for source in sheet['sources']:
        if 'text' in source:
            english = unicode(source['text'].get('en', '')).strip()
            hebrew = unicode(source['text'].get('he', '')).strip()
            html += '{}<br>{}'.format(english, hebrew)
        elif 'outsideText' in source:
            html += unicode(source['outsideText']).strip()
        elif 'comment' in source:
            html += unicode(source['comment']).strip()
        html += '<br><br>'

    return html.encode('utf-8')


class Store(object):
    """Stub class to get run_flow to work."""
    def put(self, credential):
        """Stub method that will be called in run_flow."""
        pass


def get_credentials(client_secrets='client_secrets.json',
                    scope_='https://www.googleapis.com/auth/drive',
                    redirect_uri_='http://localhost:8080'):
    """Authenticates the user with Google via OAuth 2.0"""
    flow = client.flow_from_clientsecrets(client_secrets,
                                          scope=scope_,
                                          redirect_uri=redirect_uri_)
    credentials = tools.run_flow(flow, Store(), None)
    return credentials


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('drive', 'v3', http=http)

    sheet_id = raw_input("Input sheet id: ")
    sheet = sefaria_sheet_api(sheet_id)

    file_metadata = {
        'name': sheet.get('title', '').strip(),
        'mimeType': 'application/vnd.google-apps.document'
    }

    media = apiclient.http.MediaIoBaseUpload(
        StringIO.StringIO(create_html_string(sheet)),
        mimetype='text/html',
        resumable=True)

    new_file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id,webViewLink').execute()

    print '{} (id: {})'.format(new_file['webViewLink'], new_file['id'])


if __name__ == '__main__':
    main()
