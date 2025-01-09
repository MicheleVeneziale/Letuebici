import tkinter as tk  #per l'interfaccia grafica 
from tkinter import ttk     
from tkinter import messagebox #per i messaggi di avviso  
from PIL import Image, ImageTk
import sqlite3  #per il db
from datetime import datetime #per le date
import matplotlib.pyplot as plt #per i grafici plot
import statistics
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import subprocess #per eventualmente passare ad altri script python esterni
import os #per controllare se il file excel è aperto
import mplcursors #libreria per gestire cursore interattivo che interagisce coi punti del grafico matplot


def fetch_data(nome_bici):
    conn = sqlite3.connect('biciclette.db')
    cursor = conn.cursor()
    # Query per ottenere i dati
    if nome_bici != 'Tutte':  # Se `nome_bici` non è vuoto, esegue la query con filtro
        query = """
        SELECT 
            biciclette.km_ult_tragitto AS "CONTA KM PARZIALE",
            biciclette.km_acc AS "ODOMETRO KM",
            biciclette.data AS "DATA",
            aggiornamenti_km.dest AS "DESTINAZIONE"
        FROM 
            biciclette
        LEFT JOIN 
            aggiornamenti_km ON biciclette.data = aggiornamenti_km.data
        WHERE 
            biciclette.km_ult_tragitto > 0
        AND biciclette.nome_bici = ?
        ORDER BY 
            biciclette.id;
        """
        cursor.execute(query, (nome_bici,))
    else:  # Altrimenti, esegue la query senza filtro
        query = """
        SELECT 
            biciclette.km_ult_tragitto AS "CONTA KM PARZIALE",
            biciclette.km_acc AS "ODOMETRO KM",
            biciclette.data AS "DATA",
            aggiornamenti_km.dest AS "DESTINAZIONE"
        FROM 
            biciclette
        LEFT JOIN 
            aggiornamenti_km ON biciclette.data = aggiornamenti_km.data
        WHERE 
            biciclette.km_ult_tragitto > 0
        ORDER BY 
            biciclette.id;
        """
        cursor.execute(query)
    
    data = cursor.fetchall()
    conn.close()
    return data


def display_data(data):
    # Creazione della finestra principale
    root = tk.Tk()
    root.title("Report Km Biciclette")
    # Creazione di una cornice con sfondo celeste per l'aspetto da report
    frame = tk.Frame(root, bg='light blue')
    frame.pack(fill=tk.BOTH, expand=True)

        # Creazione di una Treeview per visualizzare i dati in formato tabellare
    columns = ("CONTA KM PARZIALE", "ODOMETRO KM", "DATA", "DESTINAZIONE") 
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

    # Definizione delle intestazioni di colonna con font grassetto e centrato
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), foreground='black')
    style.configure("Treeview", background="light blue", fieldbackground="light blue")
    style.map("Treeview", background=[('selected', 'sky blue')])

    # Definizione dei colori alternati per le righe della tabella
    tree.tag_configure('odd', background="light cyan")
    tree.tag_configure('even', background="azure")
    
     # Configurazione delle colonne
    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, anchor="center", width=150)

        # Posizionamento della Treeview
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    
    # Rimuove eventuali dati esistenti
    for row in tree.get_children():
        tree.delete(row)
        
    # Aggiunge i nuovi dati alla Treeview
    #data = fetch_data(nome_bici)
    for i, row in enumerate(data):
        # Righe alternate con colore
        if i % 2 == 0:
            tree.insert("", tk.END, values=row, tags=('even',))
        else:
            tree.insert("", tk.END, values=row, tags=('odd',))
    
    def reportistica_excel():
        #df = pd.DataFrame(data, columns=["CONTA KM PARZIALE", "ODOMETRO KM", "DATA", "DESTINAZIONE"])
        # Salvataggio del risultato in un file Excel
        excel_file = "report_km_biciclette.xlsx"
        # Controlla se il file è già aperto
        if os.path.exists(excel_file):
            try:
                # Prova a sovrascrivere il file
                df = pd.DataFrame(data, columns=["CONTA KM PARZIALE", "ODOMETRO KM", "DATA", "DESTINAZIONE"])
                df.to_excel(excel_file, index=False)
                messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}")
            except PermissionError:
                # Se il file è aperto, informa l'utente
                messagebox.showwarning("Attenzione Biagio", f"Prima di fare una nuova esportazione chiudi il file '{excel_file}' già aperto precedentemente.")
                return  # Esci dalla funzione se il file è aperto
        else:
            # Se il file non esiste, crealo
            df = pd.DataFrame(data, columns=["CONTA KM PARZIALE", "ODOMETRO KM", "DATA", "DESTINAZIONE"])
            df.to_excel(excel_file, index=False)
            messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}, ora puoi salvarlo con nome e stamparlo")
        
        
        
        
        
        #df.to_excel(excel_file, index=False)
        # Caricamento del file Excel con openpyxl per adattare larghezza delle colonne e aggiungere stile tabella
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            worksheet = workbook.active

            # Adatta larghezza delle colonne in base alla lunghezza del testo
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter  # Ottieni la lettera della colonna
                for cell in col:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = (max_length + 8)  # Aggiungi un po' di margine
                worksheet.column_dimensions[column].width = adjusted_width

                # Creazione della tabella con stile
            table_ref = f"A1:D{len(df) + 1}"  # Riferimento per l'area della tabella
            table = Table(displayName="ReportTable", ref=table_ref)

                # Imposta lo stile della tabella
            style = TableStyleInfo(
                name="TableStyleMedium9",  # Uno stile predefinito
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=True
            )
            table.tableStyleInfo = style
        worksheet.add_table(table)
    # Pulsante per esportare il report in Excel
    btn_export = tk.Button(root, text="Esporta in Excel", command=reportistica_excel)
    btn_export.pack(pady=5)


