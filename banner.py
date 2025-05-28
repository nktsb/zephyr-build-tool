import os
import pyfiglet
from dotenv import load_dotenv

load_dotenv()
company_name = os.environ.get("COMPANY_NAME")
ascii_banner = pyfiglet.figlet_format(company_name)
print(ascii_banner)