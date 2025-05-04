# Standard Library
import csv
import re
import sys
from datetime import datetime, date, timedelta, time

import mplfinance as mpf
import pandas as pd
import requests
# SQLAlchemy
import sqlalchemy
# Kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.properties import StringProperty, NumericProperty, ColorProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
# Kivy Garden
from kivy_garden.matplotlib import FigureCanvasKivyAgg
# Matplotlib
from matplotlib import pyplot as plt
from matplotlib.dates import ConciseDateFormatter, AutoDateLocator
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

# Disables flooding the console with debug messages on graph render
plt.set_loglevel(level='warning')

# Your Modules
from Tokenstaller.cryptos import Crypto, PortfolioEntry, CryptoPrice, ValueCheck, User, CryptoDatabase

# External API
from pycoingecko import CoinGeckoAPI
from apikey import COINGECKO_API_KEY

coin_gecko_api = CoinGeckoAPI(demo_api_key=COINGECKO_API_KEY)


def text_color_from_value(text, lower, upper):
    """
    Yields an RGBA list for color based on the value of a string (red for negative, green for positive, black for 0)
    :param text: Text of the label whose color is to be change
    :param lower: The highest value to return pure red [1, 0, 0, 1]
    :param upper: The lowest value to return pure green [0, 1, 0, 1]
    :return: RGBA list of colors between 0 and 1
    >>> text_color_from_value('-50',-100,100)
    [0.0, 0.5, 0.0, 1.0]
    >>> text_color_from_value('-25',-100,100)
    [1.0, 0.75, 0.0, 1.0]
    >>> text_color_from_value('-1000',0,100)
    [1.0, 0.0, 0.0, 1.0]
    """
    default_text_color = [0, 0, 0, 1]
    green = [0, 1, 0, 1]
    red = [1, 0, 0, 1]
    green_differentials = [green[i] - default_text_color[i] for i in range(4)]
    # 0, 1, 0
    red_differentials = [red[i] - default_text_color[i] for i in range(4)]
    # Remove non-integers and store as an int
    value = int(re.sub('[^0-9-]', '', text))
    if value > 0:
        value = min(value, upper)
        for i in range(4):
            default_text_color[i] += (value / upper) * green_differentials[i]
    if value < 0:
        value = max(value, lower)
        for i in range(4):
            default_text_color[i] += (value / lower) * red_differentials[i]
    return default_text_color


# Main App Screens
class MySQLPasswordScreen(Screen):
    def reset_page(self):
        self.ids.password_text_input.text = ''


class PriceTrendsScreen(Screen):
    pass


class UserLoginScreen(Screen):
    pass


class CreateProfileScreen(Screen):
    pass


class MainDashboardScreen(Screen):
    def reset_page(self):
        pass


class AboutHelpScreen(Screen):
    pass


# Portfolio App Screen Classes

class AddDeleteScreen(Screen):
    def reset_page(self):
        pass

    def update_page(self):
        pass


def popup_update_text_size(instance):
    # Method to make popups adjust their text size to the size of the popup window
    instance.children[0].children[0].children[0].text_size = instance.children[0].children[0].children[0].size
    return


class PortfolioMenuScreen(Screen):
    pass


class ManageCryptocurrenciesScreen(Screen):
    pass


class AddCryptocurrencyScreen(AddDeleteScreen):
    def reset_page(self):
        self.ids.crypto_name.text = ''
        self.ids.crypto_symbol.text = ''


class DeleteCryptocurrencyScreen(AddDeleteScreen):
    def reset_page(self):
        self.ids.spinner_delete_crypto.text = 'Crypto ID' if len(
            self.ids.spinner_delete_crypto.text) > 0 else 'No Cryptos'
        self.ids.delete_crypto_name.text = ''
        self.ids.delete_crypto_symbol.text = ''

    def update_page(self):
        spinner_text = self.ids.spinner_delete_crypto.text
        if spinner_text == 'Crypto ID' or spinner_text == 'No Cryptos':
            return
        crypto = app.session.query(Crypto).filter(Crypto.crypto_id == spinner_text).first()
        self.ids.delete_crypto_name.text = crypto.name
        self.ids.delete_crypto_symbol.text = crypto.symbol


class ManagePortfolioEntriesScreen(Screen):
    pass


class AddPortfolioEntryScreen(AddDeleteScreen):
    def reset_page(self):
        self.ids.spinner_crypto_id.text = 'Crypto ID'
        self.ids.date_text.hint_text = 'YYYY-MM-DD'
        self.ids.date_text.text = ''
        self.ids.quantity_text.hint_text = '1'
        self.ids.quantity_text.text = ''


class UpdatePortfolioEntryScreen(AddDeleteScreen):
    def reset_page(self):
        self.ids.spinner_update_portfolio.text = 'Entry ID' if len(app.portfolio_info) != 0 else 'No Entries'
        self.ids.update_spinner_crypto_id.text = 'Crypto ID'
        self.ids.update_date_text.hint_text = 'YYYY-MM-DD'
        self.ids.update_date_text.text = ''
        self.ids.update_quantity_text.hint_text = '1'
        self.ids.update_quantity_text.text = ''

    def update_page(self):
        # Retrieve the entry with the same id as the user selects from the spinner
        spinner_text = self.ids.spinner_update_portfolio.text
        numbers_in_spinner_text = re.match(r'\d', spinner_text)
        if numbers_in_spinner_text is None:
            return
        entry = app.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == int(spinner_text)).first()
        self.ids.update_spinner_crypto_id.text = entry.crypto_id
        self.ids.update_date_text.hint_text = 'YYYY-MM-DD'
        self.ids.update_date_text.text = str(entry.timestamp.date())
        self.ids.update_quantity_text.hint_text = '1'
        self.ids.update_quantity_text.text = str(entry.quantity)