def fetch_data_manutenzione(nome_bici, cat_manut): 
    conn = sqlite3.connect('biciclette.db')
    cursor = conn.cursor()
    
    # Gestione dei casi
    if nome_bici != "Tutte" and cat_manut != "Tutte":  # Caso 1: Entrambi specifici
        query = """
        SELECT 
            sostituzione.nome_bici AS [NOME BICI],
            sostituzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            sostituzione.descrizione AS DESCRIZIONE,
            sostituzione.durata_km AS [DURATA (KM)]
        FROM 
            sostituzione
        WHERE 
            sostituzione.nome_bici = ?
            AND sostituzione.cat_manut = ?
        ORDER BY 
            sostituzione.id;
        """
        cursor.execute(query, (nome_bici, cat_manut))

    elif nome_bici != "Tutte" and cat_manut == "Tutte":  # Caso 2: nome_bici specifico, cat_manut generico
        query = """
        SELECT 
            sostituzione.nome_bici AS [NOME BICI],
            sostituzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            sostituzione.descrizione AS DESCRIZIONE,
            sostituzione.durata_km AS [DURATA (KM)]
        FROM 
            sostituzione
        WHERE 
            sostituzione.nome_bici = ?
        ORDER BY 
            sostituzione.id;
        """
        cursor.execute(query, (nome_bici,))

    elif nome_bici == "Tutte" and cat_manut != "Tutte":  # Caso 3: nome_bici generico, cat_manut specifico
        query = """
        SELECT 
            sostituzione.nome_bici AS [NOME BICI],
            sostituzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            sostituzione.descrizione AS DESCRIZIONE,
            sostituzione.durata_km AS [DURATA (KM)]
        FROM 
            sostituzione
        WHERE 
            sostituzione.cat_manut = ?
        ORDER BY 
            sostituzione.id;
        """
        cursor.execute(query, (cat_manut,))

    else:  # Caso 4: Entrambi generici (nome_bici = "Tutti" e cat_manut = "Tutte")
        query = """
        SELECT 
            sostituzione.nome_bici AS [NOME BICI],
            sostituzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            sostituzione.descrizione AS DESCRIZIONE,
            sostituzione.durata_km AS [DURATA (KM)]
        FROM 
            sostituzione
        ORDER BY 
            sostituzione.id;
        """
        cursor.execute(query)

    # Esecuzione della query
    data_manutenzione = cursor.fetchall()
    conn.close()
    return data_manutenzione

    
def display_data_manutenzione(data_manutenzione):
    # Creazione della finestra principale
    root = tk.Tk()
    root.title("Report Sostituzioni")
    # Creazione di una cornice con sfondo celeste per l'aspetto da report
    frame = tk.Frame(root, bg='light blue')
    frame.pack(fill=tk.BOTH, expand=True)

        # Creazione di una Treeview per visualizzare i dati in formato tabellare
    columns = ("NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DURATA in KM") 
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

    # Definizione delle intestazioni di colonna con font grassetto e centrato
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), foreground='black')
    style.configure("Treeview", background="light blue", fieldbackground="light blue")
    style.map("Treeview", background=[('selected', 'sky blue')])

    # Definizione dei colori alternati per le righe della tabella
    tree.tag_configure('odd', background="light cyan")
    tree.tag_configure('even', background="azure")
    
     # Configurazione delle colonne
    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, anchor="center", width=150)

        # Posizionamento della Treeview
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    
    # Rimuove eventuali dati esistenti
    for row in tree.get_children():
        tree.delete(row)
        
    # Aggiunge i nuovi dati alla Treeview
    #data = fetch_data(nome_bici)
    for i, row in enumerate(data_manutenzione):
        # Righe alternate con colore
        if i % 2 == 0:
            tree.insert("", tk.END, values=row, tags=('even',))
        else:
            tree.insert("", tk.END, values=row, tags=('odd',))
    
    def reportistica_excel_manutenzione():
        excel_file = "report_sostituzioni.xlsx"
        # Controlla se il file è già aperto
        if os.path.exists(excel_file):
            try:
                # Prova a sovrascrivere il file
                df = pd.DataFrame(data_manutenzione, columns=["NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DURATA in KM"])
                df.to_excel(excel_file, index=False)
                messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}")
            except PermissionError:
                # Se il file è aperto, informa l'utente
                messagebox.showwarning("Attenzione Biagio", f"Prima di fare una nuova esportazione chiudi il file '{excel_file}' già aperto precedentemente.")
                return  # Esci dalla funzione se il file è aperto
        else:
            # Se il file non esiste, crealo
            df = pd.DataFrame(data_manutenzione, columns=["NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DURATA in KM"])
            df.to_excel(excel_file, index=False)
            messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}, ora puoi salvarlo con nome e stamparlo")
        
        
        
        
        
        #df.to_excel(excel_file, index=False)
        # Caricamento del file Excel con openpyxl per adattare larghezza delle colonne e aggiungere stile tabella
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            worksheet = workbook.active

            # Adatta larghezza delle colonne in base alla lunghezza del testo
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter  # Ottieni la lettera della colonna
                for cell in col:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = (max_length + 8)  # Aggiungi un po' di margine
                worksheet.column_dimensions[column].width = adjusted_width

                # Creazione della tabella con stile
            table_ref = f"A1:D{len(df) + 1}"  # Riferimento per l'area della tabella
            table = Table(displayName="ReportTable", ref=table_ref)

                # Imposta lo stile della tabella
            style = TableStyleInfo(
                name="TableStyleMedium9",  # Uno stile predefinito
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=True
            )
            table.tableStyleInfo = style
        worksheet.add_table(table)
    # Pulsante per esportare il report in Excel
    btn_export = tk.Button(root, text="Esporta in Excel", command=reportistica_excel_manutenzione)
    btn_export.pack(pady=5)


def fetch_data_manutenzione_2(nome_bici,cat_manut):
    conn = sqlite3.connect('biciclette.db')
    cursor = conn.cursor()
    
    # Gestione dei casi
    if nome_bici != "Tutte" and cat_manut != "Tutte":  # Caso 1: Entrambi specifici
        query = """
        SELECT 
            manutenzione.nome_bici AS [NOME BICI],
            manutenzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            manutenzione.descrizione AS DESCRIZIONE,
            manutenzione.data_manut AS [DATA],
            manutenzione.segna_km AS [KM DELLA MANUTENZIONE]
        FROM 
            manutenzione
        WHERE 
            manutenzione.nome_bici = ?
            AND manutenzione.cat_manut = ?
        ORDER BY 
            manutenzione.id;
        """
        cursor.execute(query, (nome_bici, cat_manut))

    elif nome_bici != "Tutte" and cat_manut == "Tutte":  # Caso 2: nome_bici specifico, cat_manut generico
        query = """
        SELECT 
            manutenzione.nome_bici AS [NOME BICI],
            manutenzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            manutenzione.descrizione AS DESCRIZIONE,
            manutenzione.data_manut AS [DATA],
            manutenzione.segna_km AS [KM DELLA MANUTENZIONE]
        FROM 
            manutenzione
        WHERE 
            manutenzione.nome_bici = ?
        ORDER BY 
            manutenzione.id;
        """
        cursor.execute(query, (nome_bici,))

    elif nome_bici == "Tutte" and cat_manut != "Tutte":  # Caso 3: nome_bici generico, cat_manut specifico
        query = """
        SELECT 
            manutenzione.nome_bici AS [NOME BICI],
            manutenzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            manutenzione.descrizione AS DESCRIZIONE,
            manutenzione.data_manut AS [DATA],
            manutenzione.segna_km AS [KM DELLA MANUTENZIONE]
        FROM 
            manutenzione
        WHERE 
            manutenzione.cat_manut = ?
        ORDER BY 
            manutenzione.id;
        """
        cursor.execute(query, (cat_manut,))

    else:  # Caso 4: Entrambi generici (nome_bici = "Tutti" e cat_manut = "Tutte")
        query = """
        SELECT 
            manutenzione.nome_bici AS [NOME BICI],
            manutenzione.cat_manut AS [OGGETTO DI MANUTENZIONE],
            manutenzione.descrizione AS DESCRIZIONE,
            manutenzione.data_manut AS [DATA],
            manutenzione.segna_km AS [KM DELLA MANUTENZIONE]
        FROM 
            manutenzione
        ORDER BY 
            manutenzione.id;
        """
        cursor.execute(query)

    # Esecuzione della query
    data_manutenzione_2 = cursor.fetchall()
    conn.close()
    return data_manutenzione_2


