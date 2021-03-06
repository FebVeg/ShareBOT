print("ShareBOT - FebVeg")
print("Configurazione automatica in corso...")

SB_version = "2.3.8beta"
facebook_groups = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

from time import strftime
def printlog(log):
    now = strftime("[%H:%M:%S]")
    if log.startswith("[STARTED]"):
        print(bcolors.OKGREEN + now + " " + str(log) + bcolors.ENDC)
    elif log.startswith("[SECURITY]"):
        print(bcolors.OKBLUE + now + " " + str(log) + bcolors.ENDC)
    elif log.startswith("[DRIVER]"):
        print(bcolors.BOLD + now + " " + str(log) + bcolors.ENDC)
    elif log.startswith("[ERROR]"):
        print(bcolors.FAIL + now + " " + str(log) + bcolors.ENDC)
    elif log.startswith("[WARNING]"):
        print(bcolors.WARNING + now + " " + str(log) + bcolors.ENDC)
    else:
        print(now + " " + str(log))
    with open("sharebot.log", "a", encoding='UTF-8') as sb_logs:
        sb_logs.write(now + " " + str(log) + "\n")

try:
    printlog("Importazione delle librerie")
    from tkinter import *
    from tkinter.ttk import *
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    from tkinter import messagebox
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from os import path, name
    if name == "posix":
        from os import system, environ
    elif name == "nt":
        from os import startfile
    from random import randint, choice
    from time import sleep
    import psutil
    import re
    import pyperclip
    printlog("Librerie importate")
except Exception as lib_err:
    printlog("[ERROR] " + str(lib_err))

def istruzioni():
    printlog("[STARTED] Istruzioni")
    i = """Benvenuto in ShareBOT, programma che automatizza il processo di condivisione dei post su Facebook per tutti i volontari
In questa mini-guida verrà scritto passo-passo il corretto funzionamento\n
1.  Inserisci nel campo 'Autenticazione' le tue credenziali di Facebook e poi premi Login (Nessun dato verrà salvato o condiviso a terzi)
1a. Si aprirà il browser, lascia eseguire le operazioni al computer, non dovrai fare nulla.
1b. Le variabili che hanno come valore le tue credenziali verranno distrutte per proteggere la tua privacy
1c. Il Browser, ovvero il WebDriver verrà eseguito in modalità INCOGNITO, ossia non salverà nessun dato in locale
1d. Prima di effettuare qualsiasi operazione, effettua il Login\n
2.  Sarà possibile eseguire la funzione di Logout quando si vuole. Quando avrai finito di condividere l'appello, utilizza Logout e lascia che il Bot esegua le sue operazioni
2a. La funzione di Logout uscirà dal tuo account sfruttando le funzioni di Facebook per non salvare nessun dato alla chiusura del WebDriver.\n
3.  Nel campo 'Importa / Esporta lista gruppi' è possibile importare da 'Importa' una lista precedentemente esportata
3a. Se non hai una lista, effettua il Login ed infine usa il pulsante Esporta, verrà esportata ed importata automaticamente la lista dei tuoi gruppi di Facebook
3b  Puoi modificare i gruppi prima di inviare l'appello, usando il tasto 'Modifica' ed eliminando l'intera riga del gruppo a cui non vuoi condividere l'appello
3c. E' possibile condividere su TUTTI i gruppi anche senza usare Esporta. Per farlo, esegui il login, imposta il messaggio ed infine usa Condividi\n
4.  Nel campo 'Messaggio da condividere' dovrai scrivere il tuo appello\n
5.  Nel campo 'Azioni' ci saranno 4 pulsanti
5a. Il pulsante 'Condividi' serve per, una volta effettuato il login ed inseriti tutti i campi, avviare l'autocondivisione
5b. Il pulsante 'Istruzioni' farà apparire questa schermata di avviso
5c. Il pulsante 'Sviluppatore' aprirà il browser di default sulla pagina Github dello sviluppatore (Colui che ha programmato ShareBOT)
5d. Il pulsante 'Esci' è una funzione di chiusura logica del programma, effettua delle verifiche sul funzionamento del WebDriver per chiudere i processi figli di ShareBOT\n\n
IMPORTANTE: Durante le operazioni, non sarà possibile utilizzare il programma. Il programma lavorerà da solo, non serve chiuderlo solo perchè 'non risponde' o sembra bloccato"""
    istruzioni_window = tk.Tk()
    istruzioni_window.title('Istruzioni - Guida')
    istruzioni_window.resizable(False, False)
    Label(istruzioni_window, text=str(i)).grid(row=0, column=0, padx=5, pady=5)
    istruzioni_window.mainloop()

