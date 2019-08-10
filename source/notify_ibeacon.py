#!/usr/bin/python
# -*- coding: utf-8 -*-

MAMORIO_UUID = "b9407f30-f5f8-466e-aff925556b57fe6e"

# target [0]name,[1]major,[2]minor,[3]linetoken
MAMORIO_TARGETS = {
        ("check",11111,22222,""),
        ("gebo", 33333,44444,"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"),
        ("test", 55555,66666,"yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        }

import dbus
import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import bluezutils
import struct   
from datetime import datetime
import requests

devices = {}
targets = {}

# LINE通知する
def send_notify(access_token,username,comment):
        if( len(access_token) <= 0 ):
                return

        url = "https://notify-api.line.me/api/notify"
        headers = {'Authorization': 'Bearer ' + access_token}
        message = username + " が " + comment
        payload = {'message': message}
        print(message)
        #requests.post(url, headers=headers, params=payload,)

# targetが60秒更新されていなければ削除する
def delete_targets():
        datenow = datetime.now()
        delete_username =""
        for key, value in targets.iteritems():
                span = datenow - value
                #print(span)
                if(span.seconds>60):
                        delete_username=key
                        break

        if( len(delete_username)>0):                        
                targets.pop(delete_username)
                print("delete %s - span = %s " % (delete_username,span))

        return delete_username

# targetsリストに追加または更新する
# 戻り値true/false(新規追加はtrue)
def update_targets(username):
        datenow = datetime.now()
        if username in targets:
                targets[username] = datenow
                return False
        else:
                targets[username] = datenow
                return True

# ManufacturerDataデータをパースする
def parse_manufacture(mdata):
        uuid = ""
        major = 0
        minor = 0
        if( type(mdata) is dbus.Array and len(mdata) > 21):
                # UUID
                for item in mdata[2:6]:
                        uuid = uuid + format(item,'02x')
                uuid = uuid + "-"
                for item in mdata[6:8]:
                        uuid = uuid + format(item,'02x')
                uuid = uuid + "-"
                for item in mdata[8:10]:
                        uuid = uuid + format(item,'02x')
                uuid = uuid + "-"
                for item in mdata[10:18]:
                        uuid = uuid + format(item,'02x')

                # Major
                # - unsingned int(2バイト)
                # - リトルエンディアン
                majortmp = bytearray([int(mdata[19]),int(mdata[18])])
                major = struct.unpack('H',majortmp)[0]

                # Minor
                # - unsingned int(2バイト)
                # - リトルエンディアン
                minortmp = bytearray([int(mdata[21]),int(mdata[20])])
                minor = struct.unpack('H',minortmp)[0]
        return uuid,major,minor

# iBeaconをスキャンしたときの処理
def scan_ibeacon(properties):
        name = "unknown"
        address = "<unknown>"
        manufac = 0

        for key, value in properties.iteritems():
                if type(value) is dbus.String:
                        value = unicode(value).encode('ascii', 'replace')
                if (key == "Name"):
                        name = value
                if (key == "Address"):
                        address = value
                if (key == "ManufacturerData"):
                        manufac = value

        # print("%s (%s)" % (address, name))

        if type(manufac) is dbus.Dictionary:
                uuid = ""
                major = 0
                minor = 0
                for mdata in manufac.values():
                        uuid,major,minor = parse_manufacture(mdata)

                if( uuid.lower() == MAMORIO_UUID.lower()):
                        #print("    MAMORIO! - uuid = %s" % uuid)
                        #print("    - major = %d , minor = %d" % (major,minor))

                        # ターゲットを検索
                        username = ""
                        token = ""
                        founds = [i for i in MAMORIO_TARGETS if i[1]==major and i[2]==minor]
                        if(len(founds) <= 0):
                                return
                        username = founds[0][0]
                        token = founds[0][3]

                        print("%s - major = %d , minor = %d -> user = %s" % (datetime.now(),major,minor,username))
                        if( username == "check"):
                                notify_user = delete_targets()
                                if( len(notify_user)>0):
                                        founds = [i for i in MAMORIO_TARGETS if i[0]==notify_user]
                                        if(len(founds) > 0):
                                                send_notify(founds[0][3],notify_user,"どっかいった！")
                        else:
                                if( update_targets(username) == True):
                                        send_notify(token,username,"きた！")

def interfaces_added(path, interfaces):
        properties = interfaces["org.bluez.Device1"]

        if not properties:
                return

        if path in devices:
                devices[path] = dict(devices[path].items() + properties.items())
        else:
                devices[path] = properties

        scan_ibeacon(devices[path])

def properties_changed(interface, changed, invalidated, path):
        if interface != "org.bluez.Device1":
                return

        if path in devices:
                devices[path] = dict(devices[path].items() + changed.items())
        else:
                devices[path] = changed

        scan_ibeacon(devices[path])

if __name__ == '__main__':
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()
        adapter = bluezutils.find_adapter()


        bus.add_signal_receiver(interfaces_added,
                        dbus_interface = "org.freedesktop.DBus.ObjectManager",
                        signal_name = "InterfacesAdded")

        bus.add_signal_receiver(properties_changed,
                        dbus_interface = "org.freedesktop.DBus.Properties",
                        signal_name = "PropertiesChanged",
                        arg0 = "org.bluez.Device1",
                        path_keyword = "path")

        om = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = om.GetManagedObjects()

        for path, interfaces in objects.iteritems():
                if "org.bluez.Device1" in interfaces:
                        devices[path] = interfaces["org.bluez.Device1"]

        scan_filter = dict()
        scan_filter.update({ "Transport": "le" })
        adapter.SetDiscoveryFilter(scan_filter)
        adapter.StartDiscovery()

        mainloop = GObject.MainLoop()
        mainloop.run()