def display_data_manutenzione_2(data_manutenzione_2):
    # Creazione della finestra principale
    root = tk.Tk()
    root.title("Report Manutenzione")
    # Creazione di una cornice con sfondo celeste per l'aspetto da report
    frame = tk.Frame(root, bg='light blue')
    frame.pack(fill=tk.BOTH, expand=True)

        # Creazione di una Treeview per visualizzare i dati in formato tabellare
    columns = ("NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DATA", "KM ALLA REGISTRAZIONE") 
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

    # Definizione delle intestazioni di colonna con font grassetto e centrato
    style = ttk.Style()
    style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), foreground='black')
    style.configure("Treeview", background="light blue", fieldbackground="light blue")
    style.map("Treeview", background=[('selected', 'sky blue')])

    # Definizione dei colori alternati per le righe della tabella
    tree.tag_configure('odd', background="light cyan")
    tree.tag_configure('even', background="azure")
    
     # Configurazione delle colonne
    for col in columns:
        tree.heading(col, text=col, anchor='center')
        tree.column(col, anchor="center", width=150)

        # Posizionamento della Treeview
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    
    # Rimuove eventuali dati esistenti
    for row in tree.get_children():
        tree.delete(row)
        
    # Aggiunge i nuovi dati alla Treeview
    #data = fetch_data(nome_bici)
    for i, row in enumerate(data_manutenzione_2):
        # Righe alternate con colore
        if i % 2 == 0:
            tree.insert("", tk.END, values=row, tags=('even',))
        else:
            tree.insert("", tk.END, values=row, tags=('odd',))
    
    def reportistica_excel_manutenzione_2():
        excel_file = "report_manutenzione.xlsx"
        # Controlla se il file è già aperto
        if os.path.exists(excel_file):
            try:
                # Prova a sovrascrivere il file
                df = pd.DataFrame(data_manutenzione_2, columns=["NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DATA", "KM ALLA REGISTRAZIONE"])
                df.to_excel(excel_file, index=False)
                messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}")
            except PermissionError:
                # Se il file è aperto, informa l'utente
                messagebox.showwarning("Attenzione Biagio", f"Prima di fare una nuova esportazione chiudi il file '{excel_file}' già aperto precedentemente.")
                return  # Esci dalla funzione se il file è aperto
        else:
            # Se il file non esiste, crealo
            df = pd.DataFrame(data_manutenzione_2, columns=["NOME", "OGGETTO DI MANUTENZIONE", "DESCRIZIONE", "DATA", "KM ALLA REGISTRAZIONE"])
            df.to_excel(excel_file, index=False)
            messagebox.showinfo("Esportazione completata", f"Report esportato in {excel_file}, ora puoi salvarlo con nome e stamparlo")

        
        
        
        
        
        #df.to_excel(excel_file, index=False)
        # Caricamento del file Excel con openpyxl per adattare larghezza delle colonne e aggiungere stile tabella
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            worksheet = workbook.active

            # Adatta larghezza delle colonne in base alla lunghezza del testo
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter  # Ottieni la lettera della colonna
                for cell in col:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = (max_length + 8)  # Aggiungi un po' di margine
                worksheet.column_dimensions[column].width = adjusted_width

                # Creazione della tabella con stile
            table_ref = f"A1:D{len(df) + 1}"  # Riferimento per l'area della tabella
            table = Table(displayName="ReportTable", ref=table_ref)

                # Imposta lo stile della tabella
            style = TableStyleInfo(
                name="TableStyleMedium9",  # Uno stile predefinito
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=True
            )
            table.tableStyleInfo = style
        worksheet.add_table(table)
    # Pulsante per esportare il report in Excel
    btn_export = tk.Button(root, text="Esporta in Excel", command=reportistica_excel_manutenzione_2)
    btn_export.pack(pady=5)

# Funzione per connettersi al database e creare le tabelle
def crea_tabella():
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
 
    c.execute('''CREATE TABLE IF NOT EXISTS biciclette (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_bici TEXT,
                    km_acc REAL DEFAULT 0.0,
                    km_ult_tragitto REAL DEFAULT 0.0,
                    data TEXT
                 )''')
                 
    # Creazione della tabella per il vettore aggiornamenti
    c.execute('''CREATE TABLE IF NOT EXISTS aggiornamenti_km (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    km REAL,
                    data TEXT,
                    dest TEXT
                 )''')
                 
    # Creazione della tabella manutenzione
    c.execute('''CREATE TABLE IF NOT EXISTS manutenzione (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_bici TEXT,
                    data_manut TEXT,
                    cat_manut TEXT,
                    descrizione TEXT,
                    segna_km REAL
                 )''')
                 
    # Creazione della tabella sostituzione
    c.execute('''CREATE TABLE IF NOT EXISTS sostituzione (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_bici TEXT,
                    cat_manut TEXT,
                    descrizione TEXT,
                    durata_km REAL
                 )''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS creazione_cat_manut (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cat_manut TEXT  
                 )''')
                 
    conn.commit()
    conn.close()
    
  
# Funzione per ottenere i nomi unici delle bici dal database
def get_bici():
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT nome_bici FROM biciclette")  # Prendi solo i nomi unici
    bici_list = [row[0] for row in c.fetchall()]
    conn.close()
    bici_list.append("Tutte")
    return bici_list
    
# Funzione per ottenere i nomi unici delle categorie di manutenzione
def get_cat_manut():
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT cat_manut FROM creazione_cat_manut")  # Prendi solo i nomi unici
    cat_manut_list = [row[0] for row in c.fetchall()]
    conn.close()
    cat_manut_list.append("Tutte")
    return cat_manut_list
        
        