# Auto configurazione iniziale
try:
    printlog("Preparazione cartella di lavoro")
    if name == "nt":
        dirFile = path.dirname(path.abspath(__file__)) + "\\" # Default dir
    elif name == "posix":
        dirFile = path.dirname(path.abspath(__file__)) + "/" # Default dir
    printlog(f"Cartella di lavoro: {dirFile}")
except Exception as dirFile_err:
    printlog(f"[ERROR] {str(dirFile_err)}")

try:
    printlog("Verificando la presenza di Google Chrome")
    if name == "nt":
        if path.exists(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
            printlog("Google Chrome esistente")
            printlog("Controllando l'esistenza del WebDriver")

            if path.exists(dirFile + 'chromedriver.exe'):
                printlog("WebDriver trovato")
            else:
                printlog("[WARNING] WebDriver non trovato")
                printlog("Recupero versione di Google Chrome installata")

                def get_version_via_com(filename): # Thanks to temascal
                    printlog("Importazione libreria Dispatch da win32com.client")
                    from win32com.client import Dispatch
                    parser = Dispatch("Scripting.FileSystemObject")
                    try:
                        version = parser.GetFileVersion(filename)
                    except Exception:
                        return None
                    return version

                paths = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
                version = list(filter(None, [get_version_via_com(p) for p in paths]))[0]
                printlog("Versione di Chrome identificata: " + version)
                version = version[0:2]

                try:
                    import wget
                    chrome83 = "https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_win32.zip"
                    chrome84 = "https://chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_win32.zip"
                    chrome85 = "https://chromedriver.storage.googleapis.com/85.0.4183.38/chromedriver_win32.zip"

                    def unzip(arg):
                        printlog("Estrazione del WebDriver dal file compresso")
                        try:
                            import zipfile
                            with zipfile.ZipFile(arg, 'r') as zip_ref:
                                zip_ref.extractall(dirFile)
                            printlog("File estratto")
                        except Exception as zip_err:
                            printlog(f"[ERROR] Errore durante l'estrazione: {str(zip_err)}")
                            input("Premi INVIO per continuare")
                            exit()

                    def progress_bar(current, total, width=None):
                        print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total), end="\t\t\r")

                    if version == "83":
                        wget.download(chrome83, dirFile + 'chromedriver_win32.zip', bar=progress_bar)
                        unzip(dirFile + 'chromedriver_win32.zip')
                    elif version == "84":
                        wget.download(chrome84, dirFile + 'chromedriver_win32.zip', bar=progress_bar)
                        unzip(dirFile + 'chromedriver_win32.zip')
                    elif version == "85":
                        wget.download(chrome85, dirFile + 'chromedriver_win32.zip', bar=progress_bar)
                        unzip(dirFile + 'chromedriver_win32.zip')
                    else:
                        printlog("[ERROR] Versione di Chrome non scritta nel programma.")
                        printlog("Si prega di aggiornare Google Chrome ad una di queste seguenti versioni: 83, 84, 85")
                        input("Premi INVIO per continuare")
                        exit()

                    printlog("Rimozione del file compresso...")
                    try:
                        from os import remove
                        if path.exists(dirFile+"chromedriver_win32.zip"):
                            remove(dirFile+"chromedriver_win32.zip")
                            printlog("File compresso rimosso")
                        else:
                            printlog("[WARNING] File compresso non esistente")
                    except Exception as rem_zip:
                        printlog(f"[ERROR] {rem_zip}")
                        pass
                    printlog("[STARTED] Avvio di ShareBOT")
                except Exception as download_error:
                    printlog("Errore durante il downloading del WebDriver: " + str(download_error))
                    input("Premi INVIO per continuare")
                    exit()
        else:
            printlog("[ERROR] Google Chrome non trovato")
            printlog("[WARNING] Per far funzionare il programma, hai bisogno di installare Google Chrome")
            exit()

    elif name == "posix":
        if path.exists("/snap/bin/chromium.chromedriver"):
            printlog("Chromium WebDriver trovato, continuo")
            chromedriver = "/snap/bin/chromium.chromedriver"
            environ["WebDriver.chrome.driver"] = chromedriver
        else:
            printlog("[WARNING] WebDriver non trovato, installazione in corso...")
            system("sudo apt update; sudo apt install chromium* -y")
            printlog("Se non hai interrotto il processo, il WebDriver sarà stato installato")