class DeletePortfolioEntryScreen(AddDeleteScreen):
    def reset_page(self):
        self.ids.spinner_delete_portfolio.text = 'Entry ID' if len(app.portfolio_info) != 0 else 'No Entries'
        self.ids.delete_crypto_id.text = 'Crypto ID'
        self.ids.delete_date_text.text = 'YYYY-MM-DD'
        self.ids.delete_quantity_text.text = '0'

    def update_page(self):
        # Retrieve the entry with the same id as the user selects from the spinner
        spinner_text = self.ids.spinner_delete_portfolio.text
        numbers_in_spinner_text = re.match(r'\d', spinner_text)
        if numbers_in_spinner_text is None:
            return
        entry = app.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == int(spinner_text)).first()
        self.ids.delete_crypto_id.text = entry.crypto_id
        self.ids.delete_date_text.text = str(entry.timestamp.date())
        self.ids.delete_quantity_text.text = str(entry.quantity)


class CheckPortfolioScreen(Screen):
    pass

    def on_enter(self):
        app.add_value_check()


class PieChartScreen(Screen):
    pass


class SelectCryptoScreen(Screen):
    def reset_page(self):
        pass


class ViewHistoryScreen(Screen):
    crypto_id = StringProperty()
    crypto_name = StringProperty()
    crypto_values = ListProperty()
    crypto_percent_change = StringProperty()
    graph_type = StringProperty('line')
    graph_range = StringProperty('90_day')

    def reset_page(self):
        pass


class Text(Label):
    pass


class FormattedButton(Button):
    pass


class BackButton(FormattedButton):
    pass


class ScreenBoxLayout(BoxLayout):
    pass


class SelectCryptoBox(BoxLayout):
    crypto_symbol = StringProperty()
    crypto_name = StringProperty()
    crypto_value = StringProperty()
    crypto_percent_change = StringProperty()
    searched_cryptos_list = ListProperty()
    crypto_id = StringProperty()


def find_most_recent_timestamp(values_list):
    """
    Take a list of values and return the most recent value
    """
    most_recent_value = values_list[0]  # set the first value as the most recent value
    for value in values_list:  # iterate through the values
        if value.timestamp > most_recent_value.timestamp:  # if the value is more recent
            most_recent_value = value  # set it as the most recent value
    return most_recent_value  # return most recent value


