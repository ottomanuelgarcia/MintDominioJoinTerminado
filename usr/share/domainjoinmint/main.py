#!/usr/bin/env python3
# /usr/share/domainjoinmint/main.py

import os
import sys
import locale
import gettext
import subprocess
import threading
import configparser
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gio

# Internationalization Setup
APP_NAME = 'domainjoinmint'
LOCALE_DIR = '/usr/share/locale'
if not os.path.exists(LOCALE_DIR):
    # Local development fallback
    LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locales')

def setup_i18n():
    try:
        gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
        gettext.textdomain(APP_NAME)
        gettext.install(APP_NAME, LOCALE_DIR)
    except Exception as e:
        print(f"Error setting up i18n: {e}")

setup_i18n()
_ = gettext.gettext

class DomainJoinApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.mint.domainjoin",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None

    def do_activate(self):
        if not self.window:
            self.setup_ui()
        self.window.present()

    def set_window_icon(self):
        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.has_icon("domainjoinmint"):
            self.window.set_icon_name("domainjoinmint")
        else:
            icon_paths = [
                "/usr/share/icons/hicolor/256x256/apps/domainjoinmint.png",
                "/usr/share/pixmaps/domainjoinmint.png",
                os.path.join(os.path.dirname(__file__), "domainjoinmint.png")
            ]
            for path in icon_paths:
                if os.path.exists(path):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
                        self.window.set_icon(pixbuf)
                        break
                    except:
                        continue
        self.window.set_wmclass("DomainJoinMint", "DomainJoinMint")

    def setup_ui(self):
        self.window = Gtk.ApplicationWindow(application=self, title=_("Domain Join Mint"))
        self.window.set_default_size(500, 600)
        self.window.set_border_width(15)
        self.set_window_icon()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(vbox)

        # Title
        label_title = Gtk.Label(label=f"<b>{_('Domain Join Mint')}</b>")
        label_title.set_use_markup(True)
        label_title.set_margin_bottom(10)
        vbox.pack_start(label_title, False, False, 0)

        # Form Grid
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        vbox.pack_start(grid, False, False, 0)

        # Domain
        grid.attach(Gtk.Label(label=_("Domain"), halign=Gtk.Align.START), 0, 0, 1, 1)
        self.entry_domain = Gtk.Entry(hexpand=True)
        grid.attach(self.entry_domain, 1, 0, 1, 1)
        btn_search = Gtk.Button(label=_("Search"))
        btn_search.connect("clicked", self.on_search_clicked)
        grid.attach(btn_search, 2, 0, 1, 1)

        # User
        grid.attach(Gtk.Label(label=_("Username"), halign=Gtk.Align.START), 0, 1, 1, 1)
        self.entry_user = Gtk.Entry(hexpand=True)
        grid.attach(self.entry_user, 1, 1, 2, 1)

        # Password
        grid.attach(Gtk.Label(label=_("Password"), halign=Gtk.Align.START), 0, 2, 1, 1)
        self.entry_pass = Gtk.Entry(hexpand=True, visibility=False, caps_lock_warning=True)
        grid.attach(self.entry_pass, 1, 2, 2, 1)

        # Sudo Checkbox
        self.check_sudo = Gtk.CheckButton(label=_("Grant Sudo access to Domain Admins"))
        self.check_sudo.set_active(True)
        vbox.pack_start(self.check_sudo, False, False, 0)

        # Buttons
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bbox.set_layout(Gtk.ButtonBoxStyle.END)
        vbox.pack_start(bbox, False, False, 10)

        btn_join = Gtk.Button(label=_("Join Domain"))
        btn_join.get_style_context().add_class("suggested-action")
        btn_join.connect("clicked", self.on_join_clicked)
        bbox.add(btn_join)

        btn_cancel = Gtk.Button(label=_("Cancel"))
        btn_cancel.connect("clicked", lambda x: self.quit())
        bbox.add(btn_cancel)

        # Progress
        self.spinner = Gtk.Spinner()
        vbox.pack_start(self.spinner, False, False, 0)

        # Log
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(150)
        self.log_view = Gtk.TextView(editable=False, cursor_visible=False)
        self.log_view.set_monospace(True)
        scrolled.add(self.log_view)
        vbox.pack_start(scrolled, True, True, 0)

        # Footer
        footer = Gtk.Label()
        footer.set_markup(f"<small>{_('Developed by: Otto Manuel Garcia Preval')}</small>")
        vbox.pack_start(footer, False, False, 5)

        self.window.show_all()

    def log(self, text):
        GLib.idle_add(self._log_idle, text)

    def _log_idle(self, text):
        buffer = self.log_view.get_buffer()
        iter = buffer.get_end_iter()
        buffer.insert(iter, f"> {text}\n")
        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.log_view.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)

    def on_search_clicked(self, btn):
        self.log(_("Scanning for domains..."))
        threading.Thread(target=self._do_search).start()

    def _do_search(self):
        try:
            res = subprocess.run(['realm', 'discover'], capture_output=True, text=True)
            self.log(res.stdout if res.stdout else _("No domains found."))
        except Exception as e:
            self.log(str(e))

    def on_join_clicked(self, btn):
        domain = self.entry_domain.get_text()
        user = self.entry_user.get_text()
        password = self.entry_pass.get_text()

        if not all([domain, user, password]):
            self.log(_("Please enter all required fields"))
            return

        self.spinner.start()
        self.log(_("Starting join process..."))
        threading.Thread(target=self._do_join, args=(domain, user, password)).start()

    def _do_join(self, domain, user, password):
        try:
            # Install
            self.log(_("Verifying dependencies..."))
            pkgs = ["realmd", "sssd", "sssd-tools", "libnss-sss", "libpam-sss", "adcli", "samba-common-bin", "krb5-user", "packagekit"]
            subprocess.run(['pkexec', 'apt-get', 'install', '-y'] + pkgs, check=True)

            # Realm Join
            self.log(_("Joining domain..."))
            join_cmd = ['pkexec', 'realm', 'join', '-U', user, domain]
            process = subprocess.Popen(join_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input=password)
            
            if process.returncode != 0:
                raise Exception(stderr or stdout)

            # PAM
            subprocess.run(['pkexec', 'pam-auth-update', '--enable', 'mkhomedir'], check=True)

            # Sudoers
            if self.check_sudo.get_active():
                sudo_rule = f'%Domain\ Admins@ {domain} ALL=(ALL) ALL'
                subprocess.run(['pkexec', 'sh', '-c', f'echo \'{sudo_rule}\' > /etc/sudoers.d/domain_admins'], check=True)

            self.log(_("Success! Reboot recommended."))
            GLib.idle_add(self._show_success)
        except Exception as e:
            self.log(f"{_('Failed to join domain')}: {e}")
        finally:
            GLib.idle_add(self.spinner.stop)

    def _show_success(self):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Success")
        )
        dialog.format_secondary_text(_("System successfully joined to the domain. Please restart."))
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = DomainJoinApp()
    app.run(sys.argv)
