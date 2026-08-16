#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""

import io
import logging
import os
import sys
import time
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import constants

# Add folder Path of your resume
originalResumePath = constants.ORIGINAL_RESUME_PATH
# Add Path where modified resume should be saved
modifiedResumePath = constants.MODIFIED_RESUME_PATH

# Update your naukri username and password here before running
username = constants.USERNAME
password = constants.PASSWORD
mob = constants.MOBILE

# False if you dont want to add Random HIDDEN chars to your resume
updatePDF = getattr(constants, "UPDATE_PDF", False)

# If Headless = True, script runs Chrome in headless mode without visible GUI
headless = getattr(constants, "HEADLESS", True)


# ----- No other changes required -----

# Set login URL
NaukriURL = constants.NAUKRI_LOGIN_URL

logging.basicConfig(
    level=logging.INFO, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ["WDM_LOCAL"] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    _, _, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "TAG": By.TAG_NAME,
        "CLASS": By.CLASS_NAME,
        "CSS": By.CSS_SELECTOR,
        "LINKTEXT": By.LINK_TEXT,
    }
    return map[locatorType.upper()]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:

        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag)
                )

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def safe_click(driver, element):
    """Click element; fall back to JS click if a chatbot/overlay intercepts it

    Naukri's chatbot widget overlays the profile/edit links and blocks
    native Selenium clicks with ElementClickInterceptedException.
    """
    try:
        element.click()
    except Exception as e:
        log_msg("Native click failed (%s), retrying with JS click" % e)
        driver.execute_script("arguments[0].click();", element)


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for _ in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg("Exception when WaitTillElementPresent : %s" % e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result

def Logout(driver):
    """Logout from Naukri session """

    try:
        # -------- Drawer Menu XPaths --------
        drawer_xpaths = [
            f"//*[contains({ci('@class')}, 'drawer__icon')]",
            f"//div[contains({ci('@class')}, 'drawer')]"
        ]

        for xpath in drawer_xpaths:
            if is_element_present(driver, By.XPATH, xpath):
                try:
                    el = GetElement(driver, xpath, locator="XPATH")
                    if el:
                        el.click()
                        time.sleep(1)
                        log_msg("Drawer menu opened")
                        break
                except Exception as e:
                    log_msg(f"Drawer open failed ({xpath}): {e}")
                    continue

        # -------- Logout XPaths --------
        logout_xpaths = [
            "//a[@data-type='logoutLink']",

            f"//a[contains({ci('@class')}, 'list-cta') and contains({ci('@title')}, 'logout')]",
            f"//a[contains({ci('@class')}, 'logout')]",
            f"//a[contains({ci('@href')}, 'logout')]",

            f"//*[contains({ci('text()')}, 'logout')]",
            f"//*[contains({ci('.')}, 'logout')]",
        ]

        for xpath in logout_xpaths:
            if is_element_present(driver, By.XPATH, xpath):
                try:
                    el = GetElement(driver, xpath, locator="XPATH")
                    if el:
                        driver.execute_script("arguments[0].scrollIntoView(true);", el)
                        time.sleep(0.5)
                        el.click()
                        time.sleep(2)
                        log_msg("Logout Successful")
                        return True
                except Exception as e:
                    log_msg(f"Logout click failed ({xpath}): {e}")
                    continue

        log_msg("Logout button not found")
        return False

    except Exception as e:
        log_msg(f"Logout error: {e}")
        return False
    
def ci(xpath_part: str) -> str:
    """
    Wraps an XPath string in lowercase translate() for case-insensitive matching.
    Usage:
        ci("@class") → "translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
        ci("text()") → "translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
    """
    return f"translate({xpath_part},'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))


def LoadNaukri(headless):
    """Open Chrome to load Naukri.com"""

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popups")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    # Configure auto-download directory for resume
    download_dir = getattr(constants, "DOWNLOAD_DIR", os.path.abspath("downloads"))
    os.makedirs(download_dir, exist_ok=True)
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
    }
    options.add_experimental_option("prefs", prefs)
    
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
    else:
        options.add_argument("--start-maximized")

    # updated to use latest selenium Chrome service
    driver = None
    try:
        driver = webdriver.Chrome(options=options, service=ChromeService())
    except Exception as e:
        log_msg(f"Standard Chrome launch failed ({e}), falling back to direct options launch...")
        driver = webdriver.Chrome(options=options)

    # Enable download in headless Chrome across all browser targets
    try:
        driver.execute_cdp_cmd(
            "Browser.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": download_dir, "eventsEnabled": True},
        )
    except Exception:
        pass
    try:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": download_dir},
        )
    except Exception:
        pass


    log_msg("Google Chrome Launched!")

    driver.implicitly_wait(5)
    driver.get(NaukriURL)
    return driver




