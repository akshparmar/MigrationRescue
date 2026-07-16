# MigrationRescue

🛟 IMAP Email Migration Rescue Tool
A lightweight, open-source Python GUI utility designed to automatically reconnect to old source IMAP email servers and rescue specific emails (.eml format) that were skipped or failed during a cloud migration (like IMAP to Microsoft 365).

How to Prepare Your Input Sheet
The tool accepts either an Excel (.xlsx) or CSV sheet. It searches for items row-by-row based on the column headers.

Make sure your sheet contains these two exact column names:

Subject: The exact subject line of the email to look for.

DateReceived (or Date): The timestamp of when the email hit the server.

Tip: You can download and use the template_skipped.csv file in this repository as your baseline!

Setup & Installation Instructions
1. Clone or Download the Tool
Download the files to a folder on your computer (e.g., D:\MigrationRescue).

2. Install the Required Packages
Open your Command Prompt (CMD) inside the folder and install the necessary data handling components:
Run the main graphical interface from CMD
python app.py

Step-by-Step Guide to Getting EMLs
Enter IMAP Credentials: Input the host address of your old source mail server (e.g., mail.yourdomain.com), your username, and your password.

Load the Sheet: Click the Browse Sheet File... button and select your custom CSV or Excel file containing the skipped items report.

Run Downloader: Click the green Run Downloader button.

Collect Files: The app will cycle through each entry, log into your source mailbox, find the matching messages, and download them seamlessly as .eml files into:
D:\MigrationRescue\DownloadedEMLs

You can now take those .eml files and easily drag-and-drop or import them straight into your users' new active Microsoft 365 Outlook accounts!

