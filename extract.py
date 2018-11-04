import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


USR = os.environ['YAHOO_FOOTBALL_USER']
PWD = os.environ['YAHOO_FOOTBALL_PASS']
chrome = r'C:\Program Files (x86)\Google\Chrome\chromedriver.exe'


def parse_table(trs, td_num, roster0):
    for tr in trs:
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
        ID = href[href.rindex('/') + 1:]
        team, position = div2.find_element_by_xpath('.//span').text.split(' - ')

        # Display projected points
        a = div1.find_element_by_xpath('.//span/a')
        # ActionChains(driver).move_to_element(a).click(a).perform()
        # Scroll show this row is shown
        ActionChains(driver).move_to_element(a).perform()
        driver.execute_script("arguments[0].click();", a)
        sleep(1)  # TODO: wait only until projection box shown

        # Parse table
        points = []
        trs2 = driver.find_elements_by_xpath("//table[@class='teamtable']/tbody/tr")
        sleep(1)  # TODO: wait only until the table is populated
        for tr2 in trs2:
            # Scroll until the row is shown
            # ActionChains(driver).move_to_element(tr2).perform()
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

        # Display
        print(','.join([ID, name, team, position, str(roster0), *points]))


# Start browser
driver = webdriver.Chrome(executable_path=chrome)
driver.implicitly_wait(10)  # seconds

# Navigate to Yahoo
URL = 'https://football.fantasysports.yahoo.com/f1/542214/11'
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

# Zoom out and full screen
driver.maximize_window()
# driver.execute_script("document.body.style.zoom='50%'")
# sleep(1)

# Parse current players
for i in range(3):
    trs = driver.find_elements_by_xpath("//table[@id='statTable{}']/tbody/tr".format(i))
    parse_table(trs, 2, 1)

# Parse available players
URL = 'https://football.fantasysports.yahoo.com/f1/542214/players?status=A&pos=O&cut_type=9&stat1=S_PN4W&myteam=0&sort=PTS&sdir=1'
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs, 1, 0)

# Parse next page
URL = 'https://football.fantasysports.yahoo.com/f1/542214/players?status=A&pos=O&cut_type=9&stat1=S_PN4W&myteam=0&sort=PTS&sdir=1&count=25'
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs, 1, 0)

# Parse defenses
URL = 'https://football.fantasysports.yahoo.com/f1/542214/players?&sort=PTS&sdir=1&status=A&pos=DEF&stat1=S_PN4W&jsenabled=1'
driver.get(URL)
# Loop over table
trs = driver.find_elements_by_xpath("//div[@id='players-table']/div[@class='players']/table/tbody/tr")
parse_table(trs, 1, 0)

# Close browser
driver.quit()
