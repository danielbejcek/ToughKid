"""
Welcome to my first project ToughKid.

This project took me around 2-3 months of work with close to zero experience,
please understand that this code is a work of an enthusiast and a amateur.

The idea behind this project was to release pressure and save valuable time of shift managers,
who need to distribute specific positions to relevant employees.

Up until now, every manager in our small company needed to come to work earlier to sit behind a computer and collect data
about employees, who are supposed to work on that specific shift from Google Sheets table.
Then he needed to look for every employee who has a 'X' symbol next to his name
and after that, copy all of those names into a final table, which he then proceeded to take a picture of and share it in a WhatsApp group.

This small application will make their lives easier, everything is combine into this small pocket project.

This App pulls data from Google Sheets table automatically and allows the user the fill the table without the need to verify,
if the employee in-fact works that day.

Along this long process of creating this app, I have been using getting alot of help, mainly from Stack Overflow, Youtube, Github and google overall.
This app is then finalized and complied trough usage of Buildozer and Windows Subsystem for Linux.

"""

import kivy
import pyparsing
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from kivy.core.window import Window
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
gc = gspread.authorize(creds)
sh = gc.open("Your Database")


# Returns a list of worksheet titles
worksheet_list = []
for worksheet in sh.worksheets():
    worksheet_list.append(worksheet.title)


class FirstPageLayout(Screen):

# Builds a series of buttons trough a loop, each button is then set off by a 0.1 to prevent them from overlapping.
    def month_list(self):
        self.custom_height = 1
        for month in worksheet_list:
            self.custom_height = self.custom_height - 0.1
            self.btn = Button(
                text=month,
                font_name='BrunoAceSC-Regular.ttf',
                font_size=40,
                pos_hint={"center_x": .5, 'center_y': self.custom_height},
                background_color=(.5, .5, .5, .75),
                on_press=self.button_id)
            self.btn.my_id = month
            self.btn.bind(on_release=self.switch_screen)
            self.ids.GLM.add_widget(self.btn)

# Binds a function to a button when pressed, saves a variable 'month_name',
# which is also global variable and is later used to display data corresponding to a specified month.

    def button_id(self, month_id):
        global month_name
        month_name = (str(month_id.my_id))

