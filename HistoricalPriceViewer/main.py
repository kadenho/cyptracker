import sys
from datetime import datetime
import sqlalchemy
from kivy.app import App
import matplotlib.pyplot as plt
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from crypto import CryptoDatabase, Coin, CoinValue
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from pycoingecko import CoinGeckoAPI

coin_gecko_api = CoinGeckoAPI()

class Text(Label):
    pass


class FormattedButton(Button):
    pass


class BackButton(FormattedButton):
    pass


class HomeScreen(Screen):
    pass


class ScreenBoxLayout(BoxLayout):
    pass


class PortfolioTrackerScreen(Screen):
    pass


class TopGainersAndLosersScreen(Screen):
    pass


class SelectCoinScreen(Screen):
    pass


class ViewHistoryScreen(Screen):
    coin_code = StringProperty()
    coin_name = StringProperty()
    coin_values = ListProperty()
    coin_percent_change = StringProperty()


class CryptoWatchlistScreen(Screen):
    pass


class SelectCoinBox(BoxLayout):
    coin_code = StringProperty()
    coin_name = StringProperty()
    coin_value = StringProperty()
    coin_percent_change = StringProperty()
    searched_coins_list = ListProperty()


def find_most_recent_timestamp(values_list):
    """
    Take a list of values and return the most recent value
    """
    most_recent_value = values_list[0]  # set the first value as the most recent value
    for value in values_list:  # iterate through the values
        if value.timestamp > most_recent_value.timestamp:  # if the value is more recent
            most_recent_value = value  # set it as the most recent value
    return most_recent_value  # return most recent value