# Funzione per creare una nuova bici
def crea_nuova_bici():
    nome = entry_nome_bici.get().strip()
    km_iniziali = entry_km_iniziali.get().strip()
    if nome and km_iniziali:
        conn = sqlite3.connect('biciclette.db')
        c = conn.cursor()
        c.execute("SELECT * FROM biciclette WHERE nome_bici = ?", (nome,))
        risultati = c.fetchall()
        conn.commit()
        conn.close()
        if risultati:
            messagebox.showwarning("Attenzione!", f"\nEsiste già la bici '{nome}'")
        else:
            try:
                km_iniziali = float(km_iniziali)
                conn = sqlite3.connect('biciclette.db')
                c = conn.cursor()
                data = datetime.now().strftime("%Y-%m-%d") 
                c.execute("INSERT INTO biciclette (nome_bici, km_acc, km_ult_tragitto, data) VALUES (?, ?, ?, ?)", 
                        (nome, km_iniziali, 0.0, data))
                conn.commit()
                conn.close()
                messagebox.showwarning("Grande!", f"Bici '{nome}' creata con {km_iniziali} km iniziali.")
            except ValueError:
                messagebox.showwarning("Ops", f"Inserisci un valore numerico valido per i chilometri.")
    else:
        messagebox.showwarning("Ops", f"COMPILA TUTTI I CAMPI.")


# Funzione per aggiornare i chilometri percorsi da una bici
def aggiorna_km_percorsi():
    nome = selected_bici.get().strip()  # Nome bici dalla selezione
    km_percorsi = entry_km_percorsi.get().strip()  # Km percorsi
    destinazione = entry_destinazione.get().strip()  # Destinazione
    data = entry_data.get().strip() #data
    
    if nome and km_percorsi and data:
        try:
             # Controllo del formato della data
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Ops", f"Inserisci la data in formato valido (YYYY-MM-DD).")
                return
            
            km_percorsi = float(km_percorsi)  # Convertiamo in float i km percorsi
            conn = sqlite3.connect('biciclette.db')
            c = conn.cursor()
            
            # Otteniamo gli ultimi km accumulati della bici
            c.execute("SELECT km_acc FROM biciclette WHERE nome_bici = ? ORDER BY id DESC LIMIT 1", (nome,))
            result = c.fetchone()
            
            if result:
                km_accumulati = result[0] + km_percorsi #result[0] perchè, anche se in result c'è solo un elemento, non si può sommare una tupla con un float
                #data = datetime.now().strftime("%Y-%m-%d")
                
                # Inseriamo i dati nella tabella biciclette
                c.execute("INSERT INTO biciclette (nome_bici, km_acc, km_ult_tragitto, data) VALUES (?, ?, ?, ?)", 
                          (nome, km_accumulati, km_percorsi, data))
                          
                # Inseriamo i km percorsi, la destinazione e la data nella tabella aggiornamenti_km
                c.execute("INSERT INTO aggiornamenti_km (km, data, dest) VALUES (?, ?, ?)", (km_percorsi, data, destinazione))
                
                conn.commit()

                # Output dei risultati
                messagebox.showwarning("Grande!", f"Kilometri per '{nome}' aggiornati. Totale ora: {km_accumulati} km. Sei arrivato a: '{destinazione}'.") 
                
   
            else:
                messagebox.showwarning("Ops", f"Attenzione: La bici '{nome}' non esiste.")
            
            conn.close()

        except ValueError:
            messagebox.showwarning("Ops", f"Inserisci un valore numerico valido per i chilometri.")
    else:
        messagebox.showwarning("Ops", f"COMPILA TUTTI I CAMPI.")

# Funzione per visualizzare i record filtrati per bici o a prescindere delle bici (mostra i record della tabella biciclette)
def visualizza_record_filtrati():
    #scelta = var_filtro.get()
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
    #if scelta == "Nome Bici":
    nome_filtro = selected_bici.get().strip()
    if nome_filtro:
            data = fetch_data(nome_filtro);
            display_data(data);
            #c.execute("SELECT * FROM biciclette WHERE nome_bici = ?", (nome_filtro,))
            #risultati = c.fetchall()
            #if risultati:
                #messagebox.showwarning("Report", f"\nRecord per la bici '{nome_filtro}'")
                #output_text.insert(tk.END, f"{'ID':<5}{'Nome':<20}{'Km Accumulati':<15}{'Ultimo Tragitto':<15}{'Data':<12}\n")
                #for record in risultati:
                    #output_text.insert(tk.END, f"{record[0]:<5}{record[1]:<20}{record[2]:<15}{record[3]:<15}{record[4]:<12}\n")
            #else:
                #messagebox.showwarning("Ops", f"Non ci sono dati per la bici '{nome_filtro}'.")
    else:
            messagebox.showwarning("Ops", f"Errore: Inserisci il nome della bici da filtrare.")
    
    #elif scelta == "Tutte le Bici":
        #tuttelebici = 'Tutte'
        #data = fetch_data(tuttelebici);
        #display_data(data); #chiamando questa funzione si chiama fetch_data e se poi viene schiacciato esporta excel si chiama reportistica_excel
        #c.execute("SELECT * FROM biciclette")
        #risultati = c.fetchall()
        #if risultati:
            #output_text.insert(tk.END, f"\nRecord per tutte le bici:\n")
            #output_text.insert(tk.END, f"{'ID':<5}{'Nome':<20}{'Km Accumulati':<15}{'Ultimo Tragitto':<15}{'Data':<12}\n")
            #for record in risultati:
               # output_text.insert(tk.END, f"{record[0]:<5}{record[1]:<20}{record[2]:<15}{record[3]:<15}{record[4]:<12}\n")
        #else:
            #output_text.insert(tk.END, "Non ci sono dati disponibili.\n")

    conn.close()

