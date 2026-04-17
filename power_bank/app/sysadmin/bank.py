
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_webase_address(user_name="sysadmin", url=None):
    """
    无头模式获取 WeBASE 私钥管理页面的用户地址
    """
    if url is None:
        url = os.environ.get("WEBASE_PRIVATEKEY_URL", "http://127.0.0.1:5002/WeBASE-Front/#/privateKeyManagement")
    # 1. 配置
    options = Options()
    options.add_argument("--headless=new")


    # 建议设置窗口大小，防止某些响应式页面在无头模式下由于尺寸过小而隐藏元素
    options.add_argument('--window-size=1920,1080')
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # 2. 动态构建 XPath
        # 逻辑：寻找包含指定用户名的行 (tr)，并在该行中寻找以 '0x' 开头的 span
        # xpath = f"//tr[contains(., '{user_name}')]//span[contains(text(), '0x')]"
        xpath = f"//span[text()='{user_name}']/ancestor::td/preceding-sibling::td[2]//span"
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        address = element.text.strip()

        return address


    except Exception as e:
        print(f"获取地址失败: {e}")
        return None

    finally:
        driver.quit()


# --- 使用示例 ---
if __name__ == "__main__":
    admin_address = get_webase_address("sysadmin")
    if admin_address:
        print(f" 获取成功！地址为: {admin_address}")
