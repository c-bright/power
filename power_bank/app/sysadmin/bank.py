import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_webase_address(user_name="sysadmin", url=None):
    """
    无头模式获取 WeBASE 私钥管理页面中的用户地址。
    """
    if url is None:
        url = os.environ.get("WEBASE_PRIVATE_KEY_URL", "http://127.0.0.1:5002/WeBASE-Front/#/privateKeyManagement")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--window-size=1920,1080')
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        xpath = f"//span[text()='{user_name}']/ancestor::td/preceding-sibling::td[2]//span"
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        address = element.text.strip()
        return address
    except Exception as e:
        print(f"获取地址失败: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    admin_address = get_webase_address("sysadmin")
    if admin_address:
        print(f"获取成功，地址为: {admin_address}")
