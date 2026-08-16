# Configuration and constants used in the script. Update values or set environment variables.
import os

USERNAME = os.getenv("NAUKRI_USERNAME") or "mnsrnithin9@gmail.com"
PASSWORD = os.getenv("NAUKRI_PASSWORD") or "Nithin9@"
MOBILE = os.getenv("NAUKRI_MOBILE") or "8886744899"
ORIGINAL_RESUME_PATH = os.getenv("ORIGINAL_RESUME_PATH") or "Nithin_SDE_Resume.pdf"
RESUME_NAME = os.getenv("RESUME_NAME") or "Nithin_SDE_Resume.pdf"
MODIFIED_RESUME_PATH = os.getenv("MODIFIED_RESUME_PATH") or "Nithin_SDE_Resume.pdf"
HEADLESS = (os.getenv("HEADLESS") or "True").lower() in ("true", "1", "yes")
UPDATE_PDF = (os.getenv("UPDATE_PDF") or "False").lower() in ("true", "1", "yes")
AUTO_DOWNLOAD_RESUME = (os.getenv("AUTO_DOWNLOAD_RESUME") or "True").lower() in ("true", "1", "yes")
DOWNLOAD_DIR = os.path.abspath(os.getenv("DOWNLOAD_DIR") or "downloads")
NAUKRI_LOGIN_URL = "https://www.naukri.com/nlogin/login"
NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


