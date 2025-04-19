import re
from datetime import datetime, date, timedelta, time

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.modules import inspector
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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


class PortfolioTrackerApp(App):
    kv_file = 'portfolio_tracker.kv'
    title_text = StringProperty('PortfolioApp Portfolio App')

    background_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    text_color = ColorProperty([0.0, 0.0, 0.0, 1.0])
    outline_color = ColorProperty([1.0, 1.0, 1.0, 1.0])
    # Button color has to be transparent so its canvas color isn't obscured by it
    button_color = ColorProperty([1.0, 1.0, 1.0, 0.0])



    portfolio_report_date = StringProperty('')
    portfolio_report_previous_date = StringProperty('')
    portfolio_report_total = NumericProperty(0)
    portfolio_report_percent_change = NumericProperty(0)
    coingecko_api = CoinGeckoAPI(demo_api_key='CG-1h5S2Brt9U9LxgUxyjtU4RBj')

    def __init__(self, **kwargs):
        super(PortfolioTrackerApp, self).__init__(**kwargs)
        password = input('What is the password to your MySQL server?')
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
        self.crypto_database = CryptoDatabase(url)
        self.session = self.crypto_database.create_session()

    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).

    def change_screen(self, screen):
        self.root.current = screen

    def change_color(self, variable, color):
        if '.' not in color:
            color = re.findall('d+', color)
        else:
            color = re.findall('d*.d+', color)
        while len(color) < 4:
            color.append(1.0)
        color = [float(color[i]) for i in range(4)]
        match variable:
            case 'Background':
                self.background_color = color
            case 'Outline':
                self.outline_color = color
            case 'Text':
                self.text_color = color
            case 'Button':
                color = color[0:3]
                color.append(0)
                self.button_color = color



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
            added_crypto_id = list(filter(lambda dictionary: dictionary["symbol"] == symbol\
                        and dictionary["name"] == name, coin_gecko_api.get_coins_list()))[0]['id']
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

    def add_crypto_price(self, crypto_id, timestamp, price):
        crypto_price = CryptoPrice(crypto_id=crypto_id, timestamp=timestamp, price=price)
        self.session.add(crypto_price)
        self.session.commit()

    def add_portfolio_entry(self, crypto_id, entry_date, quantity):
        """
        Adds a portfolio entry to the database using its id, a date, and a quantity
        :param crypto_id: id of the crypto
        :param entry_date: Date of entry
        :param quantity: Quantity of the crypto bought at that date
        :return: None
        """
        does_crypto_date_match = CryptoPrice.crypto_id == crypto_id and CryptoPrice.timestamp == entry_date

        if crypto_id == 'Crypto ID':
            self.display_popup('No Crypto ID Selected', 'Please select a Crypto ID.', 'New Portfolio Entry')
            return

        if len(quantity) == 0:
            self.display_popup('Empty Data', 'Please enter in a quantity.', 'New Portfolio Entry')
            return

        try:
            entry_date = date.fromisoformat(entry_date)
            # Sets the time element of the entry_date to be midnight
            entry_date = datetime.combine(entry_date, time())
            # Date in format 'DD-MM-YYYY' as required by the CoinGecko API
            adjusted_date = f'{entry_date.day:02d}-{entry_date.month:02d}-{entry_date.year:04d}'
        except ValueError as error:
            self.display_popup('Date Error', str(error), 'New Portfolio Entry')
            return

        if entry_date < datetime.combine(date.today(), time()) - timedelta(days=364):
            self.display_popup('Date Out of Range',
                               'Please enter a date within the last 364 days.',
                               'New Portfolio Entry')
            return

        if int(quantity) > 10000:
            self.display_popup('Value Error', 'Quantity is too high, please enter a lower quantity',
                               'New Portfolio Entry')
            return

        if self.session.query(CryptoPrice).filter(does_crypto_date_match).count() == 0:
            historic_coin_data = coin_gecko_api.get_coin_history_by_id(crypto_id, adjusted_date)
            price = historic_coin_data['market_data']['current_price']['usd']
            self.add_crypto_price(crypto_id, entry_date, price)
            self.display_popup('Database Error',
                               'This crypto did not exist at your selected date. Please select a later date.',
                               'New Portfolio Entry')
        try:
            investment = self.session.query(CryptoPrice).filter(does_crypto_date_match).one().price * int(quantity)
            portfolio_entry = PortfolioEntry(crypto_id=crypto_id,
                                         timestamp=entry_date,
                                         quantity=quantity,
                                         investment=investment)
        except SQLAlchemyError:
            self.display_popup('Invalid Date',
                               'This crypto did not exist at this date, please choose a later date',
                               'New Portfolio Entry')
            return

        try:
            self.session.add(portfolio_entry)
            self.session.commit()
        except SQLAlchemyError as error:
            print(self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id\
                                                         and CryptoPrice.timestamp == entry_date).first().price)
            self.session.rollback()
            self.display_popup('Database Error', str(error), 'New Portfolio Entry')
            return
        self.display_popup('Entry Added', 'Portfolio Entry successfully added', 'Menu')

    def add_value_check(self, timestamp=datetime.now()):
        """
        Adds a value check to the database containing a date, total value, and percentage change.
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
            crypto_price = self.session.query(CryptoPrice).filter(CryptoPrice.crypto_id == crypto_id and timestamp == timestamp)
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
    Window.size = (400, (16 / 9) * 400)
    Window.top = 0
    try:
        app = PortfolioTrackerApp()
        app.run()
    except SQLAlchemyError as e:
        print(f'There was a database error: {e}')
    except KeyboardInterrupt:
        app.session.close()