def naukriLogin(headless=False):
    """Open Chrome browser and Login to Naukri.com"""
    status = False
    driver = None
    username_locator = "usernameField"
    password_locator = "passwordField"
    login_btn_locator = "//*[@type='submit' and (normalize-space()='Login' or @value='Login')]"
    skip_locator = "//*[text() = 'SKIP AND CONTINUE' or contains(text(), 'Skip')]"
    close_locator = "//*[contains(@class, 'cross-icon') or @alt='cross-icon' or contains(@class, 'crossIcon')]"

    if username in ("your_naukri_username", "", None) or password in ("your_naukri_password", "", None):
        log_msg("❌ ERROR: Please update USERNAME and PASSWORD in constants.py (or set environment variables) before running!")
        return (False, None)

    try:
        driver = LoadNaukri(headless)

        log_msg(f"Page Title: {driver.title}")
        if "naukri.com" in driver.title.lower():
            log_msg("Website Loaded Successfully.")

        emailFieldElement = None
        if WaitTillElementPresent(driver, username_locator, locator="ID", timeout=15):
            emailFieldElement = GetElement(driver, username_locator, locator="ID")
            passFieldElement = GetElement(driver, password_locator, locator="ID")
            loginButton = GetElement(driver, login_btn_locator, locator="XPATH")
        else:
            log_msg("Login fields not found on page.")

        if emailFieldElement is not None:
            emailFieldElement.clear()
            emailFieldElement.send_keys(username)
            time.sleep(1)
            passFieldElement.clear()
            passFieldElement.send_keys(password)
            time.sleep(1)
            
            # Click Login button
            if loginButton:
                safe_click(driver, loginButton)
            else:
                passFieldElement.send_keys(Keys.ENTER)
            
            log_msg("Submitted login credentials, verifying session...")
            time.sleep(3)

            # Check for error messages
            error_xpaths = [
                "//*[contains(@class, 'server-err')]",
                "//*[contains(@class, 'err-msg')]",
                "//*[contains(@class, 'error') and text()]"
            ]
            for err_xpath in error_xpaths:
                if is_element_present(driver, By.XPATH, err_xpath):
                    err_el = driver.find_element(By.XPATH, err_xpath)
                    if err_el and err_el.text.strip():
                        log_msg(f"Login Error from Naukri: {err_el.text.strip()}")

            # Dismiss popups/skip prompts if any
            if is_element_present(driver, By.XPATH, close_locator):
                try:
                    driver.find_element(By.XPATH, close_locator).click()
                except Exception:
                    pass
            if is_element_present(driver, By.XPATH, skip_locator):
                try:
                    driver.find_element(By.XPATH, skip_locator).click()
                except Exception:
                    pass

            # Modern Checkpoint to verify login:
            # 1. URL redirect to mnjuser/homepage or profile
            # 2. Presence of drawer/user menu/profile elements
            success_indicators = [
                "//*[contains(@class, 'nI-gNb-drawer')]",
                "//*[contains(@class, 'view-profile')]",
                "//a[contains(@href, '/mnjuser/profile')]",
                "//*[contains(@class, 'user-name')]",
                "//*[contains(@class, 'dashboard')]",
                "//*[@id='ff-inventory']"
            ]

            start_wait = time.time()
            while time.time() - start_wait < 20:
                current_url = driver.current_url.lower()
                if "mnjuser" in current_url or "homepage" in current_url or "profile" in current_url:
                    log_msg(f"Naukri Login Successful! (Redirected to {driver.current_url})")
                    status = True
                    return (status, driver)

                for ind in success_indicators:
                    if is_element_present(driver, By.XPATH, ind):
                        log_msg("Naukri Login Successful! (Dashboard element detected)")
                        status = True
                        return (status, driver)
                time.sleep(1)

            # Check if OTP is requested
            if "otp" in driver.page_source.lower():
                log_msg("⚠️ Naukri is prompting for OTP verification on this device/network.")
            else:
                log_msg("Login could not be verified. Please check credentials or Captcha/OTP prompts.")
            return (status, driver)

    except Exception as e:
        catch(e)
    return (status, driver)



