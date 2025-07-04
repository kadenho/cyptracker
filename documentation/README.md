# CrypTracker
## Introduction
CrypTracker is a cryptocurrency tracking app. With it, you can watch, track, and view the price history of cryptocurrencies. \
\
Developed for use on Python 3.10

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Completion](#completion)
- [Credits](#credits)

## Installation
1. Clone the repository at this address:
   - https://git.unl.edu/tthiede2/soft161_milestone_2
2. Download and set up a local MySQL server on your machine using this link: https://dev.mysql.com/downloads/mysql/
   * Note: This project was made using MySQL 8.0 Windows and MySQL 9.0.2 Mac, though it should work for later versions regardless of OS 
3. Make sure you have the following Python Packages installed:
   - requests
   - kivy
   - kivy-garden
   - kivy-garden.matplotlib
   - matplotlib
   - mplfinance
   - pandas
   - sqlalchemy
   - pycoingecko
4. Create a free CoinGeckoAPI demo account to use your own apikey
   1. Go to https://www.coingecko.com and click "Sign Up" in the top right
   2. Go to https://www.coingecko.com/en/developers/dashboard and "Add New Key"
   3. Copy the API Key (should be a string of 27 random characters)
   4. Create the python file 'apikey.py' in the **project directory** and type "COINGECKO_API_KEY = 'your api key'"
      * Note: if forking project in a VCS, NEVER add your apikey file to the VCS to make sure nobody else can use it
      * For git users. add 'CrypTracker\apikey.py' to .gitignore or tell your IDE not to commit it.
   5. The program should now use your api key when making calls
5. Run CrypTracker/main.py in your terminal, or click "Run" in your IDE

## Usage
1. After you have run the program, you will be prompted for a MySQL server password
2. After entering your password, you will be able to view the application's login screen. If you do not see it, you may be tabbed out of the window.
3. You can currently log in or sign up as any user as there is no password associated to a given user
4. You can use the Portfolio tracker to add cryptocurrencies to track, or use the price viewer to view their historical data.

## Tests
1. All methods involved in Creating, Updating, and Deleting database entries are tested in Tests/
2. Each 

## Completion
The following features are planned for this app, with accompanying statuses
   * Ability to log in as multiple users
     * ✅**Complete**, no verification for users but data is properly tied to a given user
   * Ability to add and delete cryptocurrencies to the local database
     * ✅**Complete**, cryptocurrencies are added via API calls and stored via local database
   * Ability to add, update, and delete portfolio entries to the local database
     * ✅**Complete**, entries tied to a user utilize live API data and get stored to the local database 
   * Ability to view the current value, percent change, and composition of your portfolio
     * ✅**Complete**, current value and percent change calculated using API calls when necessary and a Pie Chart can 
     display your portfolio makeup 
   * ✅**Complete**, Ability to view historical price data for different cryptocurrencies stored in the local database
   * ✅**Complete**, Ability to export historical price data as a CSV file
   * ✅**Complete**, Ability to view a graph of a user's portfolio value against time
   * ✅**Complete**, Error handling for invalid inputs 
   * ➖**Partial**, Unit tests for database CUD operations
     * Some Reading operations are not directly tested

## Credits
This project was developed by 
* **Tyler Thiede**, 
* **Paden Outz**, 
* **Kaden Ho**, and 
* **Boston Bailey** 

for the University of Nebraska-Lincoln Software Engineering 161 Course of the 2025 Spring semester instructed by Dr. Shruti Bolman.

### Utilized software:
* Pycharm Professional IDE
* Draw.io diagramming tool for creating ER-diagrams
* Figma professional design tool to create wireframes of GUIs
* Python 3.10
* MySQL Community 8.0 and 9.0.2 for database management
* SQLAlchemy python package for ORM and python database integration
* CoinGeckoAPI for retrieving accurate cryptocurrency data
* "Requests" module for making API calls through CoinGecko
* MatPlotLib, MLPFinance, and Pandas for displaying graphs