except Exception as verify_chrome_err:
    printlog(f"[ERROR] {str(verify_chrome_err)}")

class Webdriver:
    def __init__(self, username, password):
        printlog("Classe: Variabili valorizzate")
        self.username = username
        self.password = password

    def login(self, driver, url, session_id, chrome_options):
        try:
            printlog("[STARTED] Login")
            driver = webdriver.Remote(command_executor=url, desired_capabilities={}, options=chrome_options)
            driver.close()
            driver.session_id = session_id
            printlog("[DRIVER] Sessione remota del WebDriver: " + session_id)
            printlog("[DRIVER] URL server locale di controllo: " + url)
            driver.get("https://mbasic.facebook.com/")
            if driver.find_element_by_name("email"):
                element = driver.find_element_by_name("email")
                element.send_keys(self.username)
                printlog("[DRIVER] Email inserita: " + self.username)
                if driver.find_element_by_name("pass"):
                    element = driver.find_element_by_name("pass")
                    element.send_keys(self.password)
                    printlog("[DRIVER] Password inserita")
                    pass
                else:
                    printlog("[ERROR][DRIVER] Campo password non trovato")
                    messagebox.showerror("Errore", "Campo PASSWORD non trovato")
                    exit()
            else:
                printlog("[ERROR][DRIVER] Campo email non trovato")
                messagebox.showerror("Errore", "Campo EMAIL non trovato")
                exit()             
            printlog("[SECURITY] Rimozione delle variabili 'email' e 'password' in corso...")
            try:
                del self.username 
                del self.password
                printlog("[SECURITY] Variabili rimosse, eseguo un secondo controllo...")

                # Controllo la variabile username
                if 'username' in dir(self):
                    if len(self.username) > 0:
                        printlog("[WARNING][SECURITY] Variabile 'username' NON rimossa con valore integro")
                    else:
                        printlog("[WARNING][SECURITY] Variabile 'username' NON rimossa ma senza valore")
                else:
                    printlog("[SECURITY] Variabile 'username' inesistente")
                    pass

                # Controllo la variabile password
                if 'password' in dir(self):
                    if len(self.password)> 0:
                        printlog("[WARNING] [SECURITY] Variabile 'password' NON rimossa con valore integro")
                    else:
                        printlog("[WARNING] [SECURITY] Variabile 'password' NON rimossa ma senza valore")
                else:
                    printlog("[SECURITY] Variabile 'password' inesistente")
                    pass

            except Exception as del_err:
                printlog("[WARNING][SECURITY] Non sono riuscito a rimuovere i valori delle variabili 'email' e 'password': " + str(del_err))
                pass
            else:
                printlog("[SECURITY] Variabili rimosse correttamente")
                pass
            printlog("[SECURITY] Rimozione del campo 'Password' dall'interfaccia grafica")
            try:
                password.delete(0, END) # Elimino la stringa della Entry
            except Exception as gui_delpass_err:
                printlog("[ERROR][SECURITY] Rimozione del campo 'Password' dall'interfaccia grafica NON riuscita: " + str(gui_delpass_err))
            else:
                printlog("[SECURITY] Rimozione del campo 'Password' dall'interfaccia grafica")
                pass
            
            driver.find_element_by_xpath('//*[@id="login_form"]/ul/li[3]/input').click()
            try:
                if driver.find_element_by_xpath('//*[@id="header"]/nav/a[1]'):
                    printlog("[DRIVER] Homepage rilevata. Login effettuato")
                    messagebox.showinfo("Info", 'Login effettuato')
            except:
                messagebox.showerror('WARNING', "Non sono riuscito a rilevare la homepage di Facebook, verifica se si è presentato un errore sul WebDriver o se Facebook ha bisogno di identificarti")
                printlog("[WARNING][DRIVER] HomePage non rilevata")
                pass
        except Exception as login_err:
            printlog("[ERROR][DRIVER] Funzione: 'login': " + str(login_err))
            messagebox.showerror("Errore nella funzione 'login'", str(login_err))
            pass
    
    def logout(self, driver, url, session_id, chrome_options):
        try:
            printlog("[STARTED] Logout")
            driver = webdriver.Remote(command_executor=url, desired_capabilities={}, options=chrome_options)
            driver.close()
            driver.session_id = session_id
            printlog("[DRIVER] Sessione remota del WebDriver: " + session_id)
            printlog("[DRIVER] URL server locale di controllo: " + url)
            printlog("[DRIVER] Ritorno alla homepage...")
            driver.get("https://mbasic.facebook.com/")
            sleep(5)
            driver.find_element_by_xpath('//*[@id="header"]/nav/a[10]').click()
            printlog("[DRIVER] Logout: passaggio 1/5")
            sleep(5)
            driver.find_element_by_xpath('//*[@id="mbasic_logout_button"]').click()
            printlog("[DRIVER] Logout: passaggio 2/5")
            sleep(5)
            driver.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/div/form[2]/input[3]').click()
            printlog("[DRIVER] Logout: passaggio 3/5")
            sleep(5)
            driver.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/div/div[2]/div[1]/table/tbody/tr/td[3]/a/div/img').click()
            printlog("[DRIVER] Logout: passaggio 4/5")
            sleep(5)
            driver.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/div[3]/div/form[1]/table/tbody/tr/td/header/h3[1]/input').click()
            printlog("[DRIVER] Logout: passaggio 5/5")
            sleep(5)
            # check
            printlog("[DRIVER] Controllando se la disconnessione ha avuto successo...")
            if driver.find_element_by_xpath('//*[@id="login_form"]/ul/li[3]/input'):
                printlog("[DRIVER] Logout riuscito")
                messagebox.showinfo('Info', 'Logout riuscito')
            else:
                printlog("[WARNING][DRIVER] Logout non riuscito")
                messagebox.showwarning('Warning', 'Logout non riuscito')
        except Exception as logout_err:
            printlog("[ERROR] Funzione: 'logout': " + str(logout_err))
            messagebox.showerror("Errore nella funzione 'logout'", str(logout_err))
            pass
    
    def cond_with_list(self, driver, url, session_id, lista, post, chrome_options):
        try:
            if driver_process.is_running():
                chrome_process = driver_process.children()
                if chrome_process:
                    chrome_process = chrome_process[0]
                    if chrome_process.is_running():
                        driver = webdriver.Remote(command_executor=url, desired_capabilities={}, options=chrome_options)
                        driver.close()
                        driver.session_id = session_id
                        printlog("[DRIVER] Condivisione sui gruppi della lista in corso")
                        printlog("[DRIVER] Preparazione della lista...")
                        group_lines = open(lista, encoding="utf-8").readlines()
                        for line in group_lines:
                            line = line.strip()
                            line = re.sub(r' \s.*$', '', line)
                            line = line.split(" ", 1)[0]
                            facebook_groups.append(line)
                        printlog("[DRIVER] Lista preparata. Avvio la condivisione su %s gruppi..." % (len(facebook_groups)))
                        printlog("[DRIVER] Per interrompere il processo: Premi CTRL+C in questa schermata")
                        for idx, val in enumerate(facebook_groups, 1):
                            try:
                                for i in range(randint(1, 60), 0, -1):
                                    print("[ANTISPAM] Attesa di", i, "secondi ", end='\r')
                                    sleep(1)
                                print("[DRIVER] Condivisione del post in corso...", end="\r")
                                if pyperclip.paste() == post:
                                    pass
                                else:
                                    pyperclip.copy(post)
                                    printlog("[DRIVER] Valore nella clipboard resettato su: " + post[0:10] + "...")
                                driver.get(val)
                                title = driver.title
                                sleep(randint(2, 4))
                                cond = driver.find_element_by_name("xc_message")
                                cond.click()
                                sleep(randint(2, 4))
                                cond.send_keys(Keys.CONTROL + "v")
                                sleep(randint(5, 8))
                                cond = driver.find_element_by_name("view_post")
                                sleep(randint(2, 4))
                                cond.click()
                                printlog("[DRIVER] %d/%s Post condiviso a: %s" % (idx, len(facebook_groups), title))
                            except Exception as err:
                                printlog("[WARNING][DRIVER] In questo gruppo '%s' non sembra sia possibile condividere il post: %s" % (title, err))
                                pass
                            except KeyboardInterrupt:
                                driver.quit()
                                printlog("[WARNING][DRIVER] Condivisione interrotta")
                                messagebox.showwarning('Warning', 'Condivisione interrotta')
                                return
                        printlog("[DRIVER] Resetto la lista gruppi in memoria...")
                        facebook_groups.clear()
                        printlog("[DRIVER] Condivisione completata")
                        messagebox.showinfo('Info', 'Condivisione completata')
                    else:
                        printlog("[WARNING][DRIVER] Il WebDriver non è in esecuzione")
                        messagebox.showwarning('Warning', 'Il WebDriver non è in esecuzione')
                        pass                          
                else:
                    printlog("[WARNING][DRIVER] Non ci sono processi figli del WebDriver")
                    messagebox.showwarning('Warning', 'Non ci sono processi figli del WebDriver')
                    pass
            else:
                printlog("[WARNING][DRIVER] Processo del WebDriver non in servizio")
                messagebox.showwarning('Warning', 'Processo del WebDriver non in servizio')
                pass
            
        except Exception as cond_with_list_err:
            driver.quit()
            printlog("[ERROR] Funzione 'cond_with_list': " + str(cond_with_list_err))
            messagebox.showerror("Errore nella funzione 'cond_with_list'", str(cond_with_list_err))

    def cond_without_list(self, driver, url, session_id, post, chrome_options):
        try:
            if driver_process.is_running():
                chrome_process = driver_process.children()
                if chrome_process:
                    chrome_process = chrome_process[0]
                    if chrome_process.is_running():
                        printlog("[DRIVER] Condivisione su tutti i gruppi di cui fai parte")
                        printlog("[DRIVER] Cerco i gruppi")
                        elems = driver.find_elements_by_tag_name("a")
                        if elems:
                            for elem in elems:
                                elem_clean = elem.get_attribute("href") # Raccolto in variabile solo gli href dell'html
                                if elem_clean.endswith("?refid=27"): # estraggo solo le stringhe che finiscono per ?refid=27
                                    facebook_groups.append(elem_clean) # appeno il gruppo all'array
                            printlog("[DRIVER] Gruppi importati nell'array: " + len(facebook_groups))
                            printlog("[DRIVER] Procedo con la condivisione")
                            printlog("[DRIVER] Per interrompere il processo: Premi CTRL+C in questa schermata")

                            for idx, val in enumerate(facebook_groups, 1):
                                try:
                                    for i in range(randint(1, 60), 0, -1):
                                        print("[ANTISPAM] Attesa di", i, "secondi ", end='\r')
                                        sleep(1)                        
                                    print("[DRIVER] Condivisione del post in corso...", end="\r")   
                                    if pyperclip.paste() == post:
                                        pass
                                    else:
                                        pyperclip.copy(post)
                                        printlog("[DRIVER] Valore nella clipboard resettato su: " + post[0:10] + "...")                             
                                    driver.get(val)
                                    title = driver.title
                                    pyperclip.copy(post)
                                    sleep(randint(2, 6))
                                    cond = driver.find_element_by_name("xc_message")
                                    cond.click()
                                    sleep(randint(2, 6))
                                    cond.send_keys(Keys.CONTROL + "v")
                                    sleep(randint(4, 8))
                                    driver.find_element_by_name("view_post").click()
                                    sleep(randint(2, 6))
                                    printlog("[DRIVER] %d/%s Post inviato a: %s" % (idx, len(facebook_groups), title))
                                except Exception as err:
                                    printlog("[WARNING][DRIVER] In questo gruppo '%s' non sembra possibile condividere il post: %s" % (title, err))
                                    pass
                                except KeyboardInterrupt:
                                    printlog("[WARNING][DRIVER] Condivisione interrotta")
                                    messagebox.showwarning('Warning', 'Condivisione interrotta')
                                    return
                            facebook_groups.clear()
                            printlog("[DRIVER] Condivisione completata")
                            messagebox.showinfo('Info', 'Condivisione completata')
                        else:
                            printlog("[WARNING][DRIVER] Gruppi non trovati")
                            messagebox.showinfo('Warning', 'Gruppi non trovati')

                    else:
                        printlog("[WARNING][DRIVER] Il WebDriver non è in esecuzione")
                        messagebox.showwarning('Warning', 'Il WebDriver non è in esecuzione')
                        pass                          
                else:
                    printlog("[WARNING][DRIVER] Non ci sono processi figli del WebDriver")
                    messagebox.showwarning('Warning', 'Non ci sono processi figli del WebDriver')
                    pass
            else:
                printlog("[WARNING][DRIVER] Processo del WebDriver non in servizio")
                messagebox.showwarning('Warning', 'Processo del WebDriver non in servizio')
                pass

        except Exception as cond_without_list_err:
            driver.quit()
            printlog("[ERROR][DRIVER] Funzione: 'cond_without_list': " + str(cond_without_list_err))
            messagebox.showerror("Errore nella funzione 'cond_without_list'", str(cond_without_list_err))

    def get_groups(self, driver, url, session_id, chrome_options):
        try:
            driver = webdriver.Remote(command_executor=url,desired_capabilities={}, options=chrome_options)
            driver.close()
            driver.session_id = session_id
            printlog("[DRIVER] Estrazione dei gruppi in corso...")
            driver.get("https://mbasic.facebook.com/groups/")
            sleep(randint(2, 4))
            driver.find_element_by_xpath("//span[contains(text(),'Mostra tutti')]").click()
            sleep(randint(2, 4))
            gp_list = "ListaGruppi.txt"
            printlog("[DRIVER] Cerco i gruppi...")
            elems = driver.find_elements_by_tag_name("a")
            if elems:
                for elem in elems:
                    elem_clean = elem.get_attribute("href") # Raccolto in variabile solo gli href dell'html
                    if elem_clean.endswith("?refid=27"): # estraggo solo le stringhe che finiscono per ?refid=27
                        name_clean = elem.get_attribute('text')
                        blob = elem_clean + " : " + name_clean
                        facebook_groups.append(blob) # appeno il gruppo all'array
                printlog("[DRIVER] Salvataggio di %s gruppi in corso..." % (len(facebook_groups)))
                dump = open(dirFile+gp_list, "w", encoding='utf-8')
                for x in facebook_groups:
                    dump.write(x + "\n")
                dump.close()
                printlog("[DRIVER] Gruppi salvati qui: " + dirFile + gp_list)
                facebook_groups.clear()
                messagebox.showinfo('Info', "Gruppi salvati qui: " + dirFile + gp_list)
                lista.insert(0, dirFile + gp_list)
            else:
                printlog("[WARNING][DRIVER] Gruppi non trovati")
                messagebox.showwarning('Warning', 'Gruppi non trovati')
        except Exception as get_groups_err:
            printlog("[ERROR][DRIVER] Funzione 'get_groups': " + str(get_groups_err))
            messagebox.showerror("Errore nella funzione 'get_groups'", str(get_groups_err))
