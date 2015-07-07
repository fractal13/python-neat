import pygtk
pygtk.require('2.0')
import gtk
import gobject
import uttt_data


class TTTGUI:

    def __init__(self, data, send_queue):
        self.data = data
        self.send_queue = send_queue
        self.build_interface()
        self.register_handlers()
        return

    def build_login_interface(self):

        # Username
        self.username_label = gtk.Label("Username/Email")
        self.username_label.show()

        self.username_view = gtk.Entry(35)
        self.username_view.show()

        self.username_box = gtk.HBox(False, 0)
        self.username_box.pack_start(self.username_label, True, False)
        self.username_box.pack_start(self.username_view, True, True)
        self.username_box.show()

        # Password
        self.password_label = gtk.Label("Password")
        self.password_label.show()

        self.password_view = gtk.Entry(35)
        self.password_view.set_visibility(False)
        self.password_view.show()

        self.password_box = gtk.HBox(False, 0)
        self.password_box.pack_start(self.password_label, True, False)
        self.password_box.pack_start(self.password_view, True, True)
        self.password_box.show()

        # Login Button
        self.login_button = gtk.Button("Login")
        self.login_button.show()

        # Login Interface
        self.login_box = gtk.VBox(False, 0)
        self.login_box.pack_start(self.username_box,	True, True)
        self.login_box.pack_start(self.password_box,	True, True)
        self.login_box.pack_start(self.login_button,	True, True)
        self.login_box.show()

        return

    def build_signup_interface(self):

        # Username
        self.su_username_label = gtk.Label("Username")
        self.su_username_label.show()

        self.su_username_view = gtk.Entry(35)
        self.su_username_view.show()

        self.su_username_box = gtk.HBox(False, 0)
        self.su_username_box.pack_start(self.su_username_label, True, False)
        self.su_username_box.pack_start(self.su_username_view, True, True)
        self.su_username_box.show()

        # Email
        self.su_email_label = gtk.Label("Email")
        self.su_email_label.show()

        self.su_email_view = gtk.Entry(35)
        self.su_email_view.show()

        self.su_email_box = gtk.HBox(False, 0)
        self.su_email_box.pack_start(self.su_email_label, True, False)
        self.su_email_box.pack_start(self.su_email_view, True, True)
        self.su_email_box.show()

        # Password
        self.su_password_label = gtk.Label("Password")
        self.su_password_label.show()

        self.su_password_view = gtk.Entry(35)
        self.su_password_view.set_visibility(False)
        self.su_password_view.show()

        self.su_password_box = gtk.HBox(False, 0)
        self.su_password_box.pack_start(self.su_password_label, True, False)
        self.su_password_box.pack_start(self.su_password_view, True, True)
        self.su_password_box.show()

        # Confirm
        self.su_confirm_label = gtk.Label("Confirm")
        self.su_confirm_label.show()

        self.su_confirm_view = gtk.Entry(35)
        self.su_confirm_view.set_visibility(False)
        self.su_confirm_view.show()

        self.su_confirm_box = gtk.HBox(False, 0)
        self.su_confirm_box.pack_start(self.su_confirm_label, True, False)
        self.su_confirm_box.pack_start(self.su_confirm_view, True, True)
        self.su_confirm_box.show()

        # Sign up Button
        self.signup_button = gtk.Button("Sign up")
        self.signup_button.show()

        # Sign up Interface
        self.signup_box = gtk.VBox(False, 0)
        self.signup_box.pack_start(self.su_username_box,	True, True)
        self.signup_box.pack_start(self.su_email_box,	 True, True)
        self.signup_box.pack_start(self.su_password_box,	True, True)
        self.signup_box.pack_start(self.su_confirm_box,	 True, True)
        self.signup_box.pack_start(self.signup_button,	True, True)
        self.signup_box.show()

        return

    def build_wait_interface(self):

        # Message
        self.wait_label = gtk.Label("Please Wait")
        self.wait_label.show()

        # Wait Interface
        self.wait_box = gtk.VBox(False, 0)
        self.wait_box.pack_start(self.wait_label,	 True, True)
        self.wait_box.show()

        return

    def build_login_fail_interface(self):

        # Message
        self.login_fail_label = gtk.Label("Login Failed")
        self.login_fail_label.show()

        # Acknowledge Button
        self.login_fail_button = gtk.Button("OK")
        self.login_fail_button.show()

        # Login Fail Interface
        self.login_fail_box = gtk.VBox(False, 0)
        self.login_fail_box.pack_start(self.login_fail_label,	 True, True)
        self.login_fail_box.pack_start(self.login_fail_button,	True, True)
        self.login_fail_box.show()

        return

    def build_signup_fail_interface(self):

        # Message
        self.signup_fail_label = gtk.Label("Sign Up Failed")
        self.signup_fail_label.show()

        # Acknowledge Button
        self.signup_fail_button = gtk.Button("OK")
        self.signup_fail_button.show()

        # Signup Fail Interface
        self.signup_fail_box = gtk.VBox(False, 0)
        self.signup_fail_box.pack_start(self.signup_fail_label,	 True, True)
        self.signup_fail_box.pack_start(self.signup_fail_button,	True, True)
        self.signup_fail_box.show()

        return

    # This method builds all of the user interface elements
    # This is done bottom-up with detailed elements created
    # first, then added into larger containers.
    def build_interface(self):

        self.build_menubar()
        self.build_login_interface()
        self.build_signup_interface()
        self.build_wait_interface()
        self.build_login_fail_interface()
        self.build_signup_fail_interface()

        # Views Notebook
        self.notebook = gtk.Notebook()
        self.notebook.append_page(self.login_box)
        self.notebook.append_page(self.signup_box)
        self.notebook.append_page(self.wait_box)
        self.notebook.append_page(self.login_fail_box)
        self.notebook.append_page(self.signup_fail_box)
        self.notebook.set_show_tabs(False)
        self.notebook.set_current_page(0)
        self.notebook.show()

        # Everything
        self.top_box = gtk.VBox(False, 0)
        self.top_box.pack_start(self.menubar,	 False, False)
        self.top_box.pack_start(self.notebook,	False, False)
        self.top_box.show()

        # Window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.add(self.top_box)
        self.window.set_default_size(400, 300)
        self.window.show()

        return

    def build_menubar(self):

        # Menu Items
        self.login_item = gtk.MenuItem('Login')
        self.login_item.show()
        self.signup_item = gtk.MenuItem('Sign up')
        self.signup_item.show()
        self.quit_item = gtk.MenuItem('Quit')
        self.quit_item.show()

        # File Menu
        self.file_menu = gtk.Menu()
        self.file_menu.append(self.login_item)
        self.file_menu.append(self.signup_item)
        self.file_menu.append(self.quit_item)
        self.file_menu.show()

        # File Menu's Item in the Menubar
        self.file_menu_item = gtk.MenuItem('File')
        self.file_menu_item.set_submenu(self.file_menu)
        self.file_menu_item.show()

        # Finally, the Menubar
        self.menubar = gtk.MenuBar()
        self.menubar.append(self.file_menu_item)
        self.menubar.show()

        return

    # This methods connects handler methods to actions
    # on user interface elements.
    def register_handlers(self):
        self.login_item.connect('activate', self.show_login_handler)
        self.signup_item.connect('activate', self.show_signup_handler)
        self.quit_item.connect('activate', self.destroy_handler)

        self.username_view.connect('activate', self.login_handler)
        self.password_view.connect('activate', self.login_handler)
        self.login_button.connect('clicked', self.login_handler)

        self.su_username_view.connect('activate', self.signup_handler)
        self.su_email_view.connect('activate', self.signup_handler)
        self.su_password_view.connect('activate', self.signup_handler)
        self.su_confirm_view.connect('activate', self.signup_handler)
        self.signup_button.connect('clicked', self.signup_handler)

        self.login_fail_button.connect('clicked', self.login_fail_handler)
        self.signup_fail_button.connect('clicked', self.signup_fail_handler)

        self.window.connect('delete_event', self.delete_event_handler)
        self.window.connect('destroy', self.destroy_handler)

        return

    # This method never returns, because gtk.main() doesn't.
    def run(self):
        self.monitor_id = gobject.timeout_add(1000, self.timeout_handler)
        gtk.main()
        return

    def timeout_handler(self):
        if not self.data:
            return False

        state = self.data.GetState()
        print "GTK:CurrentState:", state
        if state == uttt_data.STATE_SHOW_LOGIN:
            self.window.deiconify()
            self.notebook.set_current_page(0)
        elif state == uttt_data.STATE_SHOW_SIGNUP:
            self.window.deiconify()
            self.notebook.set_current_page(1)
        elif state == uttt_data.STATE_WAIT_LOGIN or state == uttt_data.STATE_WAIT_SIGNUP:
            self.window.deiconify()
            self.notebook.set_current_page(2)
        elif state == uttt_data.STATE_LOGIN_FAIL:
            self.window.deiconify()
            self.notebook.set_current_page(3)
        elif state in [
            uttt_data.STATE_SIGNUP_FAIL_USERNAME, uttt_data.STATE_SIGNUP_FAIL_EMAIL,
                uttt_data.STATE_SIGNUP_FAIL_PASSWORD, uttt_data.STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED]:
            self.window.deiconify()
            self.notebook.set_current_page(4)
        elif state == uttt_data.STATE_SIGNUP_OK:
            username = self.su_username_view.get_text()
            password = self.su_password_view.get_text()
            text = self.data.SendLogin(username, password)
            print "gtk: queuing: %s" % (text, )
            self.send_queue.put(text)
            self.window.deiconify()
            self.notebook.set_current_page(2)
        elif state in [
            uttt_data.STATE_WAIT_GAME, uttt_data.STATE_SHOW_GAME, uttt_data.STATE_GAME_OVER,
                uttt_data.STATE_TURN_FAILED, uttt_data.STATE_WAIT_TURN]:
            self.window.iconify()
        elif state == uttt_data.STATE_SOCKET_CLOSED:
            print "Socket closed, GTK will quit."
            gtk.main_quit()
        else:
            print "UNKNOWN STATE in GTK"
        return True

    # This method is called by the 'X' button on the window,
    # or as a result of gtk.main_quit()
    def delete_event_handler(self, widget, event, data=None):
        # return False to indicate that we agree with the window
        # being deleted.
        return False

    # This method is called by the 'login' menu item
    def show_login_handler(self, widget, data=None):
        if self.data:
            if self.data.GetState() == uttt_data.STATE_SHOW_SIGNUP:
                self.notebook.set_current_page(0)
                self.data.ShowLogin()
        else:
            self.notebook.set_current_page(0)
        return

    # This method is called by the 'signup' menu item
    def show_signup_handler(self, widget, data=None):
        if self.data:
            if self.data.GetState() == uttt_data.STATE_SHOW_LOGIN:
                self.notebook.set_current_page(1)
                self.data.ShowSignUp()
        else:
            self.notebook.set_current_page(1)
        return

    # This method is called by the 'quit' button
    def destroy_handler(self, widget, data=None):
        gtk.main_quit()
        return

    # This method is called by the 'login' button
    def login_handler(self, widget, data=None):
        username = self.username_view.get_text()
        password = self.password_view.get_text()
        print "username=", username, "	 password=", password
        if self.data and self.send_queue:
            text = self.data.SendLogin(username, password)
            print "gtk: queuing: %s" % (text, )
            self.send_queue.put(text)
            self.notebook.set_current_page(2)
        return

    # This method is called by the 'signup' button
    def signup_handler(self, widget, data=None):
        username = self.su_username_view.get_text()
        email = self.su_email_view.get_text()
        password = self.su_password_view.get_text()
        confirm = self.su_confirm_view.get_text()
        print "username=", username, "	 email=", email, "	 password=", password, "	confirm=", confirm
        if self.data and self.send_queue:
            text = self.data.SendSignUp(username, email, password, confirm)
            print "gtk: queuing: %s" % (text, )
            self.send_queue.put(text)
            self.notebook.set_current_page(2)
        return

    # This method is called by the 'login fail' button
    def login_fail_handler(self, widget, data=None):
        if self.data:
            self.data.ShowLogin()
        self.notebook.set_current_page(0)
        return

    # This method is called by the 'signup fail' button
    def signup_fail_handler(self, widget, data=None):
        if self.data:
            self.data.ShowSignUp()
        self.notebook.set_current_page(1)
        return


def uttt_gtk_main(data, send_queue):
    gui = TTTGUI(data, send_queue)
    gui.run()
    return

if __name__ == "__main__":
    uttt_gtk_main(None, None)
