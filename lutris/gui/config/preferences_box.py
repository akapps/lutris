from gettext import gettext as _

from gi.repository import Gtk, Gio

from lutris.gui.dialogs import ErrorDialog
from lutris.runtime import RuntimeUpdater

from lutris.gui.config.base_config_box import BaseConfigBox


def trigger_runtime_update(parent):
    application = Gio.Application.get_default()
    if application:
        window = application.window
        if window:
            if window.download_queue.is_empty:
                updater = RuntimeUpdater(application.gpu_info)
                updater.update_runtime = True
                window.install_runtime_updates(updater)
            else:
                ErrorDialog(_("Updates cannot begin while downloads are already underway."), parent=parent)


class InterfacePreferencesBox(BaseConfigBox):
    settings_options = {
        "hide_client_on_game_start": _("Minimize client when a game is launched"),
        "hide_text_under_icons": _("Hide text under icons"),
        "hide_badges_on_icons": _("Hide badges on icons (Ctrl+p to toggle)"),
        "show_tray_icon": _("Show Tray Icon"),
        "dark_theme": _("Use dark theme (requires dark theme variant for Gtk)"),
        "discord_rpc": _("Enable Discord Rich Presence for Available Games"),
    }

    settings_accelerators = {
        "hide_badges_on_icons": "<Primary>p"
    }

    def __init__(self, accelerators):
        super().__init__()
        self.accelerators = accelerators
        self.add(self.get_section_label(_("Interface options")))
        frame = Gtk.Frame(visible=True, shadow_type=Gtk.ShadowType.ETCHED_IN)
        listbox = Gtk.ListBox(visible=True)
        frame.add(listbox)
        self.pack_start(frame, False, False, 12)
        for setting_key, label in self.settings_options.items():
            list_box_row = Gtk.ListBoxRow(visible=True)
            list_box_row.set_selectable(False)
            list_box_row.set_activatable(False)
            list_box_row.add(self.get_setting_box(setting_key, label))
            listbox.add(list_box_row)


class UpdatePreferencesBox(BaseConfigBox):
    settings_options = {
        "auto_update_runtime": {
            "label": _("Automatically update the Lutris runtime"),
            "default": True,
            "update_function": trigger_runtime_update
        },
        "auto_update_runners": {
            "label": _("Automatically update Wine"),
            "default": True,
            "warning":
                _("<b>Warning</b> The Lutris Team does not support running games on old version of Wine.\n"
                  "<i>Automatic Wine updates are strongly recommended.</i>"),
            "warning_condition": lambda active: not active
        }
    }

    def __init__(self):
        super().__init__()
        self.add(self.get_section_label(_("Update options")))
        frame = Gtk.Frame(visible=True, shadow_type=Gtk.ShadowType.ETCHED_IN)
        listbox = Gtk.ListBox(visible=True)
        frame.add(listbox)
        self.pack_start(frame, False, False, 12)
        for setting_key, setting_option in self.settings_options.items():
            label = setting_option["label"]
            default = setting_option.get("default") or False
            warning_markup = setting_option.get("warning")
            warning_condition = setting_option.get("warning_condition")
            update_function = setting_option.get("update_function")

            if update_function:
                def on_update_now_clicked(_widget, func):
                    func(self.get_toplevel())

                update_button = Gtk.Button(_("Update Now"), halign=Gtk.Align.END, visible=True)
                update_button.connect("clicked", on_update_now_clicked, update_function)
            else:
                update_button = None

            list_box_row = Gtk.ListBoxRow(visible=True)
            list_box_row.set_selectable(False)
            list_box_row.set_activatable(False)
            list_box_row.add(self.get_setting_box(setting_key, label, default=default,
                                                  warning_markup=warning_markup,
                                                  warning_condition=warning_condition,
                                                  extra_widget=update_button))
            listbox.add(list_box_row)