# Termine della classe
# Inizio funzioni out of class
def user_login():
    if len(email.get()) > 0:
        if len(password.get()) > 0:
            global utente
            global chrome_options
            chrome_options = Options()
            chrome_options.add_argument("--incognito") # Abilito la incognito mode
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # Rimuovo lo status di logging
            chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2}) # Rimuovo JavaScript
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_experimental_option("prefs", { \
                "profile.default_content_setting_values.notifications": 2 # 1:allow, 2:block 
            })

            global driver
            if name == "nt":
                driver = webdriver.Chrome(executable_path=dirFile + 'chromedriver.exe', options=chrome_options)
            elif name == "posix":
                driver = webdriver.Chrome(executable_path=chromedriver, options=chrome_options)
            
            driver.set_window_size(500,500)
            driver.minimize_window()
            global url, session_id, driver_process
            url = driver.command_executor._url
            session_id = driver.session_id 
            driver_process = psutil.Process(driver.service.process.pid)
            printlog("[DRIVER] WebDriver process: " + str(driver_process))
            printlog("[DRIVER] WebDriver session id: " + session_id)
            printlog("Il WebDriver è nella modalità 'incognito/privata' quindi non verrà salvato nessun dato in locale")
            utente = Webdriver(email.get(), password.get())
            utente.login(driver, url, session_id, chrome_options)
            pass
        else:
            printlog("[WARNING] Campo password vuoto")
            messagebox.showwarning("Warning", "Campo PASSWORD vuoto")
            pass
    else:
        printlog("[WARNING] Campo email vuoto")
        messagebox.showwarning("Warning", "Campo EMAIL vuoto")
        pass