# Allows to make a transition to a specified screen.
    def switch_screen(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = "Second"

    def remove_btn1(self, button):
        bl1 = self.ids.BL1
        bl1.remove_widget(button)


class SecondPageLayout(Screen):

# Global variable 'month_name' is used here from previous class to load data from a specific worksheet.
    def flight_list(self):
        month_sheet = sh.worksheet(month_name)
        flights_list = []
        # Gets all the values from specified rows into a 'row' variable.
        # 1 = Date, 2 = Carrier and 3 = zimun, which stands for start of the shift.
        row1 = month_sheet.row_values(1)
        row3 = month_sheet.row_values(3)
        row5 = month_sheet.row_values(5)

        for date, carrier, zimun in zip(row1, row3, row5):
            # If there is no zimun(start of the shift) nor carrier, means that there is no flight to be selected.
            if not zimun or not carrier:
                pass
            else:
                flights_list.append(f"{date}, {carrier}, {zimun}")

        # Cycles trough a series of flights in a specified month and displays all of the flights as clickable buttons.
        for flight in flights_list:
            self.btn_flights = Button(
                text=flight,
                font_name='BrunoAceSC-Regular.ttf',
                font_size=35,
                size_hint_y=None,
                size_hint_x=.6,
                pos_hint={"center_x": .5, "center_y": 1},
                background_color=(.5, .5, .5, 1),
                # On release triggers 'flight_id' function that stores values of a button that was clicked,
                # this value is later used to display employees working on this shift.
                on_release=self.flight_id)
            self.ids.SL3.add_widget(self.btn_flights)

            # ID of a button is a index value from a 'flight_list' loop. Used as a corresponding variable for later use.
            self.btn_flights.my_id = flight

            # This line of code allows for the scrolling feature of all of those buttons to happen.
            self.ids.SL3.bind(minimum_height=self.ids.SL3.setter('height'))
            self.btn_flights.bind(on_release=self.switch_screen_third)

    def flight_id(self, flight_id):
        # Variable 'flight_name' is once again used as Global variable to allow usage in following class.
        global flight_name
        flight_name = (str(flight_id.my_id))

    def disable_btn(self):
        self.ids.btn2.disabled = True

    def enable_btn(self):
        self.ids.btn2.disabled = False

    def switch_screen_third(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = "Third"

    def remove_btn_flight(self):
        self.ids.SL3.clear_widgets()


class ThirdPageLayout(Screen):
    def __init__(self, **kwargs):
        super(ThirdPageLayout, self).__init__(**kwargs)

        # General snippet used for modifiyng the keyboard behaviour. Once this code is applied,
        # the keyboard should now be dynamic when text input field is active. Meaning, whenever there is a textinput hidden behind a keyboard screen,
        # the text input will be elevated just above the cellphone keyboard so the user can see what he is typing.
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
        Window.softinput_mode = "below_target"

        # Trigger boolean here servers as an option to not run a specific code (therefore set to False from the beginning).
        # The idea behind is that, when a user enters this screen for the first time,
        # all of this block of code below will be fired. Meaning all of the buttons with employee names will be loaded,
        # all of the text input entries will be empty and ready to be filled with values. More explanation further down.
        self.trigger = False


    # 'on_enter' method triggers everything as soon as the screen is accessed by the user.
    def on_enter(self):

        # All of the code below is encapsuled by a trigger condition. When 'trigger' is set to True, code block below will be skipped.
        # The idea behind it is, when user is finished with distributing the positions and is ready to proceed to the final screen,
        # but then notices that he made a mistake. Skipping this block of code allows him to keep the original values that have already been entered by him.
        # Otherwise without this 'trigger' condition, all of the values will be deleted and the screen will be 'remade fresh',
        # because of these methods which are fired when the screen is entered.
        if not self.trigger:
            self.flight_label = Label(
                text=flight_name,
                font_name='BrunoAceSC-Regular.ttf',
                font_size=20)
            self.ids.BL4.add_widget(self.flight_label)

            # 'listed_flight' takes the whole flight_name variable and splits it into 3 different parts (date, carrier and start of the shift) for further use.
            listed_flight = flight_name.split(", ")
            # Once again Global variable 'month_name' is used here to help access a desired month.
            month_worksheet = sh.worksheet(month_name)
            flight_date = listed_flight[0]
            flight_carrier = listed_flight[1]
            flight_zimun = listed_flight[2]


            # 'date' variable takes a splitted string from 'flight_name' and proceeds to find a cell in the worksheet that matches the same string.
            date = month_worksheet.findall(flight_date)


            # 'names_list' takes all of the values from column 1 in the worksheet which contains names of all the employees,
            # plus some additional information that is later on sliced and deleted.
            names_list = month_worksheet.col_values(1)
            del names_list[36:]
            del names_list[:13]

            # This code provides final values with employees working on a specific shift.
            shift_list = []
            for cell in date:

                # 'cell_col_number' variable takes a 'cell' from 'date'(explained above) which contains a specific column values.
                cell_col_number = cell.col

                # 'col_data' is variable that contains all of the values from a desired column.
                col_data = month_worksheet.col_values(cell_col_number)

                # Carrier and the time when the shift is starting is present within the column (meaning that the value is not Null).
                # Some of the columns are infact empty, for example on Saturday, there is no flight. I didn't want an empty flight information to be displayed.
                if flight_carrier and flight_zimun in col_data:

                    # Here we append the values from 'col_data' to an empty list, which will be later used as a corresponding factor.
                    # For example now, the empty list contains all of the data from a column, even if the employee doesn't work on that spcific shift.
                    # The list could have following data: ['x','','VCT','','X'],
                    # where 'X' means that employee is planned for the shift, '' empty string means day off and 'VCT' stands for vacation.
                    # Of course, I dont't want to organize and distribute positions for shift, when some of the employees in the list have a day off
                    # and/or are on a vacation. These discrepancies are filtered out in the following code bellow.
                    for shift in col_data:
                        shift_list.append(shift)

            # Here we slice and delete an unnecessary information from the list such as date, carrier, start of the shift etc.
            # The idea is to have a clean list of entries that we can later connect to a specific employee.
            del shift_list[36:]
            del shift_list[:13]

            # This code bellow serves as a connecting point between a name of the employee and the value in the column in the same row as is his name.
            # Here we create an empty list, which will be filled with list of dictionaries.
            names_dictionary = []

            # With a use of a for loop we cycle trough the 'names_list', which contains all of the employee names, we also set a new variable 'x' with value of -1.
            # This values is automaticaly incremented by 1 with every single cycle. This allows me to continuously merge 'one_name' with a value from 'shift_list'.
            # Result now could potentialy look like this:
            # {Daniel: 'X'}
            # {Ivan: ''}
            # {Noy: 'VCT'}
            x = -1
            for index, one_name in enumerate(names_list):
                x += 1
                names_dictionary.append({one_name: [shift_list[x]]})

            # Now that we have a list of dictionaries with corresponding values, where every KEY(employee name) is connected to the VALUE(fact if the employee is wokring or not).
            # We need to filter out those employees, who are not available for the shift. Meaning they are on a vacation or have a day off.
            final_list = []
            for names in names_dictionary:
                for key, value in names.items():

                    # In this code we check if the KEY (employee) has a certain VALUE connected to his name, which proves his availability for the shift.
                    if any('X' in val for val in value) or ('GUIDE' in value) or ('HAF' in value):

                        # Where 'X' stands for working,
                        # 'GUIDE' stands for also working, but acting as a person who escorts other employees who do not have a permanent identification card.
                        # 'HAF' is short for Hafifa, which is a Hebrew word for training.
                        # If one of those conditions is met, employee's name is added to the 'final_list' of employees.
                        final_list.append(key)

            position_list = ["Bachir", "Mafrid", "Searches", "Sniffers", "CT 1", "CT 2", "CT 3", "Matos 1", "Petah",
                             "Matos 2", "Matos 3", "Gate 1", "Gator", "Guide", "Star", "C/I"]

            # From the list 'position_list' we create a series of lables that serve as a main construction for the final table,
            # where employee names will be asigned to these positions.
            for position in position_list:
                self.position_label = Label(
                    text=position,
                    font_name='BrunoAceSC-Regular.ttf',
                    halign="left",
                    valign="middle")
                self.ids.BL2.add_widget(self.position_label)

            # Creating buttons with employee names from a 'final_list'. Each button created binds a function to them.
            # 'disabled' attribute is used to divide between buttons that have already been pressed or asigned and buttons,
            # that have yet to be asigned to a position.
            self.selected_btn = None
            for i, name in enumerate(final_list):
                self.name_btn = ToggleButton(
                    text=name,
                    font_name='BrunoAceSC-Regular.ttf',
                    font_size=20,
                    background_color=(.5, .5, .5, 1),
                    group="Employees",
                    on_press=self.select_name,
                    state="normal",
                    disabled=False)
                self.ids.GL4.add_widget(self.name_btn)

            # With a use of a loop we create 16 empty text input fields. There are few functions bound to this widget.
            # First attribute worth mentioning is 'is_focusable=False', when user has a button selected and proceeds to
            # add the value from the button into the empty text input field by simply clickling into it.
            # The text is automatically transfered without the text input being focused (the android keyboard won't pop up),
            # preventing a nondesirable need to close the keyboard everytime we fill the text input with a name.

            # Another method is a 'enable_focus', which allows the user to focus into the text input field manualy,
            # by double tapping the corresponding field. Allowing him to type text into it.

            # 'on_empty_text_touch' method is the logic behind importing a text value from a selected button into the text input field.
            # First we check if user has selected the button ('self.selected_btn is not None'),
            # then we verify if appropriate field has been selected ('instance.collide_point(*touch.pos)')
            # and at last we need to make sure that the text input field is empty and available to recieve a value from a selected button ('instance.text = ""').
            # If all of these conditions are met, we proceed to transfer the value from a button into the text field ('instance.text = self.selected_btn.text').
            for empty_text_input in range(16):
                self.empty_text = TextInput(
                    text="",
                    multiline=False,
                    font_name='BrunoAceSC-Regular.ttf',
                    halign="center",
                    size_hint=(1, 1),
                    background_color=(.5, .5, .5, 1),
                    allow_copy=False,
                    is_focusable=False,
                    use_bubble=False,
                    use_handles=False,
                    cursor_color=(.1, .1, .1, 1))
                self.empty_text.bind(on_touch_down=self.enable_focus)
                self.empty_text.bind(on_touch_down=self.on_empty_text_touch)
                self.empty_text.bind(text=self.check_text_input)
                self.ids.BL3.add_widget(self.empty_text)

            self.button_input_mapping = {}



    def on_empty_text_touch(self, instance, touch):
        index = self.ids.BL3.children.index(instance)
        if self.selected_btn is not None and instance.collide_point(*touch.pos) and instance.text == "":
            instance.text = self.selected_btn.text
            self.button_input_mapping[self.selected_btn] = instance

            # These indices are specific to a position, once a name is assigned to one of these positions bellow, the name button will not be disabled,
            # allowing further use of the button ergo employee.
            if index == 1:
                self.selected_btn.disabled = False
            elif index == 12:
                self.selected_btn.disabled = False
            elif index == 13:
                self.selected_btn.disabled = False
            else:
                self.selected_btn.disabled = True
            self.selected_btn = None

    # Method that allows to type into text input field after double tapping on it.
    def enable_focus(self, instance, touch):
        if touch.is_double_tap:
            instance.is_focusable = True
        else:
            instance.is_focusable = False

    # This method configures the 'disabled' attribute of the button. Once button is pressed, it automatically becomes disabled.
    # Also, 'self.selected_btn' now stores a value which is equal to the instance, which is now the text value stored in the button.
    def select_name(self, instance):
        if self.selected_btn is not None:
            self.selected_btn.disabled = False
        self.selected_btn = instance
        self.selected_btn.disabled = True

    # With this method we check the text input field for value. Allowing us to control the button availablity.
    # When value inside the text is an empty string (the name was manually deleted by user),
    # button with a corresponding name will be once again available.
    def check_text_input(self, instance, value):
        if value == "":
            for button, text_input in self.button_input_mapping.items():
                if text_input == instance:
                    button.disabled = False
                    del self.button_input_mapping[button]  # Remove association from the dictionary
                    break

    # Here we define a global empty list for use in the last page.
    # We cycle trough all of the values(names of employees) that have been added by the user into the text input field.
    # Once there is no name record in the field, '-' sign will be added to represent an empty postition.
    def final_employee_names(self):
        global final_employee_list
        final_employee_list = []
        for text_input in self.ids.BL3.children:
            name = text_input.text.strip()  # Get the text value from the TextInput
            if name:  # Only add non-empty names to the list
                final_employee_list.append(name)
            else:
                final_employee_list.append('-')

    def remove_btns(self):
        self.ids.GL4.clear_widgets()
        self.ids.BL2.clear_widgets()
        self.ids.BL3.clear_widgets()

    def on_leave(self, *args):
        self.trigger = False
        self.ids.BL4.remove_widget(self.flight_label)


class FinalScreen(Screen):
    def __init__(self, **kwargs):
        super(FinalScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        position_list = ["Bachir", "Mafrid", "Searches", "Sniffers", "CT 1", "CT 2", "CT 3", "Matos 1", "Petah",
                         "Matos 2", "Matos 3", "Gate 1", "Gator", "Guide", "Star", "C/I"]

        for position in position_list:
            self.position_label = Label(
                text=position,
                font_size=32,
                font_name='BrunoAceSC-Regular.ttf',
                halign="left",
                valign="middle")
            self.ids.BL5.add_widget(self.position_label)

        final_employee_list.reverse()
        for name in final_employee_list:
            self.employee_name = Label(
                text=name,
                font_size=32,
                font_name='BrunoAceSC-Regular.ttf',
                halign="left",
                valign="middle")
            self.ids.BL6.add_widget(self.employee_name)

    def on_touch_down(self, touch):
        if not touch.is_mouse_scrolling:
            self.start_x = touch.x

    # Method that enables the trigger condition. When user transitions from Final Screen page to a previous one,
    # all data will be kept the same as they were, allowing the user to continue exactly where he left off.
    # Also this combines a touch and slide transition feature, where user in order to access a previous page to modify some positions,
    # he simply needs to slide his finger from left to right.
    def on_touch_move(self, touch):
        self.manager.get_screen("Third").trigger = True
        if not touch.is_mouse_scrolling:
            if touch.dx > 50 and touch.x > self.start_x:
                self.manager.transition.direction = 'right'
                self.manager.current = 'Third'


    def on_leave(self, *args):
        self.ids.BL5.clear_widgets()
        self.ids.BL6.clear_widgets()


class WindowManager(ScreenManager):
    pass


class ToughKid(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FirstPageLayout(name='First'))
        sm.add_widget(SecondPageLayout(name="Second"))
        sm.add_widget(ThirdPageLayout(name="Third"))
        sm.add_widget(FinalScreen(name='Final'))
        self.icon = "Images/Logo.png"
        return sm


if __name__ == "__main__":
    ToughKid().run()





