from webarchive_scrapper import get_site_map
import csv
import config

if __name__ == '__main__':
	site_map = get_site_map('http://admlist.ru')
	with open('site_map.csv', 'w') as file:
		writer = csv.writer(file)
		writer.writerows(site_map)