def user_logout():
    try:         
        if driver_process.is_running():
            printlog("[DRIVER] Controllo se il WebDriver è attivo per eseguire il logout")
            chrome_process = driver_process.children()
            if chrome_process:
                chrome_process = chrome_process[0]
                if chrome_process.is_running():
                    utente.logout(driver, url, session_id, chrome_options)
                    pass
                else:
                    printlog("[WARNING] Non posso eseguire il logout se il WebDriver non è attivo, esegui il LOGIN e riprova")
                    messagebox.showwarning('Warning', 'Non posso eseguire il logout se il WebDriver non è attivo, esegui il LOGIN e riprova')
                    pass
            else:
                printlog("[WARNING] Non ci sono processi figli del WebDriver, esegui il Login e riprova")
                messagebox.showwarning('Warning', 'Non ci sono processi figli del WebDriver, esegui il Login e riprova')
                pass
        else:
            printlog("[WARNING] WebDriver non in funzione")
            messagebox.showwarning('Warning', 'WebDriver non in funzione')
            pass
    except Exception as user_logout_error:
        if str(user_logout_error) == "name 'driver_process' is not defined":
            printlog("[WARNING] Processo del WebDriver non valorizzato, effettua prima il Login")
            messagebox.showerror('Error', "Processo del WebDriver non valorizzato, effettua prima il Login")
            pass
        else:
            printlog("[ERROR] Funzione 'Logout': " + str(user_logout_error))
            messagebox.showerror("Problema nella funzione 'Logout'", str(user_logout_error))
            pass

