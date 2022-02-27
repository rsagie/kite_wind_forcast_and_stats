#this one does not download the openskiron
pyinstaller --noconsole --onefile main.py --name wind_report_v2.1 --add-data="conf\*;conf" --clean --add-binary=./driver/chromedriver.exe;./driver

# Use this one
pyinstaller --onefile main.py --name wind_report_v2.8 --add-data="conf\*;conf" --clean --add-binary=./driver/chromedriver.exe;./driver