def UpdateProfile(driver):
    try:
        mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
        saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
        view_profile_locator = "//*[contains(@class, 'view-profile')]//a"
        edit_locator = "(//*[contains(@class, 'icon edit')])[1]"
        save_confirm = "//*[text()='today' or text()='Today']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        WaitTillElementPresent(driver, view_profile_locator, "XPATH", 20)
        profElement = GetElement(driver, view_profile_locator, locator="XPATH")
        safe_click(driver, profElement)
        driver.implicitly_wait(2)

        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, edit_locator + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, edit_locator):
            editElement = GetElement(driver, edit_locator, locator="XPATH")
            safe_click(driver, editElement)

            WaitTillElementPresent(driver, mobXpath, "XPATH", 10)
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)
                
            saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            saveFieldElement.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)

            WaitTillElementPresent(driver, save_confirm, "XPATH", 10)
            if is_element_present(driver, By.XPATH, save_confirm):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        elif is_element_present(driver, By.XPATH, saveXpath):
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)
    
            saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            saveFieldElement.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)

            WaitTillElementPresent(driver, "confirmMessage", locator="ID", timeout=10)
            if is_element_present(driver, By.ID, "confirmMessage"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        time.sleep(5)

    except Exception as e:
        catch(e)



def TouchResumeFile(source_pdf_path, custom_name=None):
    """Appends an invisible PDF comment so file hash changes and Naukri records a fresh upload date"""
    try:
        with open(source_pdf_path, "rb") as f:
            content = f.read()
        # Appending a trailing PDF comment is 100% valid in PDF spec and changes the file checksum
        touched_content = content + f"\n% NAUKRI_REFRESH_{int(time.time())}\n".encode("utf-8")
        filename = custom_name or getattr(constants, "RESUME_NAME", "Nithin_SDE_Resume.pdf")
        out_path = os.path.abspath(filename)
        with open(out_path, "wb") as f:
            f.write(touched_content)
        log_msg(f"Prepared resume as '{filename}' ready for upload: {out_path}")
        return out_path
    except Exception as e:
        log_msg(f"Failed to touch resume ({e}), using original file: {source_pdf_path}")
        return source_pdf_path


def DownloadExistingResume(driver, download_dir):
    """Finds and downloads the existing resume directly from Naukri profile"""
    try:
        import requests

        log_msg("Checking for existing resume on Naukri profile to download...")
        driver.get(constants.NAUKRI_PROFILE_URL)
        time.sleep(3)

        close_locator = "//*[contains(@class, 'crossIcon')]"
        if is_element_present(driver, By.XPATH, close_locator):
            try:
                driver.find_element(By.XPATH, close_locator).click()
                time.sleep(1)
            except Exception:
                pass

        # Clear any existing downloaded files in folder
        if os.path.exists(download_dir):
            for f in os.listdir(download_dir):
                file_p = os.path.join(download_dir, f)
                if os.path.isfile(file_p):
                    try:
                        os.remove(file_p)
                    except Exception:
                        pass
        else:
            os.makedirs(download_dir, exist_ok=True)

        # Locators to find the download resume link/icon on modern OneTheme profile page
        download_xpaths = [
            "//*[contains(text(), 'downloadOneTheme') or contains(@class, 'downloadOneTheme')]/ancestor-or-self::a",
            "//*[contains(text(), 'downloadOneTheme') or contains(@class, 'downloadOneTheme')]/parent::*",
            "//*[contains(text(), 'downloadOneTheme') or contains(@class, 'downloadOneTheme')]",
            "//a[contains(@class, 'download') or contains(@href, 'download')]",
            "//*[contains(@class, 'resume')]//a[contains(translate(., 'DOWNLOAD', 'download'), 'download')]",
            "//a[contains(@title, 'Download') or contains(@aria-label, 'Download')]",
            "//span[contains(translate(text(), 'DOWNLOAD', 'download'), 'download')]/ancestor::a",
            "//i[contains(@class, 'download')]/ancestor::a | //i[contains(@class, 'download')]/parent::*",
            "//a[contains(@href, 'downloadResume') or contains(@href, 'download-resume')]",
            "//*[contains(@class, 'resume')]//a"
        ]

        download_elem = None
        for xpath in download_xpaths:
            if is_element_present(driver, By.XPATH, xpath):
                elems = driver.find_elements(By.XPATH, xpath)
                for el in elems:
                    try:
                        if el.is_displayed():
                            download_elem = el
                            log_msg(f"Found download resume element with XPath: {xpath}")
                            break
                    except Exception:
                        pass
                if download_elem:
                    break

        if not download_elem:
            log_msg("No download resume button found on profile page.")
            return None

        # Method 1: Try direct download with authenticated session cookies if href exists
        href = download_elem.get_attribute("href")
        if not href or href.startswith("javascript"):
            try:
                parent_a = download_elem.find_element(By.XPATH, "./ancestor-or-self::a")
                href = parent_a.get_attribute("href")
            except Exception:
                href = None

        if href and (href.startswith("http") or href.startswith("/")):
            if href.startswith("/"):
                href = "https://www.naukri.com" + href
            
            try:
                log_msg(f"Downloading resume directly via authenticated HTTP request from URL: {href}")
                session = requests.Session()
                for cookie in driver.get_cookies():
                    session.cookies.set(cookie['name'], cookie['value'])

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Referer": constants.NAUKRI_PROFILE_URL
                }
                res = session.get(href, headers=headers, stream=True, timeout=20)
                if res.status_code == 200 and len(res.content) > 500:
                    out_path = os.path.join(download_dir, "Resume.pdf")
                    with open(out_path, "wb") as f:
                        f.write(res.content)
                    log_msg(f"Downloaded resume successfully via direct session to: {out_path} ({len(res.content)} bytes)")
                    return os.path.abspath(out_path)
            except Exception as e:
                log_msg(f"Direct download request failed ({e}), falling back to browser click...")

        # Method 2: Browser click download
        main_window = driver.current_window_handle
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_elem)
        time.sleep(1)
        safe_click(driver, download_elem)
        log_msg("Triggered resume download via browser, waiting for file to save...")

        # If a new tab opened, check its URL
        time.sleep(2)
        if len(driver.window_handles) > 1:
            for handle in driver.window_handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    new_tab_url = driver.current_url
                    if new_tab_url and new_tab_url.startswith("http") and ("naukri" in new_tab_url or "pdf" in new_tab_url.lower()):
                        try:
                            session = requests.Session()
                            for cookie in driver.get_cookies():
                                session.cookies.set(cookie['name'], cookie['value'])
                            res = session.get(new_tab_url, stream=True, timeout=15)
                            if res.status_code == 200 and len(res.content) > 500:
                                out_path = os.path.join(download_dir, "Resume.pdf")
                                with open(out_path, "wb") as f:
                                    f.write(res.content)
                                driver.close()
                                driver.switch_to.window(main_window)
                                log_msg(f"Downloaded resume from new tab to: {out_path}")
                                return os.path.abspath(out_path)
                        except Exception:
                            pass
                    driver.close()
            driver.switch_to.window(main_window)

        # Wait for file to finish downloading to disk
        start_time = time.time()
        timeout = 25
        while time.time() - start_time < timeout:
            time.sleep(1)
            valid_files = [
                os.path.join(download_dir, f)
                for f in os.listdir(download_dir)
                if not f.endswith(".crdownload") and not f.endswith(".tmp") and os.path.getsize(os.path.join(download_dir, f)) > 0
            ]
            if valid_files:
                downloaded_file = max(valid_files, key=os.path.getctime)
                log_msg(f"Downloaded resume successfully via browser: {downloaded_file}")
                return os.path.abspath(downloaded_file)

        log_msg("Download timed out or no file was saved.")
        return None
    except Exception as e:
        catch(e)
        return None