def lista_import():
    try:
        ilist = askopenfilename(initialdir=dirFile, filetypes =(("File di test", "*.txt"),("All Files", "*.*")), title = "Importa la lista gruppi")
        lista.delete(0, END)
        lista.insert(0, ilist)
        pass
    except Exception as lista_import_err:
        printlog("[ERROR] Funzione 'lista_import': " + str(lista_import_err))
        messagebox.showerror("Errore nella funzione 'lista_import'", str(lista_import_err))
        pass

def lista_export():
    try:
        if driver_process.is_running():
            printlog("Controllo se il WebDriver è attivo per eseguire il logout")
            chrome_process = driver_process.children()
            if chrome_process:
                chrome_process = chrome_process[0]
                if chrome_process.is_running():
                    utente.get_groups(driver, url, session_id, chrome_options)
                    pass
                else:
                    printlog("[WARNING] Non posso eseguire il logout se il WebDriver non è attivo, esegui il LOGIN e riprova")
                    messagebox.showwarning('Warning', 'Non posso eseguire il logout se il WebDriver non è attivo, esegui il LOGIN e riprova')
                    pass
            else:
                printlog("[WARNING] Non ci sono processi figli del WebDriver, esegui il Login e riprova")
                messagebox.showwarning('Warning', 'Non ci sono processi figli del WebDriver, esegui il Login e riprova')
                pass
        else:
            printlog("[WARNING] WebDriver non in funzione")
            messagebox.showwarning('Warning', 'WebDriver non in funzione')
            pass
    except Exception as lista_export_err:
        if str(lista_export_err) == "name 'utente' is not defined":
            printlog("Effettua prima il Login")
            messagebox.showwarning('Warning', 'Effettua prima il Login')
            pass
        elif str(lista_export_err) == "name 'driver_process' is not defined":
            printlog('[WARNING] Processo del WebDriver non valorizzato, effettua prima il Login')
            messagebox.showwarning('Warning', 'Processo del WebDriver non valorizzato, effettua prima il Login')
            pass
        else:
            printlog("[ERROR] Funzione 'lista_export': " + str(lista_export_err))
            messagebox.showerror("Errore nella funzione 'lista_export'", str(lista_export_err))
            pass

