from webdriver_helper import get_webdriver
import time 
def test_web():
    driver = get_webdriver()
    driver = get('http://www.baidu.com/')
    time.sleep(2)
    print("test run")
    driver.quit()
