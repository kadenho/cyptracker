import re
from datetime import datetime, date, timedelta, time

import sqlalchemy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.modules import inspector
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.spinner import SpinnerOption
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from matplotlib import pyplot as plt
from sqlalchemy import and_, desc
from sqlalchemy.exc import SQLAlchemyError

from HistoricalPriceViewer.main import coin_gecko_api
from Tokenstaller.cryptos import CryptoDatabase, Crypto, PortfolioEntry, CryptoPrice
from Tokenstaller.cryptos import ValueCheck
from pycoingecko import CoinGeckoAPI


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
    # Remove non-integers and store as an int
    value = int(re.sub('[^0-9-]', '', label.text))
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


class PortfolioMenuScreen(Screen):
    pass

class ManageCryptocurrenciesScreen(Screen):
    pass

class AddCryptocurrencyScreen(Screen):
    pass


class DeleteCryptocurrencyScreen(Screen):
    pass


class ManagePortfolioEntriesScreen(Screen):
    pass


class AddPortfolioEntryScreen(Screen):
    pass


class UpdatePortfolioEntryScreen(Screen):
    pass


class DeletePortfolioEntryScreen(Screen):
    pass


class CheckPortfolioScreen(Screen):
    def on_enter(self):
        app.add_value_check()


class PieChartScreen(Screen):
    pass


