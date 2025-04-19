from kivy.modules import inspector
from kivy.core.window import Window
import sys
from datetime import datetime
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
from Tokenstaller.cryptos import CryptoDatabase, Crypto, CryptoPrice
from pycoingecko import CoinGeckoAPI

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

class CrypTrackerApp(App):
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
        self.sm.add_widget(HistoryHomeScreen(name='HistoryHomeScreen'))
        self.sm.add_widget(PortfolioTrackerScreen(name='PortfolioTrackerScreen'))
        self.sm.add_widget(TopGainersAndLosersScreen(name='TopGainersAndLosersScreen'))
        self.sm.add_widget(SelectCryptoScreen(name='SelectCryptoScreen'))
        self.sm.add_widget(ViewHistoryScreen(name='ViewHistoryScreen'))
        self.sm.add_widget(CryptoWatchlistScreen(name='CryptoWatchlistScreen'))
        return self.sm
    def on_login_button_press(self):
        self.sm.current = 'MainDashboardScreen'
    def on_create_username_page_button_press(self):
        self.sm.current = 'CreateProfileScreen'
    def on_create_username_button_press(self):
        self.sm.current = 'UserLoginScreen'
    def on_historical_price_button_press(self):
        self.sm.current = 'HistoryHomeScreen'
    def on_switch_user_button_press(self):
        self.sm.current = 'UserLoginScreen'
    def on_about_help_button_press(self):
        self.sm.current = 'AboutHelpScreen'
    def on_about_help_back_button_press(self):
        self.sm.current = 'MainDashboardScreen'

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

    def display_cryptos(self, list_box, screen):
        if len(list_box.searched_cryptos_list) >= 5:
            for i in range(5):
                (symbol, name, value, percent_change) = list_box.searched_cryptos_list[i]  # retrieve values
                screen.ids.cryptos_list_boxlayout.add_widget(
                    SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                  crypto_percent_change=percent_change))  # display values
        elif 0 < len(list_box.searched_cryptos_list) <= 4:
            for i in range(len(list_box.searched_cryptos_list)):
                (symbol, name, value, percent_change) = list_box.searched_cryptos_list[i]  # retrieve values
                screen.ids.cryptos_list_boxlayout.add_widget(
                    SelectCryptoBox(crypto_symbol=symbol, crypto_name=name, crypto_value=value,
                                  crypto_percent_change=percent_change))  # display values
        elif len(list_box.searched_cryptos_list) == 0:  # if no cryptos match the search query
            screen.ids.cryptos_list_boxlayout.add_widget(  # notify user no results were found
                Text(text='No results found', font_size=50))

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
                current_id = self.session.query(Crypto)[i]
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
        assembled_tuple = (crypto_symbol, crypto_name, today_price, percent_change)  # package data into a tuple
        return assembled_tuple  # return the assembled tuple

    def move_list_back(self):
        """
        Displays the previous 5 cryptos in the list if possible
        """
        screen = self.root.get_screen('SelectCryptoScreen')  # retrieve cryptos
        list_box = screen.ids.cryptos_list_boxlayout  # retrieve list
        if list_box.searched_cryptos_list:  # as long as the list exists
            first_box = screen.ids.cryptos_list_boxlayout.children[-1]  # retrieve the first item
            first_tuple = (first_box.crypto_id, first_box.crypto_name, first_box.crypto_value,
                           first_box.crypto_percent_change)  # repackage the data into a tuple
            index = list_box.searched_cryptos_list.index(
                first_tuple)  # search list for the matching tuple to find the current index
            if index > 4:  # if there are at least 5 widgets preceding to be displayed
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # clear the widgets
                for i in range(5):
                    (symbol, name, value, percent_change) = list_box.searched_cryptos_list[
                        index - 5 + i]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_code=symbol, crypto_name=name, crypto_value=value,
                                      crypto_percent_change=percent_change))  # display crypto

    def move_list_forward(self):
        """
        Displays the next cryptos in the list if possible
        """
        screen = self.root.get_screen('SelectCryptoScreen')
        list_box = screen.ids.cryptos_list_boxlayout
        if list_box.searched_cryptos_list:
            last_box = screen.ids.cryptos_list_boxlayout.children[0]  # select the last displayed crypto
            last_tuple = (last_box.crypto_id, last_box.crypto_name, last_box.crypto_value,
                          last_box.crypto_percent_change)  # repackage the values into a tuple
            index = list_box.searched_cryptos_list.index(last_tuple)  # find the index of that crypto

            if index < (len(list_box.searched_cryptos_list) - 5):  # if there are at least 5 cryptos left
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(5):  # for the next 5 cryptos
                    (symbol, name, value, percent_change) = list_box.searched_cryptos_list[
                        i + index + 1]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_code=symbol, crypto_name=name, crypto_value=value,
                                      crypto_percent_change=percent_change))  # display crypto
            elif index != len(list_box.searched_cryptos_list) - 1:  # if there is at least 1 crypto left
                screen.ids.cryptos_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(len(list_box.searched_cryptos_list) - index - 1):  # for the remaining cryptos
                    (symbol, name, value, percent_change) = list_box.searched_cryptos_list[
                        i + index + 1]  # retrieve values
                    screen.ids.cryptos_list_boxlayout.add_widget(
                        SelectCryptoBox(crypto_code=symbol, crypto_name=name, crypto_value=value,
                                      crypto_percent_change=percent_change))  # display crypto

    def select_crypto(self, symbol):
        """
        set the values for the show history screen
        """
        try:
            selected_crypto = self.session.query(Crypto).filter(Crypto.symbol == symbol).one()  # get the crypto selected
        except sqlalchemy.exc.MultipleResultsFound:
            print("\nError: Multiple results found. Ensure the installer was only ran once.")
            sys.exit(1)
        except sqlalchemy.exc.NoResultFound:
            print("\nError: No results found. Ensure the symbol is correct.")
            sys.exit(1)
        screen = self.root.get_screen('ViewHistoryScreen')
        screen.symbol = symbol
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

if __name__ == '__main__':
    app = CrypTrackerApp()
    app.run()