# Funzione per visualizzare le statistiche
def visualizza_statistiche():
    scelta = var_scelta.get()
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
    if scelta == "Nome Bici":
        # Cancella il contenuto attuale prima di inserire nuovi dati
        output_text.delete('1.0', 'end') 
        #nome_filtro = entry_nome_filtro_stat.get().strip()
        nome_filtro = selected_bici.get().strip()
        if nome_filtro == "Tutte":
            messagebox.showwarning("Attenzione!", f"\nFiltrare spuntando 'Tutte le bici' se vuoi vedere le tue statistiche a prescindere dalla bici utilizzata")
        if nome_filtro:
            c.execute("SELECT km_ult_tragitto, data FROM biciclette WHERE nome_bici = ? ORDER BY id", (nome_filtro,))
            risultati = c.fetchall()

            if len(risultati) > 1:
                km_percorsi = [r[0] for r in risultati[1:]]
                date_percorsi = [r[1] for r in risultati[1:]]
                media_km = sum(km_percorsi) / len(km_percorsi)
                output_text.insert(tk.END, f"Media dei km percorsi per '{nome_filtro}': {media_km:.2f} km.\n")
                varianza_km_percorsi = statistics.variance(km_percorsi)
                dev_std_km_percorsi = statistics.stdev(km_percorsi)
                coeff_variazione_km_percorsi = dev_std_km_percorsi/media_km
                coeff_variazione_km_percorsi = round(coeff_variazione_km_percorsi, 1)
                output_text.insert(tk.END, f"Coefficiente di variazione (regolarità) dei km percorsi: {coeff_variazione_km_percorsi:.2f}\n") #mettere una varianza normalizzata
                output_text.insert(tk.END, "Tale coefficiente può rappresentare la regolarità dei km percorsi. "
                           "Più si avvicina a zero, più sei regolare. Il valore soglia oltre il quale non si è più considerati regolari è 0.5 al di sotto di tale valore invece significa che "
                           "i chilometri percorsi ad ogni uscita in bici sono più vicini tra loro e si discostano poco dalla media")
            
                if coeff_variazione_km_percorsi < 0.5:
            
                    messagebox.showwarning("Ottimo!", f"Risulti essere regolare nelle uscite in termini di km percorsi : Hai un coefficiente di variabilità pari a {coeff_variazione_km_percorsi}")
                else:
                    messagebox.showwarning("Ops", f"Sei poco regolare, il tuo coefficiente è sopra la soglia ed è pari a {coeff_variazione_km_percorsi} ")
                # Creazione del grafico
                plt.figure(figsize=(10, 5))
                plt.plot(km_percorsi, marker='o', linestyle='-')
                # Linea della media
                plt.axhline(y=media_km, color='r', linestyle='-', label=f"Media ({media_km:.2f} km), Coeff.variazione ({coeff_variazione_km_percorsi:.2f})")
                plt.title(f'Kilometri Percorsi per {nome_filtro}')
                plt.xlabel('Registrazioni')
                plt.ylabel('Kilometri Percorsi')
                plt.grid()
                plt.xticks(range(len(km_percorsi)))  # Etichette per le registrazioni
                plt.legend()  # Mostra la legenda per distinguere la linea della media
                # Aggiungi cursori interattivi con mplcursors
                cursor = mplcursors.cursor(hover=False)

                # Mostra la data quando si passa il mouse sopra un punto
                @cursor.connect("add")
                def on_add(sel):
                    index = int(sel.index) # Indice del punto selezionato
                    sel.annotation.set_text(f"Data: {date_percorsi[index]}")
                plt.show()
            else:
                if nome_filtro == "Tutte":
                    output_text.insert(tk.END, f"Spunta Tutte le bici.\n")
                else:
                    output_text.insert(tk.END, f"Non ci sono abbastanza dati per calcolare le statistiche per '{nome_filtro}'.\n")
        else:
            messagebox.showwarning("Ops", f"Errore: Inserisci il nome della bici.")
    
    elif scelta == "Tutte le Bici":
            # Cancella il contenuto attuale nel box output prima di inserire nuovi dati
            output_text.delete('1.0', 'end') 
            c.execute("SELECT km, data FROM aggiornamenti_km")
            risultati = c.fetchall()
            
            vettore_colonna2 = [r[0] for r in risultati]
            date_percorsi = [r[1] for r in risultati]
            
            media_colonna2 = statistics.mean(vettore_colonna2)
            varianza_colonna2 = statistics.variance(vettore_colonna2)
            dev_std_colonna2 = statistics.stdev(vettore_colonna2)
            coeff_variazione = dev_std_colonna2/media_colonna2
            coeff_variazione = round(coeff_variazione, 1)

            output_text.insert(tk.END, f"Media dei km percorsi a prescindere dalle bici: {media_colonna2:.2f} km.\n")
            output_text.insert(tk.END, f"Coefficiente di variazione (regolarità) dei km percorsi: {coeff_variazione:.2f}\n") #mettere una varianza normalizzata
            output_text.insert(tk.END, "Tale coefficiente può rappresentare la regolarità dei km percorsi. "
                           "Più si avvicina a zero, più sei regolare. Il valore soglia oltre il quale non si è più considerati regolari è 0.5 al di sotto di tale valore invece significa che "
                           "i chilometri percorsi ad ogni uscita in bici sono più vicini tra loro e si discostano poco dalla media")
            
            if coeff_variazione < 0.5:
            
                messagebox.showwarning("Ottimo!", f"Risulti essere regolare nelle uscite in termini di km percorsi : Hai un coefficiente di variabilità pari a {coeff_variazione}")
            else:
                messagebox.showwarning("Ops", f"Sei poco regolare, il tuo coefficiente è sopra la soglia ed è pari a {coeff_variazione} ")
            
            # Creazione del grafico
            plt.figure(figsize=(10, 5))
            plt.plot(vettore_colonna2, marker='o', linestyle='-')
            plt.axhline(y=media_colonna2, color='r', linestyle='-', 
            label=f"Media ({media_colonna2:.2f} km), Coeff.variazione ({coeff_variazione:.2f})")
            plt.title('Kilometri Percorsi per tutte le Bici')
            plt.xlabel('Registrazioni')
            plt.ylabel('Kilometri Percorsi')
            plt.grid()
            plt.xticks(range(len(vettore_colonna2)))  # Etichette per le registrazioni
            plt.legend()
            cursor = mplcursors.cursor(hover=False)

                # Mostra la data quando si passa il mouse sopra un punto
            @cursor.connect("add")
            def on_add(sel):
                index = int(sel.index) # Indice del punto selezionato
                sel.annotation.set_text(f"Data: {date_percorsi[index]}")
            plt.show()
        
    
    conn.close()
    
