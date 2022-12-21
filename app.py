# HBNetMon is an attempt at a progressive web application using a server driven UI
# that will allow individual network operators to have a type of dashboard "app".
#
# Copyright (C) 2022 Eric Craw, KF7EEL <kf7eel@qsl.net>
# https://github.com/kf7eel/HBNetMon
import flet as ft

import threading
import time
from datetime import datetime
import ast
import re

from local_db import local_db

from dmr_utils3.utils import get_alias, mk_id_dict, try_download

import random

from random_word import RandomWords

import yaml

import logging
##logging.basicConfig(level=logging.DEBUG)

config_file = open("config.yml", "r")
config = yaml.safe_load(config_file)

try_download('./',config['app']['dmr_db']['json_file'], config['app']['dmr_db']['json_url'], time.time() + config['app']['dmr_db']['stale_time'])

subscriber_ids = mk_id_dict('./', 'users.json')

whos_online = {}

class Dialog(ft.UserControl):
    def modal(self, message):
        dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Alert"),
        content=ft.Text(message),
        actions=[
            
        ],
        actions_alignment=ft.MainAxisAlignment.END)

        return dlg
    def banner(self, message):
        ban = ft.Banner(
        bgcolor=ft.colors.AMBER_100,
        leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
        content=ft.Container(ft.Markdown(
                message,
                extension_set="gitHubWeb",
            ),
##                    width=400,
##                    bgcolor="#f5f5f5",
        ##            border=border.all(2, "blue"),
        ##            border_radius=10,
                    padding=10,
                ),
            
        actions=[
        ],
    )
        return ban


class PageTemplate(ft.UserControl):
    def chat(self, hx):
        ui_list = []
        for i in hx:
            msg = i.split(':::')
##            ui_list.append(ft.Row(controls=[ft.Text(msg[0] + ' >> ',  weight=ft.FontWeight.BOLD, color=ft.colors.BLUE), ft.Text(msg[1])]))

            ui_list.append(

            ft.Container(ft.Markdown(
                '* **' + msg[0] + '** >> ' + msg[1],
                extension_set="gitHubWeb",
            ),
                    width=400,
##                    bgcolor="#f5f5f5",
        ##            border=border.all(2, "blue"),
        ##            border_radius=10,
                    padding=10,
                )
            )
##            ui_list.append(ft.Markdown(i, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB))           
        return ui_list

    def chat_online(self):
##        global whos_online
        ui_list = [ft.Text('Online:',  size=40)]
        for i in whos_online.items():
            ui_list.append(ft.Text(i[0] + ' [' + i[1]['page'] + ']',  weight=ft.FontWeight.BOLD, color=ft.colors.GREEN))
        return ui_list

    def view_page(self, page_name):
        try:
            md_text = open(config['pages'][page_name]['markdown_file'], "r").read()
            return md_text
        except Exception as e:
            print(e)
            return '# Not found or other error.'
        
        
        
    
class LiveData(ft.UserControl):

    lo_db = local_db()
    lo_db.init_db()
        
    
    def lastheard(self, records_length = 10, dmr_id = None, buttons = True):
       
        if dmr_id == None:
            log = self.lo_db.CallLog.query.order_by(self.lo_db.CallLog.id.desc()).limit(records_length)
        elif dmr_id != None:
            log = self.lo_db.CallLog.query.filter_by(source = dmr_id).order_by(self.lo_db.CallLog.id.desc()).limit(records_length)
        r_list = []
        for i in log:
##            print(i.source)
##            source_button = ft.FilledButton(str(get_alias(int(i.source), subscriber_ids)) + '\n' + str(i.source), on_click=lambda e: print(str(get_alias(int(i.source), subscriber_ids)) + '\n' + str(i.source))) #on_click=lambda e: view_call_log(e, i.source))
                            
