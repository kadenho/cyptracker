from kivy.modules import inspector
from kivy.core.window import Window
import sys
from datetime import datetime, date, time, timedelta
import sqlalchemy
from kivy.app import App
import matplotlib.pyplot as plt
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from Tokenstaller.cryptos import CryptoDatabase, Crypto, CryptoPrice, PortfolioEntry, ValueCheck
from pycoingecko import CoinGeckoAPI
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.spinner import SpinnerOption
from sqlalchemy.exc import SQLAlchemyError

coin_gecko_api = CoinGeckoAPI()

class UserLoginScreen(Screen):
    pass
class CreateProfileScreen(Screen):
    pass
class MainDashboardScreen(Screen):
    pass
class AboutHelpScreen(Screen):
    pass
class HistoryHomeScreen(Screen):
    pass
class PortfolioTrackerScreen(Screen):
    pass
class TopGainersAndLosersScreen(Screen):
    pass
class SelectCryptoScreen(Screen):
    pass
class ViewHistoryScreen(Screen):
    crypto_id = StringProperty()
    crypto_name = StringProperty()
    crypto_values = ListProperty()
    crypto_percent_change = StringProperty()
class CryptoWatchlistScreen(Screen):
    pass
class PortfolioMenuScreen(Screen):
    pass
class NewCryptocurrencyScreen(Screen):
    pass
class PortfolioEntriesScreen(Screen):
    pass
class AddPortfolioEntryScreen(Screen):
    pass
class UpdatePortfolioEntryScreen(Screen):
    pass
class DeletePortfolioEntryScreen(Screen):
    pass
class CheckPortfolioScreen(Screen):
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
def text_color_from_value(label, lower, upper):
    """
    Yields an RGBA list for color based on the value of a string (red for negative, green for positive, black for 0)
    :param label: Label whose text and color will be changed
    :param lower: The highest value to return pure red [1, 0, 0, 1]
    :param upper: The lowest value to return pure green [0, 1, 0, 1]
    :return: RGBA list of colors between 0 and 1
    >>> import sys
    >>> from io import StringIO
    >>> sys.stdin = StringIO('weak')
    >>> colored_text = Label(text='100',color=[0, 0, 0, 1])
    >>> test_app = PortfolioTrackerApp()
    What is the password to your MySQL server?
    >>> text_color_from_value(colored_text, -100, 100)
    [0.0, 1.0, 0.0, 1.0]
    >>> import sys
    >>> from io import StringIO
    >>> sys.stdin = StringIO('weak')
    >>> color = [0.5, 0.0, 0.5, 1]
    >>> colored_text = Label(text='50',color=color)
    >>> test_app = PortfolioTrackerApp()
    What is the password to your MySQL server?
    >>> text_color_from_value(colored_text, -100, 100)
    [0.25, 0.5, 0.25, 1.0]
    >>> import sys
    >>> from io import StringIO
    >>> sys.stdin = StringIO('weak')
    >>> color = [1.0, 1.0, 0.0, 1]
    >>> colored_text = Label(text='-25',color=color)
    >>> test_app = PortfolioTrackerApp()
    What is the password to your MySQL server?
    >>> text_color_from_value(colored_text, -100, 100)
    [1.0, 0.75, 0.0, 1.0]
    """
    # Have to copy text_color so that it is not carried over through the default parameter
    text_color = list(label.color)
    green = [0, 1, 0, 1]
    red = [1, 0, 0, 1]
    green_differentials = [green[i] - text_color[i] for i in range(4)]
    # 0, 1, 0
    red_differentials = [red[i] - text_color[i] for i in range(4)]
    # Remove commas, spaces, periods, percentages, and dollar signs
    value = int(label.text.translate({ord(c): None for c in ', %$.'}))
    if value > 0:
        value = min(value, upper)
        for i in range(4):
            text_color[i] += (value / upper) * green_differentials[i]
    if value < 0:
        value = max(value, lower)
        for i in range(4):
            text_color[i] += (value / lower) * red_differentials[i]
    return text_color