# Funzione per aggiornare la manutenzione
def manutenzione():
    output_text.delete('1.0', 'end') 
    conn = sqlite3.connect('biciclette.db')
    c = conn.cursor()
    #cat_manut_new = entry_cat_manut_new.get().strip()  
    #if cat_manut_new:
       # conn = sqlite3.connect('biciclette.db')
       # c = conn.cursor()
        #c.execute("INSERT INTO creazione_cat_manut (cat_manut) VALUES (?)", (cat_manut_new,))
        #conn.commit()
        #output_text.insert(tk.END, f"Oggetto di manutenzione: '{cat_manut_new}' creato.\n")
        
    nome = selected_bici.get().strip()   # Nome bici dalla tendina
    cat_manut = selected_cat_manut.get().strip()          # Categoria di manutenzione dalla tendina
    descrizione = entry_descrizione.get().strip()      # Descrizione della categoria/oggetto di manutenzione
    
    if nome and cat_manut:
        # Otteniamo l'ultimo record di km_acc dalla tabella biciclette per la bici specificata
        c.execute("SELECT km_acc FROM biciclette WHERE nome_bici = ? ORDER BY id DESC LIMIT 1", (nome,))
        result = c.fetchone()
        
        if result:
            segna_km = result[0]
            data = datetime.now().strftime("%Y-%m-%d")
            
            # Inserimento dei dati nella tabella manutenzione
            c.execute("INSERT INTO manutenzione (nome_bici, data_manut, cat_manut, descrizione, segna_km) VALUES (?, ?, ?, ?, ?)", 
                      (nome, data, cat_manut, descrizione, segna_km))
            
            # Recupera gli ultimi due record di manutenzione per la bici e la categoria specificata
            c.execute("SELECT segna_km, descrizione FROM manutenzione WHERE nome_bici = ? AND cat_manut = ? ORDER BY id DESC LIMIT 2", (nome, cat_manut))
            manutenzioni = c.fetchall()
            #print(manutenzioni)
            # Se ci sono almeno due record, calcola la differenza di km e inserisci nella tabella sostituzione
            if len(manutenzioni) == 2:
                km_ultimo = manutenzioni[0][0]   # L'ultimo segna_km
                km_penultimo = manutenzioni[1][0]  # Il penultimo segna_km
                descrizione_penultima = manutenzioni[1][1]  # Descrizione del penultimo record
                durata_km = km_ultimo - km_penultimo
                
                
                # Inserimento nella tabella sostituzione con la descrizione del penultimo record
                c.execute("INSERT INTO sostituzione (nome_bici, cat_manut, descrizione, durata_km) VALUES (?, ?, ?, ?)", 
                          (nome, cat_manut, descrizione_penultima, durata_km))
                output_text.insert(tk.END, f"Sostituzione per '{nome}' inserita con durata di {durata_km:.2f} km.\n")
            
            conn.commit()
            output_text.insert(tk.END, f"Manutenzione per '{nome}' aggiornata in data '{data}'.\n")
        
        else:
            output_text.insert(tk.END, f"Attenzione: La bici '{nome}' non esiste.\n")
        
        conn.close()

    else:
        output_text.insert(tk.END, "Errore: Compila tutti i campi.\n")

def crea_cat_manut():
    cat_manut_new = entry_cat_manut_new.get().strip()  
    if cat_manut_new:
        conn = sqlite3.connect('biciclette.db')
        c = conn.cursor()
        c.execute("INSERT INTO creazione_cat_manut (cat_manut) VALUES (?)", (cat_manut_new,))
        conn.commit()
        output_text.insert(tk.END, f"Oggetto di manutenzione: '{cat_manut_new}' creato riavvia il programma per trovarlo nella tendina di selezione.\n")
        
#Funzione per la sostituzione
def sostituzione():
    output_text.delete('1.0', 'end') 
    nome = selected_bici.get().strip()  # Nome bici
    cat_manut = selected_cat_manut.get().strip()     # Oggetto di manutenzione
    if nome and cat_manut:
            data_manutenzione = fetch_data_manutenzione(nome,cat_manut); #report sostituizione
            display_data_manutenzione(data_manutenzione);
            conn = sqlite3.connect('biciclette.db')
            c = conn.cursor()
            c.execute("SELECT segna_km FROM manutenzione WHERE nome_bici = ? AND cat_manut = ? ORDER BY id DESC", (nome,cat_manut)) #seleziona dalla tabella manutenzione la colonna "segna km" filtrata per nome e cat.manut coi valori in ordine decrescente
            result = c.fetchall()
            #VISUALIZZAZIONE DELLA TABELLA SOSTITUZIONE
            #conn = sqlite3.connect('biciclette.db')
            #c = conn.cursor()
            #c.execute("SELECT * FROM sostituzione WHERE nome_bici = ? AND cat_manut = ?", (nome,cat_manut))
            #sostituzioni = c.fetchall()
            #for r in sostituzioni:
            #    print(r)
            #_________________
            if len(result) > 1:
                output_text.insert(tk.END, f"L'oggetto '{cat_manut}' è stato sostituito un numero di volte pari a {len(result)}.\n")
            if len(result) == 1:
                output_text.insert(tk.END, "L'oggetto non è ancora stato sostituito in questo database.\n")
    else:
            output_text.insert(tk.END, "Errore: Compila tutti i campi.\n")
            
      
def report_manutenzione():
    nome = selected_bici.get().strip()  # Nome bici
    cat_manut = selected_cat_manut.get().strip()     # Oggetto di manutenzione
    if nome and cat_manut:
            data_manutenzione_2 = fetch_data_manutenzione_2(nome,cat_manut); 
            display_data_manutenzione_2(data_manutenzione_2);
            conn = sqlite3.connect('biciclette.db')
            c = conn.cursor()
    else:
            output_text.insert(tk.END, "Errore: Compila tutti i campi.\n")
            

# Funzione per mostrare i campi solo per la scelta selezionata
def mostra_frame(frame):
    for f in frames:
        f.pack_forget()  # Nascondi tutti i frame
    if frame:
        frame.pack(padx=10, pady=10)  # Mostra solo il frame selezionato



  


# Setup dell'interfaccia grafica
root = tk.Tk()
root.title("Letuebici realizzato da Michele Veneziale")

# Ottieni il percorso della directory del file Python eseguibile o dello script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Costruisci il percorso relativo all'immagine di sfondo
image_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "sfondo.jpg")

# PER LO SFONDO
try:
    # Carica l'immagine utilizzando il percorso relativo
    background_image = Image.open(image_path)

    # Ridimensiona l'immagine a metà delle dimensioni originali
    new_size = (background_image.width // 2, background_image.height // 2)  # Dimensioni dimezzate
    background_image = background_image.resize(new_size, Image.LANCZOS)  # Usa LANCZOS per ridimensionamento di alta qualità

    # Converti l'immagine ridimensionata in un formato compatibile con Tkinter
    background_photo = ImageTk.PhotoImage(background_image)

    # Crea un'etichetta per visualizzare l'immagine di sfondo
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Copre l'intera finestra

except FileNotFoundError:
    print(f"Errore: Immagine di sfondo non trovata in {image_path}")
    # Puoi aggiungere qui un messaggio per indicare il problema o terminare il programma

# FINE PER LO SFONDO

#PER L'IMMAGINE LOGO
# Percorsi relativi delle immagini
logo_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "LE TUE BICI.png")
crea_bici_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "CREA BICI.jpg")
aggiorna_km_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "AGGIORNA KM.jpg")
report_tragitti_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "REPORT_TRAGITTI.jpg")
visualizza_statistiche_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "VISUALIZZA STATISTICHE.jpg")
manutenzione_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "MANUTENZIONE.jpg")
report_manutenzione_path = os.path.join(base_dir, "IMMAGINI INTERFACCIA", "REPORT MANUTENZIONE.jpg")

