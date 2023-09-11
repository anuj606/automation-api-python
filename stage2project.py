import imaplib
import email
import csv
import re
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
from operator import itemgetter


html_converter = html2text.HTML2Text()
html_converter.ignore_links = True

def getEmails(credentials, max_lines=1000000): 
    output = []
    for username, password in credentials:
        my_email = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        my_email.login(username, password)
        my_email.select('INBOX')

        _, data = my_email.search(None, '(UNSEEN)')
        unread_message_ids = data[0].split()

        for message_id in unread_message_ids[-15:]:
            _, messages = my_email.fetch(message_id, '(RFC822)')

            for message in messages:
                if type(message) is tuple:
                    message_body = email.message_from_bytes((message[1]))
                    messagetext, messagehtml, email_date = "", "", None
                    for part in message_body.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload()
                            body_without_regards = re.sub(r'Regards.*', '', body, flags=re.DOTALL)
                            body_without_regards = body_without_regards.replace("good morning", '').replace("hello", '')
                            messagetext = '\n'.join(body_without_regards.strip().split('\n')[:max_lines])
                        if part.get_content_type() == 'text/html':
                            soup = BeautifulSoup(part.get_payload(), 'lxml')
                            html_text_content = soup.get_text()
                            messagehtml = '\n'.join(html_text_content.strip().split('\n')[:max_lines])

                    # Extract and parse email date
                    email_date = message_body['date']
                            
                    output.append([messagetext, messagehtml, email_date])

        # Sort emails by arrival time in ascending order
        output.sort(key= lambda row: email.utils.parsedate_tz(row[2]))

        my_email.close()
        my_email.logout()

    return output


if __name__ == "__main__":
    with open(r"credentials.csv") as csvfile:
        credentials = csv.reader(csvfile, delimiter=' ')
        
        output = getEmails(credentials)

        with open(r"out.csv", 'w', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for email_text in output:
                writer.writerow(email_text)
