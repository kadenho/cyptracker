
from kivy.modules import inspector
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from Tokenstaller.cryptos import Crypto, PortfolioEntry, CryptoPrice, ValueCheck, User, CryptoDatabase

#Main App Screens
class MySQLPasswordScreen(Screen):
    pass
class UserLoginScreen(Screen):
    pass
class CreateProfileScreen(Screen):
    pass
class MainDashboardScreen(Screen):
    pass
class AboutHelpScreen(Screen):
    pass



class CrypTrackerApp(App):
    def build(self):
        inspector.create_inspector(Window, self)
        self.update_usernames()
        self.sm = ScreenManager()
        self.sm.add_widget(MySQLPasswordScreen(name='MySQLPasswordScreen'))
        self.sm.add_widget(UserLoginScreen(name='UserLoginScreen'))
        self.sm.add_widget(CreateProfileScreen(name='CreateProfileScreen'))
        self.sm.add_widget(MainDashboardScreen(name='MainDashboardScreen'))
        self.sm.add_widget(AboutHelpScreen(name='AboutHelpScreen'))
        return self.sm

    #Main app buttons
    def on_login_button_press(self):
        self.sm.current = 'MainDashboardScreen'
    def on_create_username_page_button_press(self):
        self.sm.current = 'CreateProfileScreen'
    def on_switch_user_button_press(self):
        self.sm.current = 'UserLoginScreen'
    def on_about_help_button_press(self):
        self.sm.current = 'AboutHelpScreen'
    def on_about_help_back_button_press(self):
        self.sm.current = 'MainDashboardScreen'
    def on_enter_password_button_press(self):
        screen = self.sm.get_screen('MySQLPasswordScreen')
        try:
            password = screen.ids.password_text_input.text
            url = CryptoDatabase.construct_mysql_url('localhost', 3306, 'cryptos', 'root', password)
            self.crypto_database = CryptoDatabase(url)
            self.session = self.crypto_database.create_session()

            self.sm.current = 'UserLoginScreen'
        except Exception as e:
            print('Error connecting to MySQL:', e)
    def on_create_username_button_press(self):
        screen = self.sm.get_screen('CreateProfileScreen')
        username = screen.ids.new_username_text_input.text
        existing_user = self.session.query(User).filter_by(username=username)
        if screen.ids.new_username_text_input.text != '' or existing_user.count() == 0:
            try:
                new_user = User(username=username)
                self.session.add(new_user)
                self.session.commit()
                screen.ids.username_message_label = ''
                self.update_usernames()
                self.sm.current = 'UserLoginScreen'
            except Exception as e:
                print('Error with adding user to MySQL', e)
        else:
            screen.ids.username_message_label.text = 'Please enter a valid username.'
    def update_usernames(self):
        try:
            users = self.session.query(User).all()
            usernames = [user.username for user in users]
            self.usernames = usernames
            screen = self.sm.get_screen('UserLoginScreen')
            screen.ids.username_selector_spinner.values = usernames
        except Exception as e:
            print('Error with updating usernames', e)


if __name__ == '__main__':
    app = CrypTrackerApp()
    app.run()