import os
import imaplib
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import threading
import re

selected_file_path = ""

def select_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(
        title="Select Migration Report Sheet",
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
    )
    if file_path:
        selected_file_path = file_path
        file_label.config(text=f"Selected File: {os.path.basename(file_path)}", fg="green")
        log_message("Sheet loaded successfully!")

def log_message(message):
    log_box.insert(tk.END, f"{message}\n")
    log_box.see(tk.END)

def start_download_thread():
    t = threading.Thread(target=run_downloader)
    t.daemon = True
    t.start()

def run_downloader():
    global selected_file_path
    
    if not selected_file_path:
        messagebox.showerror("Error", "Please select your CSV/Excel file first!")
        return
        
    imap_server = server_entry.get().strip()
    email_user = user_entry.get().strip()
    email_pass = pass_entry.get().strip()
    
    if not imap_server or not email_user or not email_pass:
        messagebox.showerror("Error", "Please fill in all the IMAP credentials!")
        return

    run_btn.config(state="disabled", text="Downloading...")

    try:
        log_message("Reading migration sheet...")
        if selected_file_path.endswith('.csv'):
            df = pd.read_csv(selected_file_path, encoding='cp1252')
        else:
            df = pd.read_excel(selected_file_path)
            
        subject_col = 'Subject'
        date_col = 'DateReceived' if 'DateReceived' in df.columns else ('DateSent' if 'DateSent' in df.columns else 'Date')
        
        if subject_col not in df.columns or date_col not in df.columns:
            messagebox.showerror("Error", f"Missing required columns. Found: {list(df.columns)}")
            run_btn.config(state="normal", text="Run Downloader")
            return

        log_message("Connecting to IMAP Server...")
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")
        
        save_folder = r"D:\MigrationRescue\DownloadedEMLs"
        os.makedirs(save_folder, exist_ok=True)
        
        download_count = 0

        for index, row in df.iterrows():
            subject = str(row[subject_col]).strip()
            raw_date_val = str(row[date_col]).strip()
            
            if not subject or pd.isna(row[subject_col]) or raw_date_val == 'nan':
                continue

            try:
                parsed_date = pd.to_datetime(raw_date_val, errors='coerce', format='mixed', dayfirst=True)
                if pd.isna(parsed_date):
                    log_message(f"Skipping row {index}: Format unrecognized for date '{raw_date_val}'")
                    continue
                imap_date = parsed_date.strftime('%d-%b-%Y')
            except Exception:
                log_message(f"Skipping row {index}: Error parsing date '{raw_date_val}'")
                continue
            
            # FIXED: Break subject into clean words and pick the longest unique keyword.
            # This completely avoids breaking IMAP search strings with single quotes (') or punctuation.
            words = re.findall(r'\b[a-zA-Z0-9]{4,}\b', subject)
            search_keyword = max(words, key=len) if words else subject[:15]
            
            log_message(f"Searching: '{subject[:25]}...' (Keyphrase: '{search_keyword}') on {imap_date}")
            
            search_criterion = f'(ON "{imap_date}" SUBJECT "{search_keyword}")'
            status, data = mail.search(None, search_criterion)
            mail_ids = data[0].split()
            
            if not mail_ids:
                log_message(" -> Target item not found on server.")
                continue
                
            for i, m_id in enumerate(mail_ids):
                status, bytes_data = mail.fetch(m_id, '(RFC822)')
                raw_email = bytes_data[0][1]
                
                # File system friendly clean name
                clean_filename_subj = "".join([c for c in subject if c.isalnum() or c==' ']).strip()[:40]
                filename = f"rescued_{index}_{i+1}_{clean_filename_subj}.eml"
                filepath = os.path.join(save_folder, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(raw_email)
                
                download_count += 1
                log_message(f" -> Saved: {filename}")
                
        mail.logout()
        log_message("--- Recovery Run Finished! ---")
        messagebox.showinfo("Success", f"Completed! Rescued {download_count} emails into {save_folder}!")
        
    except Exception as e:
        messagebox.showerror("System Error", str(e))
        log_message(f"Error occurred: {str(e)}")
        
    finally:
        run_btn.config(state="normal", text="Run Downloader")

# --- Setup GUI Window Elements ---
root = tk.Tk()
root.title("IMAP Email Migration Rescue Tool")
root.geometry("600x550")
root.config(padx=15, pady=15)

# Credentials Layout
tk.Label(root, text="IMAP Server Address (e.g. imap.gmail.com, mail.yourdomain.com):", font=("Arial", 10, "bold")).pack(anchor="w")
server_entry = tk.Entry(root, width=50)
server_entry.insert(0, "") 
server_entry.pack(fill="x", pady=2)

tk.Label(root, text="Email Address:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
user_entry = tk.Entry(root, width=50)
user_entry.pack(fill="x", pady=2)

tk.Label(root, text="Password / App Password:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
pass_entry = tk.Entry(root, show="*", width=50)
pass_entry.pack(fill="x", pady=2)

# File Management Layout
tk.Label(root, text="Step 1: Select Your Migration Report (Excel or CSV)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(20, 0))
file_btn = tk.Button(root, text="Browse Sheet File...", command=select_file, bg="#E1E1E1", height=2)
file_btn.pack(fill="x", pady=5)

file_label = tk.Label(root, text="No file selected yet.", fg="red")
file_label.pack(anchor="w", pady=2)

# Execution Action Layout
tk.Label(root, text="Step 2: Start Rescuing EMLs", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 0))
run_btn = tk.Button(root, text="Run Downloader", command=start_download_thread, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), height=2)
run_btn.pack(fill="x", pady=5)

# Real-time console logs display
tk.Label(root, text="Process Logs:", font=("Arial", 9, "italic")).pack(anchor="w", pady=(15, 0))
log_box = tk.Text(root, height=10, bg="#F4F4F4")
log_box.pack(fill="both", expand=True, pady=5)

root.mainloop()