class PortfolioTrackerApp(App):
    kv_file = 'portfolio_tracker.kv'
    title_text = StringProperty('Portfolio App')
    user_id = NumericProperty(1)

    background_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    text_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    outline_color = ColorProperty([1.0, 1.0, 1.0, 1.0])
    # Button color has to be transparent so its canvas color isn't obscured by it
    button_color = ColorProperty([1.0, 1.0, 1.0, 0.0])

    portfolio_report_date = StringProperty('')
    portfolio_report_previous_date = StringProperty('')
    portfolio_report_total = NumericProperty(0)
    portfolio_report_change_from_previous = NumericProperty(0)
    portfolio_report_change_from_investment = NumericProperty(0)

    coingecko_api = CoinGeckoAPI(demo_api_key='CG-1h5S2Brt9U9LxgUxyjtU4RBj')

    def __init__(self, **kwargs):
        super(PortfolioTrackerApp, self).__init__(**kwargs)
        password = input('What is your MySQL server password?')
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
        self.crypto_database = CryptoDatabase(url)
        self.session = self.crypto_database.create_session()
        self.session.close()
        self.session = self.crypto_database.create_session()
        self.session.rollback()

    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).
        screen_manager = ScreenManager()
        screen_manager.add_widget(PortfolioMenuScreen(name='Portfolio Menu'))
        screen_manager.add_widget(ManageCryptocurrenciesScreen(name='Manage Cryptocurrencies'))
        screen_manager.add_widget(AddCryptocurrencyScreen(name='Add Cryptocurrency'))
        screen_manager.add_widget(DeleteCryptocurrencyScreen(name='Delete Cryptocurrency'))
        screen_manager.add_widget(ManagePortfolioEntriesScreen(name='Manage Portfolio Entries'))
        screen_manager.add_widget(AddPortfolioEntryScreen(name='Add Portfolio Entry'))
        screen_manager.add_widget(UpdatePortfolioEntryScreen(name='Update Portfolio Entry'))
        screen_manager.add_widget(DeletePortfolioEntryScreen(name='Delete Portfolio Entry'))
        screen_manager.add_widget(CheckPortfolioScreen(name='Check Portfolio'))
        screen_manager.add_widget(PieChartScreen(name='Pie Chart'))
        return screen_manager

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
        return

    def display_pie_chart(self, crypto_quantities):
        plt.clf()  # clear the current plot
        crypto_ids = [crypto_id for crypto_id in crypto_quantities]
        current_holdings = [crypto_quantities[crypto_id][2] for crypto_id in crypto_quantities]
        try:
            self.generate_chart(crypto_ids, current_holdings)  # generate the chart
        except ValueError:
            self.display_popup('Value Error',
                               'You currently have $0.00 in holdings, '
                               'so a pie chart cannot be generated.',
                               'Portfolio Menu')

    def generate_chart(self, crypto_ids, holdings):
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

    def add_crypto_price(self, crypto_id, timestamp, price):
        """

        :param crypto_id:
        :param timestamp:
        :param price: Price in dollars
        :return:
        """
        crypto_price = CryptoPrice(crypto_id=crypto_id, timestamp=timestamp, price=price * 100)
        # If an entry in crypto_prices with that timestamp and crypto already exists, exit
        if self.session.query(CryptoPrice).filter(
                and_(CryptoPrice.crypto_id == crypto_id, CryptoPrice.timestamp == timestamp)).count() == 0:
            return
        self.session.add(crypto_price)
        self.session.commit()
        print(f'crypto price committed {crypto_price.crypto_id, crypto_price.timestamp, crypto_price.price}')

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
                                   f'There is no portfolio entry with id {entry_id}',
                                   'Manage Portfolio Entries')
                return
            self.session.delete(entry)
            self.delete_portfolio_page(-1)
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
            if self.session.query(CryptoPrice).filter(
                    and_(CryptoPrice.timestamp == entry_date, CryptoPrice.crypto_id == crypto_id)).count() == 0:
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
                    CryptoPrice.crypto_id == crypto_id, CryptoPrice.timestamp == entry_date).first().price * int(
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
                                   f'There is no portfolio entry with id {entry_id}',
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
        count = self.session.query(ValueCheck).count()
        # Boolean decides if percent_change should also compare against the previous value check or only initial investment
        is_first_value_check = count == 0
        previous_value_check = self.session.query(ValueCheck)[count - 1] if not is_first_value_check else None
        total_value = 0
        total_initial_investment = 0
        crypto_quantities = self.get_quantities_and_investments(timestamp)
        print(crypto_quantities, timestamp)
        for crypto_id in crypto_quantities:
            total_initial_investment += crypto_quantities[crypto_id][1]
            total_value += crypto_quantities[crypto_id][2]

        change_from_previous = None

        if not is_first_value_check:
            previous_value = previous_value_check.total_value
            change_from_previous = 100 * (total_value - previous_value) // abs(
                previous_value) if previous_value != 0 else 0

        change_from_investment = 100 * (total_value - total_initial_investment) // abs(
            total_initial_investment) if total_initial_investment != 0 else 0
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
        self.portfolio_report_previous_date = str(
            previous_value_check.timestamp.date()) if previous_value_check is not None else 'N/A'
        self.portfolio_report_change_from_previous = 0 if is_first_value_check else round(change_from_previous)
        self.portfolio_report_change_from_investment = change_from_investment
        self.display_pie_chart(crypto_quantities)

    def get_quantities_and_investments(self, timestamp):
        """
        Returns a dictionary of 'crypto_id' string keys and [quantity, total investment, total held] list values
        Note: both total investment and total held should be integers in cents
        :param timestamp: Timestamp to base the 'total held' element of the tuple off. Should be the current time.
        :return:
        """
        entries = self.session.query(PortfolioEntry).filter(PortfolioEntry.user_id == self.user_id)
        # Dict of entry.crypto_id: (total quantity, total investment, total held)
        crypto_quantities_prices = dict()
        # Populate dictionary with every crypto in the user's portfolio and set their quantity and initial investment
        for entry in entries:
            crypto_quantities_prices.setdefault(entry.crypto_id, [0, 0, 0])
            crypto_quantities_prices[entry.crypto_id][0] += entry.quantity
            crypto_quantities_prices[entry.crypto_id][1] += entry.investment
        # Set the price held at the timestamp for each crypto
        for crypto_id in crypto_quantities_prices:
            crypto_price = self.session.query(CryptoPrice).filter(
                and_(CryptoPrice.timestamp == timestamp, CryptoPrice.crypto_id == crypto_id))
            # Add new price to database if none are found at the current time
            if crypto_price.count() == 0:
                price = 100 * round(coin_gecko_api.get_price(crypto_id, 'usd')[crypto_id]['usd'], 2)
                self.add_crypto_price(crypto_id, timestamp, price)
                self.session.commit()
            current_price = self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id).order_by(
                desc(CryptoPrice.timestamp)).first()
            print(current_price.timestamp)
            crypto_quantities_prices[crypto_id][2] = crypto_quantities_prices[crypto_id][0] * current_price.price
        return crypto_quantities_prices


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
    Window.size = (400, (16 / 9) * 400)
    Window.top = 0
    try:
        app = PortfolioTrackerApp()
        app.run()
    except SQLAlchemyError as e:
        app.session.rollback()
        print(f'There was a database error: {e}')