def user_share():
    try:
        if len(lista.get()) > 1:
            if path.exists(lista.get()):
                utente.cond_with_list(driver, url, session_id, lista.get(), post.get("1.0","end-1c"), chrome_options)
                pass
            else:
                printlog("[WARNING] La lista sembra non essere accessibile o forse è danneggiata")
                messagebox.showerror('Errore', 'La lista sembra non essere accessibile o forse è danneggiata')
                pass
        else:
            utente.cond_without_list(driver, url, session_id, post.get("1.0","end-1c"), chrome_options)
            pass
    except Exception as user_share_err:
        if str(user_share_err) == "name 'utente' is not defined":
            printlog("Effettua prima il Login")
            messagebox.showwarning('Warning', 'Effettua prima il Login')
            pass
        elif str(user_share_err) == "name 'driver_process' is not defined":
            printlog("[WARNING] Processo del WebDriver non valorizzato, effettua prima il Login")
            messagebox.showerror('Error', "Processo del WebDriver non valorizzato, effettua prima il Login")
            pass
        else:
            printlog("[ERROR] Funzione 'user_share': " + str(user_share_err))
            messagebox.showerror("Errore nella funzione 'user_share'", str(user_share_err))
            pass

def lista_edit():
    printlog("[STARTED] Modifica lista gruppi")
    if path.exists(dirFile + "ListaGruppi.txt"):
        if name == "nt":
            printlog("Apertura della lista gruppi")
            startfile(dirFile + "ListaGruppi.txt")
        elif name == "posix":
            printlog("Apertura della lista gruppi")
            system("xdg-open %s" % (dirFile + "/ListaGruppi.txt"))
    else:
        printlog("[WARNING] Lista gruppi non trovata")
        messagebox.showwarning('Warning', 'Lista gruppi non trovata')
        pass