def popup_update_text_size(instance):
    instance.children[0].children[0].children[0].text_size = instance.children[0].children[0].children[0].size
    return
def find_most_recent_timestamp(values_list):
    """
    Take a list of values and return the most recent value
    """
    most_recent_value = values_list[0]  # set the first value as the most recent value
    for value in values_list:  # iterate through the values
        if value.timestamp > most_recent_value.timestamp:  # if the value is more recent
            most_recent_value = value  # set it as the most recent value
    return most_recent_value  # return most recent value
def popup_update_text_size(instance):
    instance.children[0].children[0].children[0].text_size = instance.children[0].children[0].children[0].size
    return
class CrypTrackerApp(App):
    title_text = StringProperty('Portfolio App')

    background_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    text_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    outline_color = ColorProperty([1.0, 1.0, 1.0, 1.0])
    # Button color has to be transparent so its canvas color isn't obscured by it
    button_color = ColorProperty([1.0, 1.0, 1.0, 0.0])

    portfolio_report_date = StringProperty('')
    portfolio_report_previous_date = StringProperty('')
    portfolio_report_total = NumericProperty(0)
    portfolio_report_percent_change = NumericProperty(0)
    def __init__(self, **kwargs):
        super(CrypTrackerApp, self).__init__(**kwargs)
        password = input('What is the password to your MySQL server? ')
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
        self.crypto_database = CryptoDatabase(url)
        self.session = self.crypto_database.create_session()
    Window.size = (540, 960)
    def build(self):
        inspector.create_inspector(Window, self)
        self.sm = ScreenManager()
        self.sm.add_widget(UserLoginScreen(name='UserLoginScreen'))
        self.sm.add_widget(CreateProfileScreen(name='CreateProfileScreen'))
        self.sm.add_widget(MainDashboardScreen(name='MainDashboardScreen'))
        self.sm.add_widget(AboutHelpScreen(name='AboutHelpScreen'))
        self.sm.add_widget(SelectCryptoScreen(name='SelectCryptoScreen'))
        self.sm.add_widget(ViewHistoryScreen(name='ViewHistoryScreen'))
        self.sm.add_widget(PortfolioMenuScreen(name='PortfolioMenuScreen'))
        self.sm.add_widget(NewCryptocurrencyScreen(name='NewCryptocurrencyScreen'))
        self.sm.add_widget(PortfolioEntriesScreen(name='PortfolioEntriesScreen'))
        self.sm.add_widget(AddPortfolioEntryScreen(name='AddPortfolioEntryScreen'))
        self.sm.add_widget(UpdatePortfolioEntryScreen(name='UpdatePortfolioEntryScreen'))
        self.sm.add_widget(DeletePortfolioEntryScreen(name='DeletePortfolioEntryScreen'))
        self.sm.add_widget(CheckPortfolioScreen(name='CheckPortfolioScreen'))
        return self.sm
    def on_login_button_press(self):
        self.sm.current = 'MainDashboardScreen'
    def on_create_username_page_button_press(self):
        self.sm.current = 'CreateProfileScreen'
    def on_create_username_button_press(self):
        self.sm.current = 'UserLoginScreen'
    def on_historical_price_button_press(self):
        self.sm.current = 'SelectCryptoScreen'
    def on_switch_user_button_press(self):
        self.sm.current = 'UserLoginScreen'
    def on_about_help_button_press(self):
        self.sm.current = 'AboutHelpScreen'
    def on_about_help_back_button_press(self):
        self.sm.current = 'MainDashboardScreen'
    def on_portfolio_button_press(self):
        self.sm.current = 'PortfolioMenuScreen'

    def populate_list(self):
        """
        Creates the initial list displayed on the screen
        """
        screen = self.root.get_screen('SelectCryptoScreen')  # gets the screen
        list_box = screen.ids.cryptos_list_boxlayout  # gets the box that holds the rows
        list_box.searched_cryptos_list = []
        try:
            for i in range(self.session.query(Crypto).count()):
                current_id = self.session.query(Crypto)[i].crypto_id
                crypto = self.session.query(Crypto).filter(
                    Crypto.crypto_id == current_id).one()  # get crypto with that matches the id
                list_box.searched_cryptos_list.append(
                    self.assemble_tuple(crypto, current_id))  # append values to a list with a tuple
        except sqlalchemy.exc.ProgrammingError:
            print("\nError: Database not found. Create database and run installer or update database on line 80. Exiting program.")
            sys.exit(1)
        except sqlalchemy.exc.DatabaseError:
            print("\nError: Database not found. Ensure authority is set to \'localhost\' on line 80. Exiting program.")
            sys.exit(1)
        screen = self.root.get_screen('SelectCryptoScreen')
        screen.ids.cryptos_list_boxlayout.clear_widgets()  # clear the old list
        screen.ids.select_crypto_text_input.text = ''
        self.display_cryptos(list_box, screen)
    def change_screen(self, screen):
        self.root.current = screen
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

        '''Filters the full list of coins using the lambda function, then gets converted
        to a list so it can access each dictionary fitting the criteria.
        Result is a list of dictionaries with keys {'id':, 'name':, 'symbol':}
        that have the same name and symbol as the arguments to this method,
        then you take the value of the dictionary's id.
        Error handled for case of there being no crypto that fits.'''

        try:
            added_crypto_id = list(filter(lambda dictionary: dictionary["symbol"] == symbol \
                                                             and dictionary["name"] == name,
                                          coin_gecko_api.get_coins_list()))[0]['id']
        except IndexError:
            popup_title = 'Crypto not found'
            popup_message = f'Crypto with name {name} and symbol {symbol} not found.'
            self.display_popup(popup_title, popup_message, 'New Portfolio Entry')
            return
        crypto = Crypto(name=name, symbol=symbol, crypto_id=added_crypto_id)
        if not (len(name) > 0 and len(symbol) > 0):
            self.display_popup('Empty Data', 'Please enter data for all fields.', 'New Cryptocurrency')
            return
        if len(name) > 64 or len(symbol) > 64:
            self.display_popup('Data Too Long', 'At least one your entries exceeded 64 characters.',
                               'New Cryptocurrency')
            return
        count = self.session.query(Crypto).filter(Crypto.crypto_id == crypto.crypto_id).count()
        if count != 0:
            self.display_popup('Duplicate Entry',
                               f'Crypto with id \'{crypto.crypto_id}\' is already in the database {count} time(s).',
                               'New Cryptocurrency')
            return
        self.session.add(crypto)
        self.session.commit()
        self.display_popup('Entry Added', 'Crypto entry added.', 'Menu')
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
        return

    def display_cryptos(self, list_box, screen):
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
                Text(text='No results found', font_size=50))
    def add_crypto_price(self, crypto_id, timestamp, price):
        crypto_price = CryptoPrice(crypto_id=crypto_id, timestamp=timestamp, price=price)
        self.session.add(crypto_price)
        self.session.commit()

    @property
    def portfolio_info(self):
        """
        Returns a list of entry_ids from the portfolio_entries table
        """
        entry_info = []
        try:
            entries = self.session.query(PortfolioEntry)
            entry_count = entries.count()
            for i in range(entry_count):
                entry_info.append(str(entries[i].entry_id))
        except SQLAlchemyError:
            self.session.rollback()
            self.title_text = 'Database Error, make sure your port, username, and password are correct'

        return entry_info
    def modify_portfolio_entry(self, crypto_id=None, entry_date=None, quantity=None, operation=None, entry_id=None):
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
                                   f'There is no portfolio entry with id {entry_id}',
                                   'Portfolio Entries')
                return
            self.session.delete(entry)
            self.delete_portfolio_page(-1)
            # Decrements proceeding ids so there are no gaps
            for i in range(int(entry_id) + 1, len(self.portfolio_info)):
                self.session.query(PortfolioEntry)[i].entry_id -= 1

            self.display_popup('Entry Deleted',
                               'Portfolio entry successfully deleted.',
                               'Portfolio Entries')
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
            if self.session.query(CryptoPrice).filter(
                    CryptoPrice.timestamp == entry_date and CryptoPrice.crypto_id == crypto_id).count() == 0:
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
                investment = self.session.query(CryptoPrice).filter(
                    CryptoPrice.crypto_id == crypto_id and CryptoPrice.timestamp == entry_date).first().price * int(
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
                                                 investment=investment)
                try:
                    self.session.add(portfolio_entry)
                    self.session.commit()
                except SQLAlchemyError as error:
                    print(str(error), self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id \
                                                                             and CryptoPrice.timestamp == entry_date).first().price)
                    self.session.rollback()
                    self.display_popup('Database Error', str(error), 'New Portfolio Entry')
                self.display_popup('Entry Added', 'Portfolio Entry successfully added', 'Portfolio Entries')
                return
            # Logic for updating a portfolio entry
            entry = self.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == entry_id).one()
            entry.crypto_id = crypto_id
            entry.timestamp = entry_date
            entry.quantity = quantity
            entry.investment = investment
            self.session.commit()
            self.display_popup(title='Entry Updated',
                               text='Portfolio entry successfully updated.',
                               next_screen='Portfolio Entries')

    def add_value_check(self, timestamp=datetime.now()):
        """
        Adds a value check to the database containing a date, total value, and percentage change.
        :param self: Object on which the call is being made
        :param timestamp: Date of the value check, defaults to the current date.
        :return: None
        """
        count = self.session.query(ValueCheck).count()
        # Boolean decides if percent_change compares against the previous value check or each initial investment
        is_first_value_check = count == 0
        previous_value_check = self.session.query(ValueCheck)[count - 1] if not is_first_value_check else None
        total_value = 0
        total_initial_investment = 0
        entries = self.session.query(PortfolioEntry)
        # Dict of entry.crypto_id: entry.quantity
        crypto_quantities = dict()

        for entry in entries:
            total_initial_investment += entry.investment
            crypto_quantities.setdefault(entry.crypto_id, 0)
            crypto_quantities[entry.crypto_id] += entry.quantity
        for crypto_id in crypto_quantities:
            crypto_price = self.session.query(CryptoPrice).filter(
                CryptoPrice.crypto_id == crypto_id and timestamp == timestamp)
            if crypto_price.count() == 0:
                price = coin_gecko_api.get_price(crypto_id, 'usd')
                current_price = CryptoPrice(crypto_id=crypto_id, timestamp=timestamp, price=price)
                self.session.add(current_price)
                self.session.commit()
                total_value += current_price.price * crypto_quantities[crypto_id] / 100
            else:
                total_value += crypto_price.first().price * crypto_quantities[crypto_id] / 100

        previous_value = total_initial_investment if is_first_value_check else previous_value_check.total_value
        percentage_change = 100 * (total_value - previous_value) / abs(previous_value) if previous_value != 0 else 0
        value_check = ValueCheck(timestamp=timestamp, total_value=total_value, percentage_change=percentage_change)
        self.session.add(value_check)
        self.session.commit()
        self.portfolio_report_date = str(timestamp.date())
        self.portfolio_report_total = total_value
        self.portfolio_report_previous_date = str(
            previous_value_check.timestamp.date()) if previous_value_check is not None else 'N/A'
        self.portfolio_report_percent_change = round(percentage_change)
    def delete_portfolio_page(self, entry_id=1):
        """
        Edits the text in the Delete Portfolio Entry screen in the .kv
        :param entry_id: ID of the portfolio entry whose data is to be displayed. -1 for placeholders.
        :return: None
        """
        # Populate with default data if -1 is given
        if entry_id == -1:
            self.root.ids.delete_crypto_id.text = 'Crypto ID'
            self.root.ids.delete_date_text.text = 'YYYY-MM-DD'
            self.root.ids.delete_quantity_text.text = '0'
            return
        selected_entry = self.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == entry_id).first()

        try:
            self.root.ids.delete_crypto_id.text = str(selected_entry.crypto_id)

        except AttributeError as ae:
            print(ae)
            self.display_popup('No Entry Found',
                               f'There is no Portfolio Entry with id {entry_id}.',
                               'Delete Portfolio Entry')
            return

        self.root.ids.delete_crypto_id.text = str(selected_entry.crypto_id)
        self.root.ids.delete_date_text.text = str(selected_entry.timestamp.date())
        self.root.ids.delete_quantity_text.text = str(selected_entry.quantity)
        return

    def update_portfolio_page(self, entry_id=1):
        selected_entry = self.session.query(PortfolioEntry).filter(PortfolioEntry.entry_id == entry_id).first()
        self.root.ids.update_spinner_crypto_id.text = str(selected_entry.crypto_id)
        self.root.ids.update_date_text.hint_text = str(selected_entry.timestamp.date())
        self.root.ids.update_quantity_text.text = str(selected_entry.quantity)
        return
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
            self.title_text = 'Database Error, make sure your port, username, and password are correct'

        return ids
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
            for i in range(self.session.query(Crypto).count()):
                current_id = self.session.query(Crypto)[i].crypto_id
                crypto = self.session.query(Crypto).filter(Crypto.crypto_id == current_id).one()  # retrieve crypto

                if search_query in crypto.symbol.lower().strip() or search_query in crypto.name.lower().strip():  # check if crypto matches the search query
                    list_box.searched_cryptos_list.append(
                        self.assemble_tuple(crypto, current_id))  # add crypto to list if it does
            screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove old rows
            self.display_cryptos(list_box, screen)

    def assemble_tuple(self, crypto, current_id):
        """
        retrieve data and package into a tuple to be added to the list
        """
        crypto_symbol = crypto.symbol  # retrieve crypto's symbol
        crypto_name = crypto.name  # retrieve crypto's name
        today_values = self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == current_id,
                                                            # retrieve all of today's timestamps
                                                            CryptoPrice.timestamp >= datetime(2025, 1,
                                                                                            30)).all()  # timestamp is hard coded for dummy data, once we use the api it will be changed
        if not today_values:  # ensure there is a price for today
            today_price = percent_change = None
        else:
            most_recent_value = find_most_recent_timestamp(today_values)  # get most recent value from today

            today_price = str(round(most_recent_value.price * 0.01, 2))

            yesterday_values = self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == current_id,
                                                                    # retrieve all of today's timestamps
                                                                    CryptoPrice.timestamp >= datetime(2025, 1, 29),
                                                                    CryptoPrice.timestamp < datetime(2025, 1,
                                                                                                   30)).all()  # timestamp is hard coded for dummy data, once we use the api it will be changed
            if not yesterday_values:  # ensure there is a price for yesterday
                percent_change = None
            else:
                most_recent_value = find_most_recent_timestamp(yesterday_values)  # get most recent value from yesterday

                yesterday_price = str(round(most_recent_value.price * 0.01, 2))  # calculate the percent change

                if yesterday_price == '0.0':  # prevent divide by 0 error
                    percent_change = '-100.00'
                else:
                    percent_change = str(
                        round((float(today_price) - float(yesterday_price)) / float(yesterday_price) * 100,
                              2))  # calculate percent change
        assembled_tuple = (crypto_symbol, crypto_name, today_price, percent_change, current_id)  # package data into a tuple
        return assembled_tuple  # return the assembled tuple

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
        try:
            selected_crypto = self.session.query(Crypto).filter(Crypto.crypto_id == crypto_id).one()  # get the crypto selected
        except sqlalchemy.exc.MultipleResultsFound:
            print("\nError: Multiple results found. Ensure the installer was only ran once.")
            sys.exit(1)
        except sqlalchemy.exc.NoResultFound:
            print("\nError: No results found. Ensure the symbol is correct.")
            sys.exit(1)
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.crypto_id = crypto_id
        screen.crypto_name = selected_crypto.name

        selected_values = self.session.query(CryptoPrice).filter(
            CryptoPrice.crypto_id == selected_crypto.crypto_id).all()  # find all values for that crypto
        screen.crypto_values = []
        for crypto_value in selected_values:  # reassemble the values as a tuple
            assembled_tuple = (crypto_value.timestamp, crypto_value.price)
            screen.crypto_values.append(assembled_tuple)
        self.display_month_chart()

    def display_chart(self, max_previous_time):
        """
        Create and display the chart for the history screen with given max_date
        """
        plt.clf()  # clear the current plot
        timestamps = []
        values = []
        screen = self.root.get_screen('ViewHistoryScreen')
        for value in screen.crypto_values:
            if value[0] >= max_previous_time:
                timestamps.append(value[0])  # separate tuples into timestamps
                values.append(value[1] * 0.01)
        self.generate_chart(timestamps, values)  # generate the chart

    def display_month_chart(self):
        """
        Generate and display the chart for the month
        """
        self.display_chart(datetime(2025, 1, 1, 23, 59, 59))  # timestamp hard coded until api implementation

    def display_week_chart(self):
        """
        Generate and display the chart for the week
        """
        self.display_chart(datetime(2025, 1, 22, 23, 59, 59))  # timestamp hard coded until api implementation

    def display_day_chart(self):
        """
        Generate and display the chart for the day
        """
        self.display_chart(datetime(2025, 1, 29, 23, 59, 59))  # timestamp hard coded until api implementation

    def generate_chart(self, timestamps, values):
        """
        Take the timestamps and values and generate a chart for the screen
        """
        screen = self.root.get_screen('ViewHistoryScreen')
        x = timestamps  # set the x-axis to the timestamps
        y = values  # set the y-axis to the values
        plt.plot(x, y)  # plot the data
        plt.xlabel('Timestamp')  # label the x-axis
        plt.xticks(rotation=30)  # rotate the labels 30 degrees
        plt.gca().xaxis.set_major_locator(AutoDateLocator())  # finds the optimal tick locations
        plt.gca().xaxis.set_major_formatter(
            ConciseDateFormatter(AutoDateLocator()))  # finds the optimal way to label the dates
        plt.ylabel('Price')  # label the y-axis
        plt.grid()
        if values[0] > values[-1]:  # determine if price went down over course of the chart
            plt.gca().get_lines()[0].set_color("#b81121") # set color red
        elif values[0] < values[-1]:  # determine if price went up over course of the chart
            plt.gca().get_lines()[0].set_color("#158a41")  # set color green
        else:  # price stayed the same over course of the chart
            plt.gca().get_lines()[0].set_color("cornflowerblue")  # set color blue
        plt.title(screen.crypto_name)  # title the graph
        screen.ids.chart_box.clear_widgets()  # remove the old chart
        screen.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # add the new chart

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

class PortfolioUpdateSpinner(SpinnerOption):
    def __init__(self, **kwargs):
        super(PortfolioUpdateSpinner, self).__init__(**kwargs)

    def on_press(self):
        app.update_portfolio_page(self.text)


class PortfolioDeleteSpinner(SpinnerOption):
    def __init__(self, **kwargs):
        super(PortfolioDeleteSpinner, self).__init__(**kwargs)

    def on_press(self):
        app.delete_portfolio_page(self.text)


if __name__ == '__main__':
    app = CrypTrackerApp()
    app.run()