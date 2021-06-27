from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
from desktop_file_dialogs import Desktop_FileDialog, Desktop_FolderDialog, FileGroup
from pathlib import Path
from pathvalidate import sanitize_filename
from schematic_generator import generate_schematic

import os

class ResultPopup(FloatLayout):
    exit = ObjectProperty(None)
    result = StringProperty(None)


class Root(FloatLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.selected_input_path = ''
        self.output_filename = ''
        self.selected_output_dir = os.path.join(os.environ.get('appdata'), '.minecraft', 'schematics')


    def dismiss_popup(self):
        self.result_popup.dismiss()

    def select_midi_file(self):
        Desktop_FileDialog(
          title             = "Select Midi File",
          initial_directory = os.path.dirname(self.selected_input_path),
          on_cancel         = self.on_cancel_file_or_dir,
          on_accept         = self.on_accept_file,
          file_groups = [
            FileGroup(name="Midi Files", extensions=["midi, mid"]),
          ],
        ).show()

    def select_save_path(self):
        Desktop_FolderDialog(
            title = 'Select Output Directory',
            initial_directory = self.selected_output_dir,
            on_accept = self.on_accept_folder,
            on_cancel = self.on_cancel_file_or_dir
        ).show()

    def on_accept_file(self, path):
        self.selected_input_path = path
        self.ids.midi_file_label.text = path

        if self.output_filename == '':
            self.output_filename = os.path.splitext(os.path.basename(path))[0]
            self.ids.output_filename_label.text = self.output_filename

        print(f"Selected MIDI File: {path}")

    def on_accept_folder(self, path):
        self.selected_output_dir = path
        self.ids.output_directory_label.text = path
        print(f"Selected Folder: {path}")

    def on_cancel_file_or_dir(self):
        print('No File or Folder was selected')

    def submit(self):
        self.selected_input_path = self.ids.midi_file_label.text
        self.selected_output_dir = self.ids.output_directory_label.text
        self.output_filename = self.ids.output_filename_label.text
        
        if self.selected_input_path == '':
            self.show_result('Input MIDI file missing')
            return
        elif self.output_filename == '':
            self.show_result('Output Filename not given')
            return
        elif self.selected_output_dir == '':
            self.show_result('Output Directory not given')
            return
        elif not os.path.isfile(self.selected_input_path):
            self.show_result('Selected Input File not found')
            return

        self.output_filename = f'{self.output_filename}.litematic'

        Path(self.selected_output_dir).mkdir(parents=True, exist_ok=True)
        self.output_filename = sanitize_filename(self.output_filename)

        out_filepath = os.path.join(self.selected_output_dir, self.output_filename)
        generate_schematic(self.selected_input_path, out_filepath)

        self.show_result(f'File {out_filepath} was successfully created!')

    def show_result(self, result):
        result_content = ResultPopup(exit=self.dismiss_popup, result=result)
        # result_content.result = result

        self.result_popup = Popup(title='Result', content=result_content, size_hint=(0.9, 0.9))
        self.result_popup.open()
        print(result)

class Editor(App):
    icon = 'ico/icon.png'
    
    def build(self):
        self.title = 'Minecraft Noteblock Schematic Generator'
        Window.minimum_width = 500
        Window.minimum_height = 450

Factory.register('Root', cls=Root)
Factory.register('Result', cls=ResultPopup)

if __name__ == '__main__':
    Editor().run()