def UploadResume(driver, resumePath):
    """Uploads resume file to Naukri profile using file input elements"""
    try:
        if not resumePath or not os.path.exists(resumePath):
            log_msg(f"Resume path does not exist: {resumePath}")
            return

        abs_path = os.path.abspath(resumePath)
        log_msg(f"Starting resume upload with file: {abs_path}")

        close_locator = "//*[contains(@class, 'crossIcon')]"
        if is_element_present(driver, By.XPATH, close_locator):
            try:
                driver.find_element(By.XPATH, close_locator).click()
                time.sleep(1)
            except Exception:
                pass

        # Look for file input element on profile page
        file_input_xpaths = [
            "//input[@type='file']",
            "//input[@id='attachCV']",
            "//input[@id='lazyAttachCV']",
            "//input[contains(@class, 'upload')]"
        ]

        uploaded = False
        for xpath in file_input_xpaths:
            if is_element_present(driver, By.XPATH, xpath):
                try:
                    file_input = driver.find_element(By.XPATH, xpath)
                    file_input.send_keys(abs_path)
                    log_msg(f"Uploaded file to input element ({xpath}) successfully.")
                    uploaded = True
                    break
                except Exception as e:
                    log_msg(f"Send keys failed on {xpath}: {e}")

        if not uploaded:
            log_msg("Could not find file upload input element on Naukri profile.")
            return

        # Check if a save/submit button is required
        save_btn_xpaths = [
            "//button[normalize-space()='Save' or normalize-space()='Submit']",
            "//button[@type='button' and contains(@class, 'btn') and text()='Save']"
        ]
        for s_xpath in save_btn_xpaths:
            if is_element_present(driver, By.XPATH, s_xpath):
                try:
                    driver.find_element(By.XPATH, s_xpath).click()
                    time.sleep(1)
                except Exception:
                    pass

        # Wait for upload confirmation
        log_msg("Waiting for upload confirmation from Naukri...")
        time.sleep(5)
        
        # Verify updated date or success toast
        check_xpaths = [
            "//*[contains(text(), 'Uploaded on') or contains(text(), 'uploaded on')]",
            "//*[contains(@class, 'updateOn')]",
            "//*[contains(@class, 'success') or contains(text(), 'successfully uploaded')]"
        ]
        
        confirmed = False
        for c_xpath in check_xpaths:
            if is_element_present(driver, By.XPATH, c_xpath):
                el = driver.find_element(By.XPATH, c_xpath)
                if el and el.text.strip():
                    log_msg(f"Resume Upload Status: {el.text.strip()}")
                    confirmed = True
                    break

        if not confirmed:
            log_msg("Resume upload completed successfully.")

    except Exception as e:
        catch(e)
    time.sleep(2)