# Per l'immagine del logo
logo_image = Image.open(logo_path)
logo_size = (200, 200)  # Dimensioni desiderate
logo_image = logo_image.resize(logo_size, Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(root, image=logo_photo)
logo_label.place(x=10, y=10)

# Immagini per i pulsanti del menu
image_crea_bici = Image.open(crea_bici_path).resize((150, 50), Image.LANCZOS)
photo_crea_bici = ImageTk.PhotoImage(image_crea_bici)

image_aggiorna_km = Image.open(aggiorna_km_path).resize((150, 50), Image.LANCZOS)
photo_aggiorna_km = ImageTk.PhotoImage(image_aggiorna_km)

image_report_tragitti = Image.open(report_tragitti_path).resize((150, 50), Image.LANCZOS)
photo_report_tragitti = ImageTk.PhotoImage(image_report_tragitti)

image_visualizza_statistiche = Image.open(visualizza_statistiche_path).resize((150, 50), Image.LANCZOS)
photo_visualizza_statistiche = ImageTk.PhotoImage(image_visualizza_statistiche)

image_manutenzione = Image.open(manutenzione_path).resize((150, 50), Image.LANCZOS)
photo_manutenzione = ImageTk.PhotoImage(image_manutenzione)

image_report_manutenzione = Image.open(report_manutenzione_path).resize((150, 50), Image.LANCZOS)
photo_report_manutenzione = ImageTk.PhotoImage(image_report_manutenzione)
#FINE IMMAGINI PER PULSANTI MENU


crea_tabella() 

# Frame di base
sfondo="#A0B3D3"
frame_crea_bici = tk.Frame(root, bg = sfondo)
frame_aggiorna_km = tk.Frame(root, bg = sfondo)
frame_visualizza_filtrati = tk.Frame(root, bg = sfondo)
frame_statistiche = tk.Frame(root, bg = sfondo)
frame_manutenzione = tk.Frame(root, bg = sfondo)
frame_sostituzione = tk.Frame(root, bg = sfondo)


# Lista dei frame
frames = [frame_crea_bici, frame_aggiorna_km, frame_visualizza_filtrati, frame_statistiche,frame_manutenzione, frame_sostituzione]

# Menu di navigazione
frame_menu = tk.Frame(root)
frame_menu.pack(pady=10)

btn_crea_bici = tk.Button(frame_menu, image=photo_crea_bici, command=lambda: mostra_frame(frame_crea_bici))
btn_crea_bici.grid(row=0, column=0, padx=5, pady=5)

btn_aggiorna_km = tk.Button(frame_menu, image=photo_aggiorna_km, command=lambda: mostra_frame(frame_aggiorna_km))
btn_aggiorna_km.grid(row=0, column=1, padx=5, pady=5)

btn_visualizza_filtrati = tk.Button(frame_menu, image=photo_report_tragitti, command=lambda: mostra_frame(frame_visualizza_filtrati))
btn_visualizza_filtrati.grid(row=0, column=2, padx=5, pady=5)

btn_statistiche = tk.Button(frame_menu, image=photo_visualizza_statistiche, command=lambda: mostra_frame(frame_statistiche))
btn_statistiche.grid(row=0, column=3, padx=5, pady=5)

btn_manutenzione = tk.Button(frame_menu, image=photo_manutenzione, command=lambda: mostra_frame(frame_manutenzione))
btn_manutenzione.grid(row=0, column=4, padx=5, pady=5)

btn_sostituzione = tk.Button(frame_menu, image=photo_report_manutenzione, command=lambda: mostra_frame(frame_sostituzione))
btn_sostituzione.grid(row=0, column=5, padx=5, pady=5)

# Campi per "Crea Nuova Bici"
tk.Label(frame_crea_bici, text="Nome Bici:").grid(row=0, column=0, padx=5, pady=5)
entry_nome_bici = tk.Entry(frame_crea_bici)
entry_nome_bici.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_crea_bici, text="Km Iniziali:").grid(row=1, column=0, padx=5, pady=5)
entry_km_iniziali = tk.Entry(frame_crea_bici)
entry_km_iniziali.grid(row=1, column=1, padx=5, pady=5)

# Nota o commento sotto i campi di input
nota = "Nota: Dopo la creazione di una nuova bici riavvia il programma per aggiornare le tendine dei menù di selezione."
tk.Label(frame_crea_bici, text=nota, fg="red", font=("Arial", 10)).grid(row=0, column=3, columnspan=2, pady=(5, 10))

btn_crea_bici_submit = tk.Button(frame_crea_bici, text="Crea", command=crea_nuova_bici)
btn_crea_bici_submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Campi per "Aggiorna Km Percorsi"
tk.Label(frame_aggiorna_km, text="Nome Bici:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5)
# Creazione della lista a tendina (con valori unici dal database)
selected_bici = tk.StringVar()
bici_list = get_bici()  # Ottieni i nomi delle bici senza duplicati
if bici_list:
    selected_bici.set(bici_list[0])  # Imposta il valore predefinito

bici_dropdown = ttk.Combobox(frame_aggiorna_km, textvariable=selected_bici, values=bici_list, state="readonly", font=('Arial', 10))
bici_dropdown.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_aggiorna_km, text="Km Percorsi:").grid(row=1, column=0, padx=5, pady=5)
entry_km_percorsi = tk.Entry(frame_aggiorna_km)
entry_km_percorsi.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_aggiorna_km, text="Data:").grid(row=2, column=0, padx=5, pady=5)
entry_data = tk.Entry(frame_aggiorna_km)
entry_data.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_aggiorna_km, text="Destinazione:").grid(row=3, column=0, padx=5, pady=5)
entry_destinazione = tk.Entry(frame_aggiorna_km)
entry_destinazione.grid(row=3, column=1, padx=5, pady=5)

