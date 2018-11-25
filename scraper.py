import csv
from datetime import datetime
import json
from os import makedirs
from os.path import exists, join
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


# Start timer
startTime = datetime.now()

# Read Yahoo credentials from json
with open('credentials.json') as f:
    credentials = json.load(f)
USR = credentials['username']
PWD = credentials['password']
LG = credentials['league']

# Create data file
folder = 'data'
if not exists(folder):
    makedirs(folder)
filename = join(folder, '{:%Y-%m-%d %H%M} week '.format(startTime))


def parse_table(trs2, td_num=1, roster0=False, owner_col_offset=3):
    for tr in trs2:
        # Parse player info
        tds = tr.find_elements_by_xpath('.//td')
        try:
            div1 = tds[td_num].find_element_by_xpath('.//div/div')
        except NoSuchElementException:
            continue

        # Basic playing info
        div2 = div1.find_element_by_xpath('.//div')
        a = div2.find_element_by_xpath('.//a')
        name = a.text
        href = a.get_attribute('href')
        pid = href[href.rindex('/') + 1:]
        team, position = div2.find_element_by_xpath('.//span').text.split(' - ')

        # Owner
        if roster0:
            owner = 'self'
        else:
            div3 = tds[td_num + owner_col_offset].find_element_by_xpath('.//div')
            owner = div3.text

        # Display projected points
        a = div1.find_element_by_xpath('.//span/a')
        driver.execute_script("arguments[0].click();", a)

        # Retry until table contains values
        tries = 0
        while tries < 10:
            td2 = driver.find_element_by_css_selector("table.teamtable tbody tr td:nth-child(5)")
            point = td2.text
            if point != '':
                break
            tries += 1
            sleep(0.1)

        # Parse table
        points = []
        trs2 = driver.find_elements_by_xpath("//table[@class='teamtable']/tbody/tr")
        for tr2 in trs2:
            tds2 = tr2.find_elements_by_xpath('.//td')
            point = tds2[4].text
            if point == '':
                continue
            elif point == '-':
                point = '0'
            elif point[0] == '*':
                point = point[1:]
            points.append(point)

        # Close overlay
        a = driver.find_element_by_css_selector('a.yui3-ysplayernote-close')
        driver.execute_script("arguments[0].click();", a)

        # Write output
        with open(filename + '.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([pid, name, team, position, roster0, owner, *points])


# Start browser
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)  # seconds

# Navigate to Yahoo
URL = 'https://football.fantasysports.yahoo.com/f1/{}/11'.format(LG)
driver.get(URL)
assert 'Yahoo' in driver.title

# Login
elem = driver.find_element_by_id('login-username')
elem.send_keys(USR)
elem = driver.find_element_by_id('login-signin')
driver.execute_script("arguments[0].click();", elem)
elem.send_keys(Keys.RETURN)
elem = driver.find_element_by_id('login-passwd')
elem.send_keys(PWD)
elem = driver.find_element_by_id('login-signin')
driver.execute_script("arguments[0].click();", elem)

# Parse current week
elem = driver.find_element_by_css_selector('a.flyout_trigger span.flyout-title')
week = elem.text.split(' ')[1]
filename += week

# Parse current players
for i in range(3):
    trs = driver.find_elements_by_xpath("//table[@id='statTable{}']/tbody/tr".format(i))
    parse_table(trs, 2, True)

# Parse available players
URL = 'https://football.fantasysports.yahoo.com/f1/' \
    '{}/players?status=A&pos=O&cut_type=9&stat1=S_PN4W&myteam=0&sort=PTS&sdir=1'.format(LG)
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs)

# Parse next page
URL = 'https://football.fantasysports.yahoo.com/f1/' \
    '{}/players?status=A&pos=O&cut_type=9&stat1=S_PN4W&myteam=0&sort=PTS&sdir=1&count=25'.format(LG)
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs)

# Parse defenses
URL = 'https://football.fantasysports.yahoo.com/f1/' \
    '{}/players?&sort=PTS&sdir=1&status=A&pos=DEF&stat1=S_PN4W&jsenabled=1'.format(LG)
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs, owner_col_offset=2)

# Close browser
driver.quit()

# Print runtime
print('Total runtime: {}'.format(datetime.now() - startTime))