def sviluppatore():
    printlog("[STARTED] Apertura di https://github.com/FebVeg/ShareBOT/ in corso...")
    if name == "nt":
        startfile("https://github.com/FebVeg/ShareBOT")
    elif name == "posix":
        system("xdg-open https://github.com/FebVeg/ShareBOT")

def user_exit():
    printlog("[STARTED] Chiusura di ShareBOT")
    try:         
        if driver_process.is_running():
            chrome_process = driver_process.children()
            if chrome_process:
                chrome_process = chrome_process[0]
                if chrome_process.is_running():
                    # Il WebDriver è attivo, chiudo il programma
                    driver.quit()
                    master.destroy()
                    exit()
                else:
                    # Il WebDriver non è attivo, eseguo la kill del processo
                    chrome_process.kill()
                    master.destroy()
                    exit()
            else:
                # Non ci sono processi figli del WebDriver
                master.destroy()
                exit()
        else:
            # WebDriver non in funzione
            master.destroy()
            exit()
    except Exception as user_exit_err:
        if str(user_exit_err) == "name 'driver_process' is not defined":
            master.destroy()
            exit()
        else:
            printlog("[ERROR] Funzione 'user_exit': " + str(user_exit_err))
            master.destroy()
            exit()

printlog("Avvio interfaccia grafica...")
master = tk.Tk()
master.title("ShareBOT by FebVeg - Version: %s" % (SB_version))
master.resizable(True, True)
master.grid_columnconfigure(1, weight=1)
master.grid_rowconfigure(2, weight=1)

# Frame di autenticazione
frame_auth = LabelFrame(master, text="Autenticazione")
frame_auth.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="WENS")
frame_auth.columnconfigure(1, weight=1)

# Campo Email
Label(frame_auth, text="Email").grid(row=0, column=0, sticky="W", padx=5)
email = Entry(frame_auth)
email.grid(row=0, column=1, pady=5, padx=5, sticky="WENS")
# Campo Password
Label(frame_auth, text="Password").grid(row=1, column=0, sticky="W", padx=5)
password = Entry(frame_auth, show="*")
password.grid(row=1, column=1, pady=5, padx=5, sticky="WENS")
# Pulsanti Login e Logout
Button(frame_auth, text='Login', command=user_login).grid(row=2, column=0, sticky="W", padx=5, pady=5)
Button(frame_auth, text='Logout',command=user_logout).grid(row=2, column=1, sticky="E", padx=5, pady=5)

# Frame della lista gruppi
frame_lista = LabelFrame(master, text="Importa / Esporta lista gruppi")
frame_lista.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="WENS")
frame_lista.columnconfigure(1, weight=1)

# Campi esporta importa lista gruppi
Label(frame_lista, text="Lista").grid(row=0, column=0, sticky="W", padx=5)
lista = Entry(frame_lista)
lista.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="WENS")
Button(frame_lista, text='Importa', command=lista_import).grid(row=1, column=0, sticky="E", padx=5, pady=5)
Button(frame_lista, text='Esporta', command=lista_export).grid(row=1, column=1, sticky="E", padx=5, pady=5)
Button(frame_lista, text='Modifica', command=lista_edit).grid(row=1, column=2, sticky="E", padx=5, pady=5)

# Frame post
frame_post = LabelFrame(master, text="Messaggio da condividere")
frame_post.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="WENS")
frame_post.columnconfigure(0, weight=1)
frame_post.rowconfigure(0, weight=1)

# campo post
post = Text(frame_post, width=20, height=8)
post.grid(row=0, column=0, sticky="WENS", pady=5, padx=5)
scrollbar = Scrollbar(frame_post)
scrollbar.grid(row=0, column=0, sticky="ENS")
# attaccatura della scrollbar sulla textbox
post.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=post.yview)

# Frame pulsanti
frame_buttons = LabelFrame(master, text="Azioni")
frame_buttons.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="WENS")

Button(frame_buttons, text="Condividi", command=user_share).grid(row=0, column=0, padx=5, pady=5, sticky="WENS")
Button(frame_buttons, text="Istruzioni", command=istruzioni).grid(row=0, column=1, padx=5, pady=5, sticky="WENS")
Button(frame_buttons, text="Sviluppatore", command=sviluppatore).grid(row=0, column=2, padx=5, pady=5, sticky="WENS")
Button(frame_buttons, text="Esci", command=user_exit).grid(row=0, column=3, padx=5, pady=5, sticky="WENS")

master.mainloop()