##            if buttons == False:
##            source_button = ft.Text(str(get_alias(int(i.source), subscriber_ids)) + '\n' + i.source)

            source_button = ft.ElevatedButton(str(get_alias(int(i.source), subscriber_ids)), on_click=view_call_log, data=str(i.source), bgcolor = 'Blue', color = 'WHITE', tooltip = str(i.source))
            if buttons == False:
                source_button = ft.Text(str(get_alias(int(i.source), subscriber_ids)) + '\n' + i.source)
                
            r_list.append(ft.DataRow(
                    cells=[ft.DataCell(source_button),
                        ft.DataCell(ft.Text(i.destination + '\nTS: ' + str(i.slot))),
##                        ft.DataCell(ft.Text(str(i.slot))),
                        ft.DataCell(ft.Text(str(i.duration)))# + '\n' + str(i.call_type))),
##                        ft.DataCell(ft.Text(str(i.call_type))),
##                        ft.DataCell(ft.Text(str(i.stream_id))),
                        
                    ]))
        table = ft.DataTable(
##            width=700,
##            data_row_height = 100,
            heading_row_color=ft.colors.GREEN,
                    columns=[
                        ft.DataColumn(ft.Text("Source")),
                        ft.DataColumn(ft.Text("Destination")),
##                        ft.DataColumn(ft.Text("Slot")),
                        ft.DataColumn(ft.Text("Duration")),
##                        ft.DataColumn(ft.Text("Type")),
##                        ft.DataColumn(ft.Text("Stream ID")),
                    ])
        table.rows = r_list
        
        return ft.ResponsiveRow([table])
    
    def txNow(self):
        data = ft.DataTable(
                border=ft.border.all(2, "red"),
                width=700,
                heading_row_color=ft.colors.GREEN,

                
                    columns=[
                        ft.DataColumn(ft.Text("Source", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Destination", weight=ft.FontWeight.BOLD)),
##                        ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD)),
                    ])
        r_list = []
        txNow_db = self.lo_db.txNow.query.all()
        for i in txNow_db:
            r_list.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(get_alias(int(i.source), subscriber_ids)), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(i.destination)),
##                    ft.DataCell(ft.Text(str(datetime.utcnow() - i.start_time) + ' Seconds')),
                ]))
        data.rows = r_list
        return data
                
                
def main(page: ft.Page):
    global view_call_log, whos_online
    chat_hx = []
    chat_update = False
    live = LiveData()
    dlg = Dialog()
    pg_tmp = PageTemplate()
    current_time = ft.Text(str(time.time()))
    username = RandomWords().get_random_word() + ' ' + RandomWords().get_random_word()
    if page.client_storage.get("username") != None:
        username = page.client_storage.get("username")
        
    app_title = config['app']['title']
##    home_text = open(config['pages']['home']['markdown_file'], "r").read()

    # add/update controls on Page
    page.title = app_title
    

    
    page.update()

    def live_dash(e):
        page.go("/live")
##        page.pubsub.send_all_on_topic('alert', 'Server reboot in 5...')
    def home(e):
        page.go("/")
    def view_call_log(e):
        page.go("/log/" + e.control.data)
    def view_page(e):
##        print(e.data)
        print(e.control.data)
        page.go("/page/" + e.control.data)
##        print(e.data)

    def chat(e):
        page.go("/chat")
    def settings(e):
        page.go("/settings")

    def generate_page_menu():
        page_menu = []
        for i in config['pages']:
            if i != 'home':
                page_menu.append(ft.PopupMenuItem(text=config['pages'][i]['menu_title'], on_click=view_page, data=i))
        return page_menu
                
    page_menu = generate_page_menu()


    bottom_bar = ft.ResponsiveRow(
                                [ft.Divider(height=9, thickness=3),
                                 ft.Container(ft.Text("HBNetMon by KF7EEL (V. 12212022)", text_align = ft.TextAlign.CENTER),
                                padding=10,
##                                bgcolor=ft.colors.SURFACE_VARIANT,
                                col={"sm": 12, "md": 12, "xl": 12},
                                )])

    
    app_bar = ft.AppBar(
##            leading=ft.Icon(ft.icons.PALETTE),
            leading_width=40,
            title=ft.Text(app_title),
            center_title=False,
            bgcolor=config['app']['colors']['top_bar_color'],
            actions=[
                ft.IconButton(
                    icon=ft.icons.HOME,
                    icon_color=config['app']['colors']['icon_color'], #"blue400",
                    icon_size=40,
                    tooltip="Home",
                    on_click=home
                ),
                ft.IconButton(
                    icon=ft.icons.RADIO,
                    icon_color=config['app']['colors']['icon_color'],
                    icon_size=40,
                    tooltip="Live",
                    on_click=live_dash
                ),
                ft.IconButton(
                    icon=ft.icons.QUESTION_ANSWER,
                    icon_color=config['app']['colors']['icon_color'],
                    icon_size=40,
                    tooltip="Chat",
                    on_click=chat
                ),
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    icon_color=config['app']['colors']['icon_color'],
                    icon_size=40,
                    tooltip="Chat",
                    on_click=settings
                ),
##                ft.OutlinedButton(text="Home", on_click=home, icon='home', tooltip = 'Home screen'),
##                ft.FilledButton(text="Live", on_click=live_dash, icon='radio', tooltip = 'See who is transmitting...'),
##                ft.OutlinedButton(text="Chat", on_click=chat, icon='question_answer', tooltip = 'Home screen'),



                
                ft.PopupMenuButton(
                    items=page_menu, icon = ft.icons.MENU
                ),
            ],
        )