class CryptoApp(App):
    def __init__(self, **kwargs):
        super(CryptoApp, self).__init__(**kwargs)
        url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'crypto', 'root', 'sqlpassword')
        self.crypto_database = CryptoDatabase(url)
        self.session = self.crypto_database.create_session()

    def build(self):
        """
        Build the screens
        """
        screen_manager = ScreenManager(transition=NoTransition())  # create manager
        screen_manager.add_widget(HomeScreen(name='home_screen'))
        screen_manager.add_widget(PortfolioTrackerScreen(name='portfolio_tracker_screen'))
        screen_manager.add_widget(TopGainersAndLosersScreen(name='top_gainers_and_losers_screen'))
        screen_manager.add_widget(SelectCoinScreen(name='select_coin_screen'))
        screen_manager.add_widget(ViewHistoryScreen(name='view_history_screen'))
        screen_manager.add_widget(CryptoWatchlistScreen(name='crypto_watchlist_screen'))
        return screen_manager

    def populate_list(self):
        """
        Creates the initial list displayed on the screen
        """
        screen = self.root.get_screen('select_coin_screen')  # gets the screen
        list_box = screen.ids.coins_list_boxlayout  # gets the box that holds the rows
        list_box.searched_coins_list = []
        try:
            for i in range(self.session.query(Coin).count()):
                current_id = i + 1
                coin = self.session.query(Coin).filter(
                    Coin.coin_id == current_id).one()  # get coin with that matches the id
                list_box.searched_coins_list.append(
                    self.assemble_tuple(coin, current_id))  # append values to a list with a tuple
        except sqlalchemy.exc.ProgrammingError:
            print("\nError: Database not found. Create database and run installer or update database on line 80. Exiting program.")
            sys.exit(1)
        except sqlalchemy.exc.DatabaseError:
            print("\nError: Database not found. Ensure authority is set to \'localhost\' on line 80. Exiting program.")
            sys.exit(1)
        screen = self.root.get_screen('select_coin_screen')
        screen.ids.coins_list_boxlayout.clear_widgets()  # clear the old list
        screen.ids.select_coin_text_input.text = ''
        self.display_coins(list_box, screen)

    def display_coins(self, list_box, screen):
        if len(list_box.searched_coins_list) >= 5:
            for i in range(5):
                (symbol, name, value, percent_change) = list_box.searched_coins_list[i]  # retrieve values
                screen.ids.coins_list_boxlayout.add_widget(
                    SelectCoinBox(coin_code=symbol, coin_name=name, coin_value=value,
                                  coin_percent_change=percent_change))  # display values
        elif 0 < len(list_box.searched_coins_list) <= 4:
            for i in range(len(list_box.searched_coins_list)):
                (symbol, name, value, percent_change) = list_box.searched_coins_list[i]  # retrieve values
                screen.ids.coins_list_boxlayout.add_widget(
                    SelectCoinBox(coin_code=symbol, coin_name=name, coin_value=value,
                                  coin_percent_change=percent_change))  # display values
        elif len(list_box.searched_coins_list) == 0:  # if no coins match the search query
            screen.ids.coins_list_boxlayout.add_widget(  # notify user no results were found
                Text(text='No results found', font_size=50))

    def repopulate_list(self):
        """
        Repopulates the list of coins based on the search query
        """
        screen = self.root.get_screen('select_coin_screen')  # get screen
        search_query = screen.ids.select_coin_text_input.text.lower().strip()  # get the search query
        list_box = screen.ids.coins_list_boxlayout  # get box that holds the rows
        list_box.searched_coins_list = []

        if search_query == '':
            self.populate_list()  # populate the list with default values
        else:
            for i in range(self.session.query(Coin).count()):
                current_id = i + 1
                coin = self.session.query(Coin).filter(Coin.coin_id == current_id).one()  # retrieve coin

                if search_query in coin.symbol.lower().strip() or search_query in coin.name.lower().strip():  # check if coin matches the search query
                    list_box.searched_coins_list.append(
                        self.assemble_tuple(coin, current_id))  # add coin to list if it does
            screen.ids.coins_list_boxlayout.clear_widgets()  # remove old rows
            self.display_coins(list_box, screen)

    def assemble_tuple(self, coin, current_id):
        """
        retrieve data and package into a tuple to be added to the list
        """
        coin_symbol = coin.symbol  # retrieve coin's symbol
        coin_name = coin.name  # retrieve coin's name
        today_values = self.session.query(CoinValue).filter(CoinValue.coin_id == current_id,
                                                            # retrieve all of today's timestamps
                                                            CoinValue.timestamp >= datetime(2025, 1,
                                                                                            30)).all()  # timestamp is hard coded for dummy data, once we use the api it will be changed
        if not today_values:  # ensure there is a price for today
            today_price = percent_change = None
        else:
            most_recent_value = find_most_recent_timestamp(today_values)  # get most recent value from today

            today_price = str(round(most_recent_value.price * 0.01, 2))

            yesterday_values = self.session.query(CoinValue).filter(CoinValue.coin_id == current_id,
                                                                    # retrieve all of today's timestamps
                                                                    CoinValue.timestamp >= datetime(2025, 1, 29),
                                                                    CoinValue.timestamp < datetime(2025, 1,
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
        assembled_tuple = (coin_symbol, coin_name, today_price, percent_change)  # package data into a tuple
        return assembled_tuple  # return the assembled tuple

    def move_list_back(self):
        """
        Displays the previous 5 coins in the list if possible
        """
        screen = self.root.get_screen('select_coin_screen')  # retrieve coins
        list_box = screen.ids.coins_list_boxlayout  # retrieve list
        if list_box.searched_coins_list:  # as long as the list exists
            first_box = screen.ids.coins_list_boxlayout.children[-1]  # retrieve the first item
            first_tuple = (first_box.coin_code, first_box.coin_name, first_box.coin_value,
                           first_box.coin_percent_change)  # repackage the data into a tuple
            index = list_box.searched_coins_list.index(
                first_tuple)  # search list for the matching tuple to find the current index
            if index > 4:  # if there are at least 5 widgets preceding to be displayed
                screen.ids.coins_list_boxlayout.clear_widgets()  # clear the widgets
                for i in range(5):
                    (symbol, name, value, percent_change) = list_box.searched_coins_list[
                        index - 5 + i]  # retrieve values
                    screen.ids.coins_list_boxlayout.add_widget(
                        SelectCoinBox(coin_code=symbol, coin_name=name, coin_value=value,
                                      coin_percent_change=percent_change))  # display coin

    def move_list_forward(self):
        """
        Displays the next coins in the list if possible
        """
        screen = self.root.get_screen('select_coin_screen')
        list_box = screen.ids.coins_list_boxlayout
        if list_box.searched_coins_list:
            last_box = screen.ids.coins_list_boxlayout.children[0]  # select the last displayed coin
            last_tuple = (last_box.coin_code, last_box.coin_name, last_box.coin_value,
                          last_box.coin_percent_change)  # repackage the values into a tuple
            index = list_box.searched_coins_list.index(last_tuple)  # find the index of that coin

            if index < (len(list_box.searched_coins_list) - 5):  # if there are at least 5 coins left
                screen.ids.coins_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(5):  # for the next 5 coins
                    (symbol, name, value, percent_change) = list_box.searched_coins_list[
                        i + index + 1]  # retrieve values
                    screen.ids.coins_list_boxlayout.add_widget(
                        SelectCoinBox(coin_code=symbol, coin_name=name, coin_value=value,
                                      coin_percent_change=percent_change))  # display coin
            elif index != len(list_box.searched_coins_list) - 1:  # if there is at least 1 coin left
                screen.ids.coins_list_boxlayout.clear_widgets()  # remove all the rows
                for i in range(len(list_box.searched_coins_list) - index - 1):  # for the remaining coins
                    (symbol, name, value, percent_change) = list_box.searched_coins_list[
                        i + index + 1]  # retrieve values
                    screen.ids.coins_list_boxlayout.add_widget(
                        SelectCoinBox(coin_code=symbol, coin_name=name, coin_value=value,
                                      coin_percent_change=percent_change))  # display coin

    def select_coin(self, symbol):
        """
        set the values for the show history screen
        """
        try:
            selected_coin = self.session.query(Coin).filter(Coin.symbol == symbol).one()  # get the coin selected
        except sqlalchemy.exc.MultipleResultsFound:
            print("\nError: Multiple results found. Ensure the installer was only ran once.")
            sys.exit(1)
        except sqlalchemy.exc.NoResultFound:
            print("\nError: No results found. Ensure the symbol is correct.")
            sys.exit(1)
        screen = self.root.get_screen('view_history_screen')
        screen.symbol = symbol
        screen.coin_name = selected_coin.name

        selected_values = self.session.query(CoinValue).filter(
            CoinValue.coin_id == selected_coin.coin_id).all()  # find all values for that coin
        screen.coin_values = []
        for coin_value in selected_values:  # reassemble the values as a tuple
            assembled_tuple = (coin_value.timestamp, coin_value.price)
            screen.coin_values.append(assembled_tuple)
        self.display_month_chart()

    def display_chart(self, max_previous_time):
        """
        Create and display the chart for the history screen with given max_date
        """
        plt.clf()  # clear the current plot
        timestamps = []
        values = []
        screen = self.root.get_screen('view_history_screen')
        for value in screen.coin_values:
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
        screen = self.root.get_screen('view_history_screen')
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
        plt.title(screen.coin_name)  # title the graph
        screen.ids.chart_box.clear_widgets()  # remove the old chart
        screen.ids.chart_box.add_widget(FigureCanvasKivyAgg(plt.gcf()))  # add the new chart


if __name__ == '__main__':
    app = CryptoApp()
    app.run()
