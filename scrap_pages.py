from time import sleep
import os
import pandas as pd
from webarchive_scrapper import get_archive_version

import logging

if __name__ == '__main__':
	logging.basicConfig(
		filename='scrapping.log',
		format='%(asctime)s,%(name)s,%(levelname)s,%(message)s',
		level=logging.INFO
	)
	data = pd.read_csv('site_map.csv')
	blacklist = pd.read_csv('scrapping.log', names=['date_scrapped', 'logger', 'message_type', 'timestamp', 'original', 'status'])
	blacklist = blacklist.loc[blacklist['message_type']=='INFO', ['timestamp', 'original']]
	blacklist = set(blacklist.itertuples(index=False, name=None))
	for i, row in data.iterrows():
		timestamp, original = row
		if (str(timestamp), original) not in blacklist:
			url_ending = '/'.join(original.split('/')[3:])
			if '.htm' not in url_ending:
				url_ending = url_ending + '/index.html'
			response = get_archive_version(timestamp, original)
			if response.status_code == 200:
				file_path = 'pages/' + str(timestamp)[:8] + '/' + url_ending
				os.makedirs(os.path.dirname(file_path), exist_ok=True)
				with open(file_path, 'w') as file:
					file.write(response.text)
				logging.info(','.join([str(timestamp), original, '200']))
			else:
				logging.error(','.join([str(timestamp), original, str(response.status_code)]))
			print('scraped', (i, timestamp, original))
			sleep(1)
		else:
			print('skipping', (i, timestamp, original))