##    print()
##    print(app_bar.actions[4].items[1].data)
##    print('---')

    def route_change(e):

        m_route = ft.TemplateRoute(page.route)
        home_text = open(config['pages']['home']['markdown_file'], "r").read()
##        print(page.views)
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    app_bar,
                    ft.ResponsiveRow(
                                [ft.Container(
                                        ft.Markdown(
                                        home_text,
                                        extension_set="gitHubWeb",
                        ####                on_tap_link=lambda e: page.launch_url(e.data),
                                    ),
                                        padding=10,
                                        bgcolor=config['app']['colors']['home_color'],
                                        col={"sm": 12, "md": 10, "xl": 8},
##                                        width = 50,
                                    ),
                                    ft.Container(
                                        ft.Text("Lastheard", size=20, text_align = ft.TextAlign.CENTER),
                                        padding=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        col={"sm": 12, "md": 12, "xl": 12},
                                    ),
                                    ft.Container(
                                        live.lastheard(records_length = 5),
                                        padding=5,
##                                        bgcolor=ft.colors.GREEN,
                                        col={"sm": 12, "md": 12, "xl": 12},
                                    ),
                                ], alignment = ft.MainAxisAlignment.CENTER
                            ),
                    bottom_bar
    
                    
                ],
            )
        )
        if page.route == "/live":
            page.views.clear()
            page.views.append(
                ft.View(
                    "/live",
                    [
                        app_bar,
                        ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee"),
                        bottom_bar,
                    ],
                )
            )
        if page.route == "/chat":
            page.views.clear()
            def send_message(e):
                if message.value[:3] == '!!!':
                    page.pubsub.send_all_on_topic('alert', message.value[3:])
                else:
                    page.pubsub.send_all_on_topic('chat', username + '::: ' + message.value)
                message.value = ""
            message = ft.TextField(hint_text="Your message...", expand=True, on_submit=send_message)
            send = ft.ElevatedButton("Send", on_click=send_message)
            page.views.append(
                ft.View(
                    "/chat",
                    [
                        app_bar,
                        ft.ResponsiveRow(
                                [
                                    ft.Container(
                                        ft.Column(pg_tmp.chat_online(), width = 200),#, bgcolor=ft.colors.SURFACE_VARIANT, padding = 20),
                                        padding=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        col={"sm": 3, "md": 3, "xl": 3},
                                    ),
                                    ft.Container(
                                        ft.Column(controls = pg_tmp.chat(chat_hx), scroll = 'always', height = 300, auto_scroll = True),
                                        padding=5,
##                                        bgcolor=ft.colors.GREEN,
                                        col={"sm": 6, "md": 6, "xl": 6},
                                    ),
                                ], alignment = ft.MainAxisAlignment.CENTER
                            ),
                                                  
                        ft.ResponsiveRow(
                                [
                                    ft.Container(
                                        message,#, bgcolor=ft.colors.SURFACE_VARIANT, padding = 20),
##                                        padding=10,
##                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        col={"sm": 6, "md": 6, "xl": 6},
                                    ),
                                    ft.Container(
                                        send,
                                        padding=5,
##                                        bgcolor=ft.colors.GREEN,
                                        col={"sm": 3, "md": 3, "xl": 3},
                                    ),
                                ], alignment = ft.MainAxisAlignment.CENTER
                            ),#
##                        ft.Row(controls = [message, send]),
##                        ft.Divider(height=9, thickness=3),
                        bottom_bar
                        ]
                    )
                )
        if page.route == "/settings":
            def set_username(e):
                nonlocal username
                del whos_online[username]
                page.client_storage.set("username", username_field.value)
                username = username_field.value
                
            username_field = ft.TextField(hint_text=username, expand=True, on_submit=set_username)
            page.views.append(
            ft.View(
                "/settings",
                [app_bar,
                    ft.Row(controls=[ft.Text('Username: '), username_field]),
                 bottom_bar
                 ]))

            
        if m_route.match("/log/:dmr_id"):
            page.views.append(
            ft.View(
                "/log/" + m_route.dmr_id,
                [app_bar,
                    ft.Column([live.lastheard(records_length = 50, dmr_id = m_route.dmr_id, buttons = False)], scroll = ft.ScrollMode.ALWAYS),
                 bottom_bar
                 ]))
            
        if m_route.match("/page/:page_name"):
