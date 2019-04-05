# ScrapCandidature42.py
# Python script to log to candidature.42.fr when looking for new places to apply for the check-in (usually, everything is gone pretty fast)
# You need to be on the "Check-in" step
# It needs 2 mail accounts (one to send the mail, one to receive the mail). They could be the same.
# The script will log to the site and check if there are avalable check-in and send mail if it's true
# I used to put this on a raspberry pi at start (if there's a power cut) and wait for the mail

from lxml import html
import requests, time, smtplib, re, logging

# Log file creation
def create_log():
    logging.basicConfig(filename='scan_candidature_42.log',level=logging.INFO)
    
    
# Sending mail to alert
def send_email():
    smtp_server = "sender_smtp_server"
    username = "sender_username"
    password = "sender_password"
    
    recipient = ["recipient_mail"]
    subject = "Candidature 42"
    text = "There's a new the place !"
    message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

    %s
    """ % (username, ", ".join(recipient), subject, text)
    
    mail_server = smtplib.SMTP(smtp_server, 587)
    logging.info("Serveur mail: %s", smtp_server)
    
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(username, password)
    logging.info("Logged in")
    mail_server.sendmail(username, recipient, message)
    logging.info("Mail send")
    mail_server.quit()

    
# Clean string
def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# Log to candidature 42 and scrap site for places
def log_and_scrap():
    # Login
    login_url = "https://candidature.42.fr/users/sign_in"
    payload = {'user[email]': 'candidature_login',
               'user[password]': 'candidature_password'}
    logging.info(time.ctime(int(time.time())))
    
    session_requests = requests.session()
    result = session_requests.get(login_url)
    logging.info("Welcome page: %s",  result)
    
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='authenticity_token']/@value")))[0]
    payload["authenticity_token"] = authenticity_token
    
    result = session_requests.post(
        login_url, 
        data = payload,
        headers = dict(referer=login_url)
    )
    logging.info("Login result: %s", result)
    
    # Scrapping
    send_email_flag = ""
    counter_line = 0
    counter_cell = 0
    
    tree = html.fromstring(result.content)
    calendar_table_tree = tree.xpath("//table[@class='table table-hover']/tbody/tr")
    for line in calendar_table_tree:
        counter_line += 1
        counter_cell = 0
        for item in line:
            counter_cell += 1
            if counter_cell == 2:
                item_str = cleanhtml(html.tostring(item).decode()).strip()
                if item_str.find("Plus de place") == -1
                    logging.info("Send mail flag ON")
                    send_email_flag = "X"
                
    if send_email_flag == "X":
        logging.info("Sending mail")
        send_email()
    else:
        logging.info("No more places")

# Main function
def main():
    interval_sec = 600.0
    starttime = time.time()
    
    create_log()
    while True:
        log_and_scrap();
        time.sleep(interval_sec - ((time.time() - starttime) % interval_sec))

while True:
    try :
        main()
        break
    except Exception as e:
        time.sleep(10)
        pass