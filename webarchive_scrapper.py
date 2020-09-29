import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import config


def requests_retry_session(
    retries=5,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_site_map(url, limit=200000):
	params = {
		'url': url,
		'fl': 'timestamp,original',
		'matchType': 'prefix',
		'filter': ['statuscode:200', 'mimetype:text/html'],
		'collapse': ['original', 'timestamp'],
		'limit': limit

	}
	response = requests.get('https://web.archive.org/web/timemap/json', params=params)

	return response.json()



def get_archive_version(timestamp, url):
	query_url_path = '/web/{timestamp}/{url}'.format(timestamp=timestamp, url=url)
	headers = {'path': query_url_path,
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate'}
	query_url = 'https://web.archive.org' + query_url_path
	response = requests_retry_session(retries=10).get(query_url, headers=headers)
	# move logging here
	return response