##            print(pg_tmp.view_page(m_route.page_name))
##            print()
            page.views.append(
            ft.View(
            "/page/" + m_route.page_name,
            [app_bar,
             ft.ResponsiveRow(
                            [ft.Container(
                                    ft.Markdown(
                                    pg_tmp.view_page(m_route.page_name),
                                    extension_set="gitHubWeb",
                    ####                on_tap_link=lambda e: page.launch_url(e.data),
                                ),
                                    padding=10,
##                                    bgcolor=config['app']['colors']['home_color'],
                                    col={"sm": 12, "md": 10, "xl": 8},
##                                        width = 50,
                                ),

                
             bottom_bar
             ], alignment = ft.MainAxisAlignment.CENTER)]))

                
        page.update()
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    page.on_route_change = route_change
    page.on_view_pop = view_pop


    def close_modal(e):
        dlg.open = False
        page.update()
    def close_banner(e):
        page.banner.open = False
        page.update()

    def on_message(topic, message):
        nonlocal chat_update
        if topic == 'alert':
            dlg_banner = dlg.banner(message)
            
            dlg_banner.actions = [ft.TextButton("Close", on_click=close_banner),]
            page.banner = dlg_banner
            page.banner.open = True
            page.update()
        elif topic == 'chat':
            chat_update = True
            chat_hx.append(message)
            if page.route != '/chat':
                msg = message.split(':::')
                page.snack_bar = ft.SnackBar(ft.Text(msg[0] + ' >> ' + msg[1][:20] + '...'), action_color = 'green', action = "Go to chat...", on_action=chat)
                page.snack_bar.open = True
                page.update()

    def time_loop():
##        run = True
        nonlocal chat_update
        
        while True:
            time.sleep(1)
            if exit_flag:
                print('Thread stopping due to client disconnect')
                break
            whos_online[username] = {'page' : page.route, 'time': time.time()} #, 'online': True}
            if page.route == '/live':
                try:
                    del page.views[0].controls[1:-1]
##                    del page.views[0].controls[2]
                except:
                    pass
                page.views[0].scroll = ft.ScrollMode.ALWAYS
                page.views[0].horizontal_alignment = "center"
                page.views[0].controls.insert(1, live.lastheard())
                page.views[0].controls.insert(1, live.txNow())
                page.update()
                
            if page.route == '/chat':
                if chat_update == True:
                
                    try:
                        del page.views[0].controls[1]
                    except:
                        pass
                    chat_text = pg_tmp.chat(chat_hx)
                    online = pg_tmp.chat_online()
##                    page.views[0].controls.insert(1, ft.Column(controls = chat_text, scroll = 'always', height = 500, width = 300, auto_scroll = True)) #, alignment = ft.MainAxisAlignment.CENTER))
##                    page.views[0].controls.insert(1, ft.Row(controls = [ft.Container(content = ft.Column(online, width = 200), bgcolor=ft.colors.SURFACE_VARIANT, padding = 20), ft.Column(controls = chat_text, scroll = 'always', height = 500, auto_scroll = True)], scroll = 'always', width = 600))
                    page.views[0].controls.insert(1,
                    ft.ResponsiveRow(
                                [
                                    ft.Container(
                                        ft.Column(online, width = 200),#, bgcolor=ft.colors.SURFACE_VARIANT, padding = 20),
                                        padding=10,
                                        bgcolor=ft.colors.SURFACE_VARIANT,
                                        col={"sm": 3, "md": 3, "xl": 3},
                                    ),
                                    ft.Container(
                                        ft.Column(controls = chat_text, scroll = 'always', height = 300, auto_scroll = True),
                                        padding=5,
##                                        bgcolor=ft.colors.GREEN,
                                        col={"sm": 6, "md": 6, "xl": 6},
                                    ),
                                ], alignment = ft.MainAxisAlignment.CENTER
                            )
                                                  )

                    page.update()
                    chat_update = False

                    
    exit_flag = False
    
    start_time_loop = threading.Thread(target = time_loop)
    start_time_loop.start()
    page.pubsub.subscribe_topic("alert", on_message)
    page.pubsub.subscribe_topic("chat", on_message)
    page.session.set('test', str(random.randint(99,1000)))

    def user_exit(e):
        nonlocal exit_flag
        print('User Disconnected')
        try:
            del whos_online[username]
        except Exception as e:
            print(e)
        exit_flag = True
        start_time_loop.join()

    page.on_disconnect = user_exit
    page.go(page.route)
    


ft.app(target=main, port=8081, host='0.0.0.0', view=ft.WEB_BROWSER)