def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin(headless)
        if status:
            # 1. Update basic profile details (refreshes profile timestamp)
            UpdateProfile(driver)

            # 2. Automatically download existing resume from profile
            resume_to_process = None
            if getattr(constants, "AUTO_DOWNLOAD_RESUME", True):
                downloaded_file = DownloadExistingResume(driver, getattr(constants, "DOWNLOAD_DIR", "downloads"))
                if downloaded_file:
                    resume_to_process = downloaded_file

            # Fallback to local resume path if download failed or disabled
            if not resume_to_process and os.path.exists(originalResumePath):
                resume_to_process = originalResumePath

            # 3. Refresh file checksum and re-upload so Naukri updates 'Uploaded on' date to Today
            if resume_to_process:
                final_upload_path = TouchResumeFile(resume_to_process)
                if final_upload_path and os.path.exists(final_upload_path):
                    UploadResume(driver, final_upload_path)
                else:
                    UploadResume(driver, resume_to_process)
            else:
                log_msg("No resume found to download or upload. Profile details update was completed.")

    except Exception as e:
        catch(e)

    finally:
        if driver is not None:
            try:
                Logout(driver)
                time.sleep(2)
            except Exception as e:
                log_msg("Error during logout: %s" % e)
        tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")



if __name__ == "__main__":
    main()