btn_aggiorna_km_submit = tk.Button(frame_aggiorna_km, text="Aggiorna", command=aggiorna_km_percorsi)
btn_aggiorna_km_submit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Campi per "Visualizza Record Filtrati"
#var_filtro = tk.StringVar(value="Nome Bici")  # Valore predefinito
#tk.Radiobutton(frame_visualizza_filtrati, text="Nome Bici", variable=var_filtro, value="Nome Bici").grid(row=0, column=0, padx=5, pady=5)
#tk.Radiobutton(frame_visualizza_filtrati, text="Tutte le Bici", variable=var_filtro, value="Tutte le Bici").grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_visualizza_filtrati, text="Nome Bici:").grid(row=1, column=0, padx=5, pady=5)
bici_dropdown = ttk.Combobox(frame_visualizza_filtrati, textvariable=selected_bici, values=bici_list, state="readonly", font=('Arial', 10))
bici_dropdown.grid(row=1, column=1, padx=5, pady=5)
#entry_nome_filtro = tk.Entry(frame_visualizza_filtrati)
#entry_nome_filtro.grid(row=1, column=1, padx=5, pady=5)

btn_visualizza_filtrati_submit = tk.Button(frame_visualizza_filtrati, text="Visualizza", command=visualizza_record_filtrati)
btn_visualizza_filtrati_submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Campi per "Visualizza Statistiche"
tk.Label(frame_statistiche, text="Filtra per:").grid(row=0, column=0, padx=5, pady=5)
var_scelta = tk.StringVar(value="Nome Bici")  # Valore predefinito
tk.Radiobutton(frame_statistiche, text="Nome Bici", variable=var_scelta, value="Nome Bici").grid(row=0, column=1, padx=5, pady=5)
tk.Radiobutton(frame_statistiche, text="Tutte le Bici", variable=var_scelta, value="Tutte le Bici").grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame_statistiche, text="Nome Bici:").grid(row=1, column=0, padx=5, pady=5)
bici_dropdown = ttk.Combobox(frame_statistiche, textvariable=selected_bici, values=bici_list, state="readonly", font=('Arial', 10))
bici_dropdown.grid(row=1, column=1, padx=5, pady=5)
#entry_nome_filtro_stat = tk.Entry(frame_statistiche)
#entry_nome_filtro_stat.grid(row=1, column=1, padx=5, pady=5)

btn_visualizza_statistiche_submit = tk.Button(frame_statistiche, text="Visualizza Statistiche", command=visualizza_statistiche)
btn_visualizza_statistiche_submit.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

# Campi per "Manutenzione"
tk.Label(frame_manutenzione, text="Nome Bici:").grid(row=0, column=0, padx=5, pady=5)
bici_dropdown = ttk.Combobox(frame_manutenzione, textvariable=selected_bici, values=bici_list, state="readonly", font=('Arial', 10))
bici_dropdown.grid(row=0, column=1, padx=5, pady=5)
#entry_manutenzione_nome_bici = tk.Entry(frame_manutenzione)
#entry_manutenzione_nome_bici.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_manutenzione, text="Descrizione:").grid(row=2, column=0, padx=5, pady=5)
entry_descrizione = tk.Entry(frame_manutenzione)
entry_descrizione.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_manutenzione, text="Crea nuovo oggetto di manutenzione:").grid(row=3, column=2, padx=5, pady=5)
entry_cat_manut_new = tk.Entry(frame_manutenzione)
entry_cat_manut_new.grid(row=3, column=3, padx=5, pady=5)

# Nota o commento sotto i campi di input
nota = "Nota: Se crei un nuovo ogg. di manutenzione riavvia il programma."
tk.Label(frame_manutenzione, text=nota, fg="red", font=("Arial", 8)).grid(row=4, column=3, columnspan=2, pady=(5, 10))

selected_cat_manut = tk.StringVar()
cat_manut_list = get_cat_manut()  # Ottieni le cat_manut delle bici senza duplicati

if cat_manut_list:
    selected_cat_manut.set(cat_manut_list[0])  # Imposta il valore predefinito

tk.Label(frame_manutenzione, text="Oggetto di manutenzione:").grid(row=1, column=0, padx=5, pady=5)
cat_manut_dropdown = ttk.Combobox(frame_manutenzione, textvariable=selected_cat_manut, values=cat_manut_list, state="readonly", font=('Arial', 10))
cat_manut_dropdown.grid(row=1, column=1, padx=5, pady=5)

btn_manutenzione_submit = tk.Button(frame_manutenzione, text="Salva", command=manutenzione)
btn_manutenzione_submit.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

btn_manutenzione_submit = tk.Button(frame_manutenzione, text="Crea ogg.manutenzione", command=crea_cat_manut)
btn_manutenzione_submit.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Campi per "Sostituzione"
tk.Label(frame_sostituzione, text="Nome Bici:").grid(row=0, column=0, padx=5, pady=5)
bici_dropdown = ttk.Combobox(frame_sostituzione, textvariable=selected_bici, values=bici_list, state="readonly", font=('Arial', 10))
bici_dropdown.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_sostituzione, text="Oggetto di manutenzione:").grid(row=1, column=0, padx=5, pady=5)
cat_manut_dropdown = ttk.Combobox(frame_sostituzione, textvariable=selected_cat_manut, values=cat_manut_list, state="readonly", font=('Arial', 10))
cat_manut_dropdown.grid(row=1, column=1, padx=5, pady=5)

btn_sostituzione_submit = tk.Button(frame_sostituzione, text="Report sostituzioni", command=sostituzione)
btn_sostituzione_submit.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

btn_sostituzione_submit = tk.Button(frame_sostituzione, text="Report manutenzione", command=report_manutenzione)
btn_sostituzione_submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Area di output con font Calibri Light, colore del testo #6C7F9A e sfondo #879FC1
output_text = tk.Text(root, height=10, width=80, font=("Calibri Light", 14), fg="white", bg="#879FC1")  # Sfondo colore #879FC1
output_text.pack(padx=10, pady=10)


# Aggiunta del copyright in basso a destra
copyright_label = tk.Label(root, text="© 2024 Michele Veneziale.", font=("Calibri Light", 14), fg="white", bg="#879FC1")
copyright_label.place(relx=1.0, rely=1.0, anchor='se')

# Aggiunta del nome utente in alto a sinistra
#welcome_label = tk.Label(root, text="LE TUE BICI", font=("Arial", 15), fg="black")
#welcome_label.place(x=10, y=10)  # Posiziona a 10 pixel dal bordo sinistro e 10 pixel dal bordo superiore

# Avvio del programma e creazione della tabella
crea_tabella()
mostra_frame(frame_crea_bici)  # Mostra il frame di creazione bici all'avvio

root.mainloop()


#CONTINUARE DA QUI
#Creare una presentazione del software
#Dare il software a biagio e metterlo su github e poi su linkedin

#SVILUPPI FUTURI
#Confrontare bici t test es. bici1 vs bici2 se sono statisticamente significativi classificare la bici migliore
#Inserire utente e password