# Main App Class
class CrypTrackerApp(App):
    # Main app properties
    username = StringProperty()
    # Portfolio app properties
    title_text = StringProperty('Portfolio App')
    user_id = NumericProperty(1)
    background_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    portfolio_report_date = StringProperty('')
    portfolio_report_previous_date = StringProperty('')
    portfolio_report_total = NumericProperty(0)
    portfolio_report_change_from_previous = NumericProperty(0)
    portfolio_report_change_from_investment = NumericProperty(0)

    def build(self):
        inspector.create_inspector(Window, self)
        self.sm = ScreenManager()
        self.sm.add_widget(MySQLPasswordScreen(name='MySQLPasswordScreen'))
        self.sm.add_widget(UserLoginScreen(name='UserLoginScreen'))
        self.sm.add_widget(CreateProfileScreen(name='CreateProfileScreen'))
        self.sm.add_widget(MainDashboardScreen(name='MainDashboardScreen'))
        self.sm.add_widget(AboutHelpScreen(name='AboutHelpScreen'))
        return self.sm

    def on_historical_price_button_press(self):
        self.sm.current = 'SelectCryptoScreen'

    # Main app buttons
    def on_login_button_press(self):
        screen = self.sm.get_screen('UserLoginScreen')
        screen2 = self.sm.get_screen('MainDashboardScreen')
        spinner_text = screen.ids.username_selector_spinner.text
        if spinner_text != 'Select An Account':
            user = self.session.query(User).filter(User.username == spinner_text).first()
            if user:
                app = App.get_running_app()
                app.username = user.username
                app.user_id = user.user_id
                screen.ids.username_selector_message_label = ''
                screen2.ids.menu_username.text = f'Hello, {user.username}!'
                self.sm.current = 'MainDashboardScreen'
            else:
                screen.ids.username_selector_message_label = 'Username not found'
        else:
            screen.ids.username_selector_message_label.text = 'Select an Account'

    def on_create_username_page_button_press(self):
        self.sm.current = 'CreateProfileScreen'

    def on_switch_user_button_press(self):
        self.sm.current = 'UserLoginScreen'

    def on_about_help_button_press(self):
        self.sm.current = 'AboutHelpScreen'

    def on_about_help_back_button_press(self):
        self.sm.current = 'MainDashboardScreen'

    def on_portfolio_button_press(self):
        self.sm.current = 'Portfolio Menu'

    def on_price_trends_button_press(self):
        self.sm.current = 'PriceTrendsScreen'

    def on_price_trends_back_button_press(self):
        self.sm.current = 'MainDashboardScreen'

    def on_enter_password_button_press(self):
        try:
            screen = self.sm.get_screen('MySQLPasswordScreen')
            password = screen.ids.password_text_input.text
            url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
            self.crypto_database = CryptoDatabase(url)
            self.session = self.crypto_database.create_session()
            users = self.session.query(User).all()  # make any database call to elicit an error in the password
            self.update_usernames()
            self.sm.add_widget(PortfolioMenuScreen(name='Portfolio Menu'))
            self.sm.add_widget(ManageCryptocurrenciesScreen(name='Manage Cryptocurrencies'))
            self.sm.add_widget(AddCryptocurrencyScreen(name='Add Cryptocurrency'))
            self.sm.add_widget(DeleteCryptocurrencyScreen(name='Delete Cryptocurrency'))
            self.sm.add_widget(ManagePortfolioEntriesScreen(name='Manage Portfolio Entries'))
            self.sm.add_widget(AddPortfolioEntryScreen(name='Add Portfolio Entry'))
            self.sm.add_widget(UpdatePortfolioEntryScreen(name='Update Portfolio Entry'))
            self.sm.add_widget(DeletePortfolioEntryScreen(name='Delete Portfolio Entry'))
            self.sm.add_widget(CheckPortfolioScreen(name='Check Portfolio'))
            self.sm.add_widget(PieChartScreen(name='Pie Chart'))
            self.sm.add_widget(SelectCryptoScreen(name='SelectCryptoScreen'))
            self.sm.add_widget(ViewHistoryScreen(name='ViewHistoryScreen'))
            self.sm.add_widget(PriceTrendsScreen(name='PriceTrendsScreen'))
            self.sm.current = 'UserLoginScreen'
        except sqlalchemy.exc.ProgrammingError:
            self.display_popup('Password Error', 'Please re-enter your password and try again.', 'MySQLPasswordScreen')
            self.sm.current = 'MySQLPasswordScreen'

    def on_create_username_button_press(self):
        screen = self.sm.get_screen('CreateProfileScreen')
        username = screen.ids.new_username_text_input.text
        if screen.ids.new_username_text_input.text == '':
            screen.ids.username_message_label.text = 'Please enter a username.'
            return
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            screen.ids.username_message_label.text = 'Username already exists.'
            return
        try:
            new_user = User(username=username)
            self.session.add(new_user)
            self.session.commit()
            screen.ids.username_message_label = ''
            self.update_usernames()
            self.sm.current = 'UserLoginScreen'
        except Exception as e:
            print('Error with adding user to MySQL', e)

    def update_usernames(self):
        try:
            users = self.session.query(User).all()
            usernames = [user.username for user in users]
            self.usernames = usernames
            screen = self.sm.get_screen('UserLoginScreen')
            screen.ids.username_selector_spinner.values = usernames
        except Exception as e:
            print('Error with updating usernames', e)

    # Portfolio methods
    def change_screen(self, screen):
        if screen != '':
            self.root.current = screen

    @property
    def crypto_ids(self):
        """
        Returns all the crypto_ids stored in the database with error-handling
        :return: List of crypto_ids stored in the database
        """
        ids = []
        try:
            cryptos = self.session.query(Crypto)
            crypto_count = cryptos.count()
            for i in range(crypto_count):
                ids.append(cryptos[i].crypto_id)
        except SQLAlchemyError:
            self.session.rollback()
            self.title_text = 'Invalid Password. Please restart with the right password'
        return ids

    @property
    def portfolio_info(self):
        """
        Returns a list of entry_ids from the portfolio_entries table
        """
        entry_info = []
        try:
            entries = self.session.query(PortfolioEntry).filter(PortfolioEntry.user_id == self.user_id)
            entry_count = entries.count()
            for i in range(entry_count):
                entry_info.append(str(entries[i].entry_id))
        except SQLAlchemyError:
            self.session.rollback()
            self.title_text = 'Invalid Password. Please restart with the right password'

        return entry_info

    def display_popup(self, title, text, next_screen):
        """
        Displays a popup widget with some default values already set.
        Its text does not always fit in the popup, this is due to the Label widget
        not being able to have its attributes properly read from inside the popup.
        :param title: Title of the popup appearing at the top of the window
        :param text: Message in the popup
        :param next_screen: Screen to move to after dismissing popup
        :return: None
        """
        label = Label(text=text, halign='center', valign='middle')
        popup = Popup(title=title, size_hint=(0.5, 0.5), content=label)
        popup.children[0].children[2].outline_width = 0
        popup.open()
        popup.bind(on_dismiss=lambda instance: self.change_screen(next_screen))
        popup.bind(on_open=lambda instance: popup_update_text_size(instance))
        # Reset the data of the current page, needed for when next_screen is the current screen
        self.root.get_screen(self.root.current).reset_page()
        return

    def display_pie_chart(self, crypto_quantities):
        plt.clf()  # clear the current plot
        crypto_ids = [crypto_id for crypto_id in crypto_quantities]
        current_holdings = [crypto_quantities[crypto_id][2] for crypto_id in crypto_quantities]
        try:
            self.generate_pie_chart(crypto_ids, current_holdings)  # generate the chart
        except ValueError:
            self.display_popup('Value Error',
                               'You currently have $0.00 in holdings, '
                               'so a pie chart cannot be generated.',
                               'Portfolio Menu')

    def generate_pie_chart(self, crypto_ids, holdings):
        """
        Take the crypto_ids and current holdings and generate a pie chart for the screen
        """
        chart_screen = self.root.get_screen('Pie Chart')
        labels = crypto_ids  # set the labels to be the crypto_ids
        values = holdings  # set the values to the current holdings of a crypto

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title('Current Holdings')  # title the chart
        chart_screen.ids.pie_chart_box.clear_widgets()  # remove the old chart
        chart_screen.ids.pie_chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # add the new chart
        plt.close()

    def add_crypto(self, name, symbol):
        """
        Adds a crypto to the database via a name and symbol.
        Although such instances exist, the user cannot add two cryptos with the
        same name and symbol since this method will not be able to give them
        distinct ids.
        :param name: Name of the crypto to be added
        :param symbol: Symbol of the crypto to be added
        :return: None
        """

        """
        Filters the full list of coins using the lambda function, then gets converted
        to a list so it can access each dictionary fitting the criteria.
        Result is a list of dictionaries with keys {'id':, 'name':, 'symbol':}
        that have the same name and symbol as the arguments to this method,
        then you take the value of the dictionary's id.
        Error handled for case of there being no crypto that fits.
        """

        try:
            added_crypto_id = list(filter(lambda dictionary: dictionary["symbol"] == symbol.lower().strip() \
                                                             and dictionary["name"] == name.strip(),
                                          coin_gecko_api.get_coins_list()))[0]['id']
        except IndexError:
            popup_title = 'Crypto not found'
            popup_message = f'Crypto with name {name} and symbol {symbol} not found.'
            self.display_popup(popup_title, popup_message, 'Add Cryptocurrency')
            return
        crypto = Crypto(name=name, symbol=symbol, crypto_id=added_crypto_id)
        if not (len(name) > 0 and len(symbol) > 0):
            self.display_popup('Empty Data', 'Please enter data for all fields.', 'Add Cryptocurrency')
            return
        if len(name) > 64 or len(symbol) > 64:
            self.display_popup('Data Too Long', 'At least one your entries exceeded 64 characters.',
                               'Add Cryptocurrency')
            return
        count = self.session.query(Crypto).filter(Crypto.crypto_id == crypto.crypto_id).count()
        if count != 0:
            self.display_popup('Duplicate Entry',
                               f'Crypto with id \'{crypto.crypto_id}\' is already in the database.',
                               'Add Cryptocurrency')
            return
        self.session.add(crypto)
        self.session.commit()
        self.display_popup('Entry Added', 'Crypto entry added.', 'Portfolio Menu')

    def delete_crypto(self, crypto_id):
        # Don't delete if the spinner text is not set to a value
        if crypto_id == 'Crypto ID' or crypto_id == 'No Cryptos':
            self.display_popup('Empty Data',
                               'Please select a crypto to delete, if there are any.',
                               'Delete Cryptocurrency')
            return
        deleted_crypto = self.session.query(Crypto).filter(Crypto.crypto_id == crypto_id).first()
        affected_entries = self.session.query(PortfolioEntry).filter(PortfolioEntry.crypto_id == crypto_id)
        # Don't delete a crypto that is used in an entry
        if affected_entries.count() == 0:
            self.session.delete(deleted_crypto)
            self.session.commit()
        else:
            self.display_popup("Can't Remove Crypto",
                               'This crypto is currently used in a portfolio entry, '
                               'so it cannot be deleted.',
                               next_screen='Delete Cryptocurrency')
            return
        self.display_popup('Deleted Crypto',
                           f'Crypto "{crypto_id}" successfully deleted',
                           'Portfolio Menu')

    def add_crypto_price(self, crypto_id, timestamp, price):
        """

        :param crypto_id:
        :param timestamp:
        :param price: Price in dollars
        :return:
        """
        crypto_price = CryptoPrice(crypto_id=crypto_id, timestamp=timestamp, price=price * 100)
        # If an entry in crypto_prices with that timestamp and crypto already exists, exit
        if self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id).filter(
                CryptoPrice.timestamp == timestamp).count() != 0:
            return
        self.session.add(crypto_price)
        self.session.commit()

    def modify_portfolio_entry(self, crypto_id=None, entry_date=None, quantity=None, operation=None, entry_id=None,
                               ):
        """
        Either adds, updates, or deletes a portfolio entry to the database using its id, a date, and a quantity
        :param crypto_id: id of the crypto
        :param entry_date: Date of entry
        :param quantity: Quantity of the crypto bought at that date
        :param operation: 'Add', 'Delete', or 'Update'
        :param entry_id: ID of the entry to be modified in case of Updating or Deleting
        :return: None
        """

        # Logic for deleting a portfolio entry
        if operation == 'Delete':
            try:
                entry = self.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == entry_id).one()
            except SQLAlchemyError:
                self.display_popup('No Portfolio Entry Found',
                                   f'There is no portfolio entry with id "{entry_id}"',
                                   'Manage Portfolio Entries')
                return
            self.session.delete(entry)
            self.session.commit()
            self.display_popup('Entry Deleted',
                               'Portfolio entry successfully deleted.',
                               'Manage Portfolio Entries')
            return

        if crypto_id == 'Crypto ID':
            self.display_popup('No Crypto ID Selected', 'Please select a Crypto ID.', f'{operation} Portfolio Entry')
            return

        if len(quantity) == 0:
            self.display_popup('Empty Data', 'Please enter in a quantity.', f'{operation} Portfolio Entry')
            return

        try:
            entry_date = date.fromisoformat(entry_date)
            # Sets the time element of the entry_date to be midnight
            entry_date = datetime.combine(entry_date, time())
            # Date in format 'DD-MM-YYYY' as required by the CoinGecko API
            adjusted_date = f'{entry_date.day:02d}-{entry_date.month:02d}-{entry_date.year:04d}'
        except ValueError as error:
            self.display_popup('Date Error', str(error), f'{operation} Portfolio Entry')
            return

        if entry_date < datetime.combine(date.today(), time()) - timedelta(days=364) or entry_date > datetime.combine(
                date.today(), time()):
            self.display_popup('Date Out of Range',
                               'Please enter a date within the last 364 days.',
                               f'{operation} Portfolio Entry')
            return

        if int(quantity) > 10000:
            self.display_popup('Value Error', 'Quantity is too high, please enter a lower quantity',
                               f'{operation} Portfolio Entry')
            return
        # Logic for adding or updating an entry
        if operation == 'Add' or operation == 'Update':
            # Add a price entry for the given date if none are found in the Database
            if self.session.query(CryptoPrice).filter(CryptoPrice.timestamp == entry_date).filter(
                    CryptoPrice.crypto_id == crypto_id).count() == 0:
                try:
                    historic_coin_data = coin_gecko_api.get_coin_history_by_id(crypto_id, adjusted_date)
                    price = historic_coin_data['market_data']['current_price']['usd']
                    self.add_crypto_price(crypto_id, entry_date, price)
                except SQLAlchemyError:
                    self.display_popup('Database Error',
                                       'This crypto did not exist at your selected date. Please select a later date.',
                                       f'{operation} Portfolio Entry')
                except KeyError:
                    self.display_popup('API Error',
                                       'This crypto did not exist at your selected date. Please select a later date.',
                                       f'{operation} Portfolio Entry')
                    return
            try:
                investment = self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id).filter(
                    CryptoPrice.timestamp == entry_date).first().price * int(
                    quantity)
            except SQLAlchemyError as error:
                print(error)
                self.session.rollback()
                self.display_popup('Invalid Date',
                                   'This crypto did not exist at this date, please choose a later date',
                                   f'{operation} Portfolio Entry')
                return
            # Logic for adding an entry
            if operation == "Add":
                portfolio_entry = PortfolioEntry(crypto_id=crypto_id,
                                                 timestamp=entry_date,
                                                 quantity=quantity,
                                                 investment=investment,
                                                 user_id=self.user_id)
                try:
                    self.session.add(portfolio_entry)
                    self.session.commit()
                except SQLAlchemyError as error:
                    print(str(error), self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id \
                                                                             and CryptoPrice.timestamp == entry_date).first().price)
                    self.session.rollback()
                    self.display_popup('Database Error',
                                       'There likely isn\'t a price for that crypto at that date'
                                       ' in the database. You can try manually adding one.',
                                       'Add Portfolio Entry')
                self.display_popup('Entry Added', 'Portfolio Entry successfully added', 'Manage Portfolio Entries')
                return
            # Logic for updating a portfolio entry
            try:
                entry = self.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == entry_id).one()
            except SQLAlchemyError:
                self.display_popup('No Portfolio Entry Found',
                                   f'There is no portfolio entry with id "{entry_id}"',
                                   'Manage Portfolio Entries')
                return
            entry.crypto_id = crypto_id
            entry.timestamp = entry_date
            entry.quantity = quantity
            entry.investment = investment
            self.session.commit()
            self.display_popup(title='Entry Updated',
                               text='Portfolio entry successfully updated.',
                               next_screen='Manage Portfolio Entries')

    def add_value_check(self, timestamp=datetime.now()):
        """
        Adds a value check to the database containing a date, total value, and percentage change.
        :param self: Object on which the call is being made
        :param timestamp: Date of the value check, defaults to the current date.
        :return: None
        """
        value_checks = self.session.query(ValueCheck).filter(ValueCheck.user_id == self.user_id)
        number_of_value_checks = value_checks.count()
        # Boolean decides if percent_change should also compare against the previous value check or only initial investment
        is_first_value_check = number_of_value_checks == 0
        previous_value_check = value_checks[
            number_of_value_checks - 1] if not is_first_value_check else None
        total_value = 0
        total_initial_investment = 0
        change_from_previous = None
        crypto_quantities = self.get_quantities_and_investments()

        for crypto_id in crypto_quantities:
            total_initial_investment += crypto_quantities[crypto_id][1]
            total_value += crypto_quantities[crypto_id][2]

        if not is_first_value_check:
            previous_value = previous_value_check.total_value
            change_from_previous = 100 * (total_value - previous_value) // abs(previous_value) \
                if previous_value != 0 else None

        change_from_investment = 100 * (total_value - total_initial_investment) // abs(total_initial_investment) \
            if total_initial_investment != 0 else 0

        value_check = ValueCheck(timestamp=timestamp, total_value=total_value,
                                 change_from_previous=change_from_previous,
                                 user_id=self.user_id, change_from_investment=change_from_investment)
        try:
            self.session.add(value_check)
            self.session.commit()
        except sqlalchemy.exc.DataError as data_error:
            print(data_error)
            self.session.rollback()
            self.display_popup('Data out of Range',
                               'The total value of your portfolio was beyond what the database can store.',
                               '')
            total_value = 2 ** 31 - 1
            value_check = ValueCheck(timestamp=timestamp, total_value=total_value,
                                     change_from_previous=change_from_previous,
                                     user_id=self.user_id, change_from_investment=change_from_investment)
            self.session.add(value_check)
            self.session.commit()
        self.portfolio_report_date = str(timestamp.date())
        self.portfolio_report_total = total_value

        if previous_value_check is not None:
            self.portfolio_report_previous_date = str(previous_value_check.timestamp.date())
        else:
            self.portfolio_report_previous_date = 'N/A'

        if change_from_previous is not None:
            self.portfolio_report_change_from_previous = round(change_from_previous, 2)
        else:
            self.portfolio_report_change_from_previous = 0.0

        self.portfolio_report_change_from_investment = change_from_investment
        self.display_pie_chart(crypto_quantities)

    def get_quantities_and_investments(self):
        """
        Returns a dictionary of 'crypto_id' string keys and [quantity, total investment, total held] list values
        Note: both total investment and total held should be integers in cents
        not made for the same time.
        :return:
        """
        # stores the current time with seconds and microseconds set to 0, since coingecko updates prices per minute
        current_time = datetime.now() - timedelta(seconds=datetime.now().second,
                                                  microseconds=datetime.now().microsecond)
        entries = self.session.query(PortfolioEntry).filter(PortfolioEntry.user_id == self.user_id)
        # Dict of entry.crypto_id: (total quantity, total investment, total held)
        crypto_quantities_prices = dict()
        # Populate dictionary with every crypto in the user's portfolio and set their quantity and initial investment
        for entry in entries:
            # Added that id to the dictionary with default values if not already included
            crypto_quantities_prices.setdefault(entry.crypto_id, [0, 0, 0])
            crypto_quantities_prices[entry.crypto_id][0] += entry.quantity
            crypto_quantities_prices[entry.crypto_id][1] += entry.investment
        # Set the price held at the current time for each crypto
        for crypto_id in crypto_quantities_prices:
            crypto_price = self.session.query(CryptoPrice).filter(
                and_(CryptoPrice.timestamp == current_time, CryptoPrice.crypto_id == crypto_id))
            # Add new price to database if none are found at the current time
            if crypto_price.count() == 0:
                price = round(coin_gecko_api.get_price(crypto_id, 'usd')[crypto_id]['usd'], 2)
                self.add_crypto_price(crypto_id, current_time, price)
                self.session.commit()
            current_price = self.session.query(CryptoPrice).filter(
                and_(CryptoPrice.crypto_id == crypto_id, CryptoPrice.timestamp == current_time)).first()
            crypto_quantities_prices[crypto_id][2] = crypto_quantities_prices[crypto_id][0] * current_price.price
        return crypto_quantities_prices

    def populate_list(self):
        """
        Creates the initial list displayed on the screen
        """
        screen = self.root.get_screen('SelectCryptoScreen')  # gets the screen
        list_box = screen.ids.cryptos_list_boxlayout  # gets the box that holds the rows
        list_box.searched_cryptos_list = []
        coins = self.pull_api_coins()
        for coin in coins:
            list_box.searched_cryptos_list.append(self.assemble_tuple(coin))
        try:
            list_box.searched_cryptos_list = sorted(list_box.searched_cryptos_list, key=lambda x: x[0])
            screen = self.root.get_screen('SelectCryptoScreen')
            screen.ids.cryptos_list_boxlayout.clear_widgets()  # clear the old list
            screen.ids.select_crypto_text_input.text = ''
            self.display_cryptos(list_box, screen)
        except TypeError:
            self.display_popup('API Error',
                               'You are attempting to call data from the API too fast. Please wait and try again.',
                               'MainDashboardScreen')

    def repopulate_list(self):
        """
        Repopulates the list of cryptos based on the search query
        """
        screen = self.root.get_screen('SelectCryptoScreen')  # get screen
        search_query = screen.ids.select_crypto_text_input.text.lower().strip()  # get the search query
        list_box = screen.ids.cryptos_list_boxlayout  # get box that holds the rows
        list_box.searched_cryptos_list = []

        if search_query == '':
            self.populate_list()  # populate the list with default values
        else:

            try:
                coins = self.pull_api_coins()
                for coin in coins:
                    if search_query in coin['symbol'].lower() or search_query in coin['name'].lower():
                        list_box.searched_cryptos_list.append(self.assemble_tuple(coin))

                screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove old rows
                self.display_cryptos(list_box, screen)
            except TypeError:
                self.display_popup('API Error',
                                   'You are attempting to call data from the API too fast. Please wait and try again.',
                                   'MainDashboardScreen')

    @staticmethod
    def pull_api_coins():
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        coins = response.json()
        return coins

    def assemble_tuple(self, coin):
        """
        retrieve data and package into a tuple to be added to the list
        """
        try:
            crypto_symbol = coin['symbol']  # retrieve crypto's symbol
            crypto_name = coin['name']  # retrieve crypto's name
            today_price = str(coin['current_price'])
            percent_change = str(round(coin['price_change_percentage_24h'], 2))
            crypto_id = coin['id']
            assembled_tuple = (
                crypto_symbol, crypto_name, today_price, percent_change, crypto_id)  # package data into a tuple
            return assembled_tuple  # return the assembled tuple
        except TypeError:
            self.display_popup('API Error',
                               'You are attempting to call data from the API too fast. Please wait and try again.',
                               'MainDashboardScreen')

    @staticmethod
    def display_cryptos(list_box, screen):
        if len(list_box.searched_cryptos_list) >= 5:
            for i in range(5):
                (symbol, name, value, percent_change, crypto_id) = list_box.searched_cryptos_list[i]  # retrieve values
                screen.ids.cryptos_list_boxlayout.add_widget(
                    SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                    crypto_percent_change=percent_change, crypto_id=crypto_id))  # display values
        elif 0 < len(list_box.searched_cryptos_list) <= 4:
            for i in range(len(list_box.searched_cryptos_list)):
                (symbol, name, value, percent_change, crypto_id) = list_box.searched_cryptos_list[i]  # retrieve values
                screen.ids.cryptos_list_boxlayout.add_widget(
                    SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                    crypto_percent_change=percent_change, crypto_id=crypto_id))  # display values
        elif len(list_box.searched_cryptos_list) == 0:  # if no cryptos match the search query
            screen.ids.cryptos_list_boxlayout.add_widget(  # notify user no results were found
                Text(text='No results found', font_size=25))

    def move_list_back(self):
        """
        Displays the previous 5 cryptos in the list if possible
        """
        screen = self.root.get_screen('SelectCryptoScreen')  # retrieve cryptos
        list_box = screen.ids.cryptos_list_boxlayout  # retrieve list
        if list_box.searched_cryptos_list:  # as long as the list exists
            first_box = screen.ids.cryptos_list_boxlayout.children[-1]  # retrieve the first item
            first_tuple = (first_box.crypto_symbol, first_box.crypto_name, first_box.crypto_value,
                           first_box.crypto_percent_change, first_box.crypto_id)  # repackage the data into a tuple
            index = list_box.searched_cryptos_list.index(
                first_tuple)  # search list for the matching tuple to find the current index
            if index > 4:  # if there are at least 5 widgets preceding to be displayed
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # clear the widgets
                for i in range(5):
                    (symbol, name, value, percent_change, crypto_id) = list_box.searched_cryptos_list[
                        index - 5 + i]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                        crypto_percent_change=percent_change, crypto_id=crypto_id))  # display crypto

    def move_list_forward(self):
        """
        Displays the next cryptos in the list if possible
        """
        screen = self.root.get_screen('SelectCryptoScreen')
        list_box = screen.ids.cryptos_list_boxlayout
        if list_box.searched_cryptos_list:
            last_box = screen.ids.cryptos_list_boxlayout.children[0]  # select the last displayed crypto
            last_tuple = (last_box.crypto_symbol, last_box.crypto_name, last_box.crypto_value,
                          last_box.crypto_percent_change, last_box.crypto_id)  # repackage the values into a tuple

            index = list_box.searched_cryptos_list.index(last_tuple)  # find the index of that crypto

            if index < (len(list_box.searched_cryptos_list) - 5):  # if there are at least 5 cryptos left
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(5):  # for the next 5 cryptos
                    (symbol, name, value, percent_change, crypto_id) = list_box.searched_cryptos_list[
                        i + index + 1]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                        crypto_percent_change=percent_change, crypto_id=crypto_id))  # display crypto
            elif index != len(list_box.searched_cryptos_list) - 1:  # if there is at least 1 crypto left
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(len(list_box.searched_cryptos_list) - index - 1):  # for the remaining cryptos
                    (symbol, name, value, percent_change, crypto_id) = list_box.searched_cryptos_list[
                        i + index + 1]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                        crypto_percent_change=percent_change, crypto_id=crypto_id))  # display crypto

    def select_crypto(self, crypto_id):
        """
        set the values for the show history screen
        """
        selected_crypto = coin_gecko_api.get_coin_by_id(crypto_id)
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.crypto_id = selected_crypto['id']
        screen.crypto_name = selected_crypto['name']
        api_values = coin_gecko_api.get_coin_market_chart_by_id(selected_crypto['id'], 'usd', 90)
        screen.crypto_values = []
        for value in api_values['prices']:
            assembled_tuple = (datetime.fromtimestamp(value[0] / 1000), round(value[1] * 100, 2))
            screen.crypto_values.append(assembled_tuple)
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def get_timestamp_values(self):
        timestamps = []
        values = []
        max_previous_time = self.get_max_date()
        screen = self.root.get_screen('ViewHistoryScreen')
        for value in screen.crypto_values:
            if value[0] >= max_previous_time:
                timestamps.append(value[0])  # separate tuples into timestamps
                values.append(value[1] * 0.01)
        return timestamps, values

    def display_ninety_day_graph(self):
        """
        Generate and display the chart for the past 90 days
        """

        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_range = '90_day'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_thirty_day_graph(self):
        """
        Generate and display the chart for the past 30 days
        """

        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_range = '30_day'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_seven_day_graph(self):
        """
        Generate and display the chart for the past 7 days
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_range = '7_day'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_one_day_graph(self):
        """
        Generate and display the chart for the day
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_range = '1_day'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_line_graph(self):
        """
        Generate and display a line graph
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_type = 'line'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_bar_graph(self):
        """
        Generate and display a line graph
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_type = 'bar'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_candlestick_graph(self):
        """
        Generate and display a line graph
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.graph_type = 'candlestick'
        timestamps, values = self.get_timestamp_values()
        self.display_historical_graph(self.root.get_screen('ViewHistoryScreen').ids.chart_box, timestamps, values,  screen.crypto_name)

    def display_historical_graph(self, box, timestamps, values, title):
        """
        Create and display the chart for the history screen with given max_date
        """
        plt.clf()  # clear the current plot
        graph = self.generate_historical_chart(timestamps, values, title)  # generate the chart
        box.clear_widgets()  # remove olds charts
        box.add_widget(FigureCanvasKivyAgg(graph))  # add new graph
        plt.close(graph)

    def get_max_date(self):
        screen = self.root.get_screen('ViewHistoryScreen')

        match screen.graph_range:
            case '90_day':
                max_previous_time = datetime.now() - timedelta(days=90)
            case '30_day':
                max_previous_time = datetime.now() - timedelta(days=30)
            case '7_day':
                max_previous_time = datetime.now() - timedelta(days=7)
            case '1_day':
                max_previous_time = datetime.now() - timedelta(days=1)
            case _:
                'Error: invalid graph range. Exiting program.'
                sys.exit(1)
        return max_previous_time

    def generate_historical_chart(self, timestamps, values, title):
        """
        Take the timestamps and values and generate a chart for the screen
        """
        max_value = max(values)
        mean_value = sum(values) / (len(values))
        minimum_value = min(values)
        current_value = values[-1]
        screen = self.root.get_screen('ViewHistoryScreen')
        match screen.graph_type:
            case 'line':
                plt.style.use('default')
                plt.plot(timestamps, values)  # plot the data
                plt.xlabel('Timestamp')  # label the x-axis
                plt.xticks(rotation=30)  # rotate the labels 30 degrees
                plt.gca().xaxis.set_major_locator(AutoDateLocator())  # finds the optimal tick locations
                plt.gca().xaxis.set_major_formatter(
                    ConciseDateFormatter(AutoDateLocator()))  # finds the optimal way to label the dates
                plt.ylabel('Price')  # label the y-axis
                plt.grid()
                plt.axhline(y=max_value, color='#158a41', linestyle='--', linewidth=1)  # add line for max value
                plt.text(timestamps[0], max_value, f'Max: {round(max_value, 2)}',
                         fontsize=10)  # add label max value line
                plt.axhline(y=mean_value, color='cornflowerblue', linestyle='--',
                            linewidth=1)  # add line for mean value
                plt.text(timestamps[0], mean_value, f'Mean: {round(mean_value, 2)}',
                         fontsize=10)  # add label mean value line
                plt.axhline(y=minimum_value, color='#b81121', linestyle='--', linewidth=1)  # add line for minimum value
                plt.text(timestamps[0], minimum_value, f'Min: {round(minimum_value, 2)}',
                         fontsize=10)  # add label minimum value line
                plt.axhline(y=current_value, color='#b81121', linestyle='--', linewidth=1)  # add line for minimum value
                plt.text(timestamps[-1], current_value, f'Current: {round(current_value, 2)}',
                         fontsize=10, horizontalalignment='right')  # add label minimum value line
                if values[0] > values[-1]:  # determine if price went down over course of the chart
                    plt.gca().get_lines()[0].set_color("#b81121")  # set color red
                elif values[0] < values[-1]:  # determine if price went up over course of the chart
                    plt.gca().get_lines()[0].set_color("#158a41")  # set color green
                else:  # price stayed the same over course of the chart
                    plt.gca().get_lines()[0].set_color("cornflowerblue")  # set color blue
                plt.title(title)  # title the graph
                return plt.gcf()
            case 'bar':
                categories = ['Max', 'Mean', 'Min']
                colors = ['#158a41', 'cornflowerblue', '#b81121']
                plt.style.use('default')
                plt.bar(categories, [max_value, mean_value, minimum_value], color=colors)
                plt.ylabel('Price')
                plt.title(title)  # title the graph
                plt.axhline(y=max_value, color='#158a41', linestyle='--', linewidth=1)  # add line for max value
                plt.text(-0.3, max_value, f'Max: {round(max_value, 2)}',
                         fontsize=12)  # add label max value line
                plt.axhline(y=mean_value, color='cornflowerblue', linestyle='--',
                            linewidth=1)  # add line for mean value
                plt.text(.7, mean_value, f'Mean: {round(mean_value, 2)}', fontsize=12)  # add label mean value line
                plt.axhline(y=minimum_value, color='#b81121', linestyle='--', linewidth=1)  # add line for minimum value
                plt.text(1.7, minimum_value, f'Min: {round(minimum_value, 2)}',
                         fontsize=12)  # add label minimum value line
                return plt.gcf()
            case 'candlestick':
                timestamps_dict = {}  # Arrange timestamps and values into a dictionary to be used in candlestick graph
                for i in range(len(timestamps)):
                    timestamps_dict[timestamps[i]] = values[i]
                days_list = []
                for key in timestamps_dict:
                    day = datetime(year=key.year, month=key.month, day=key.day)
                    if day not in days_list:
                        days_list.append(day)
                opening_prices = []
                closing_prices = []
                average_prices = []
                highest_prices = []
                lowest_prices = []
                for day in days_list:  # for each day in our list
                    day_timestamps = []  # holds all the timestamps that occur on that day
                    for key in timestamps_dict:
                        if (datetime(year=key.year, month=key.month, day=key.day) ==
                                datetime(year=day.year, month=day.month,
                                         day=day.day)):  # check if timestamp occurs on that day
                            day_timestamps.append(key)  # if it does, append it to our list.
                    day_timestamps.sort()  # ensure the timestamps are sorted chronologically
                    day_sum = 0
                    highest_price = timestamps_dict[day_timestamps[0]]  # set the default highest price
                    lowest_price = timestamps_dict[day_timestamps[0]]  # set the default lowest price
                    for timestamp in day_timestamps:  # for each timestamp in my day's timestamp
                        if timestamps_dict[timestamp] > highest_price:  # if we have a new highest price
                            highest_price = timestamps_dict[timestamp]  # update highest price
                        if timestamps_dict[timestamp] < lowest_price:  # if we have a new lowest price
                            lowest_price = timestamps_dict[timestamp]  # update lowest price
                        day_sum += timestamps_dict[timestamp]  # increase the day's sum price
                    average_prices.append(day_sum / len(day_timestamps))  # get average price
                    highest_prices.append(highest_price)
                    lowest_prices.append(lowest_price)
                    opening_prices.append(timestamps_dict[day_timestamps[0]])
                    closing_prices.append(timestamps_dict[day_timestamps[-1]])
                data = {
                    'Open': opening_prices,
                    'High': highest_prices,
                    'Low': lowest_prices,
                    'Close': closing_prices
                }
                dataframe = pd.DataFrame(data, index=pd.DatetimeIndex(days_list))
                fig, ax = mpf.plot(dataframe, type='candle', style='charles', title=title, ylabel='Price',
                                   returnfig=True)
                ax[0].yaxis.set_label_position("left")
                ax[0].yaxis.tick_left()
                return fig

    def export_to_csv(self):
        screen = self.root.get_screen('ViewHistoryScreen')
        file_name = (
            f'{screen.crypto_id.replace(" ", "_")}_{screen.graph_range}_report_{str(datetime.now().date()).replace("-", "_")}_{str(datetime.now().hour)}_'
            f'{str(datetime.now().minute)}_{str(datetime.now().second)}.csv')
        max_date = self.get_max_date()
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Price'])
            for value in screen.crypto_values:
                if value[0] >= max_date:
                    writer.writerow(value)

    def display_home_screen_graph(self):
        screen = self.root.get_screen('MainDashboardScreen')
        crypto_quantities = self.get_quantities_and_investments()
        if crypto_quantities:
            most_invested_coin = max(crypto_quantities, key=lambda k: crypto_quantities[k][2])
            print(most_invested_coin)
            api_values = coin_gecko_api.get_coin_market_chart_by_id(most_invested_coin, 'usd', 7)
            timestamps = []
            values = []
            for value in api_values['prices']:
                timestamps.append(datetime.fromtimestamp(value[0] / 1000))
                values.append(round(value[1] * 100, 2))
            self.display_historical_graph(screen.ids.dashboard_chart_box, timestamps, values, most_invested_coin)
        else:
            screen.ids.dashboard_chart_box.clear_widgets()


class CustomButton(Button):
    """
    Button subclass to make all buttons in the .kv follow similar style
    """
    default_background_color = [1, 1, 1, 0]
    down_background_color = [0.7, 0.9, 0.7, 0]

    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)

    def on_state(self, instance, value):
        """
        Overriding of Button.on_state to change its color when pressed down. Signature inherited from parent.
        :param instance: Widget calling this function.
        :param value: New state, "normal" or "down"
        :return: None
        """
        if value == 'down':
            self.background_color = self.down_background_color
        else:
            self.background_color = self.default_background_color


if __name__ == '__main__':
    Window.size = (400, 400 * (16 / 9))
    app = CrypTrackerApp()
    app.run()
