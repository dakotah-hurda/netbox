def emailer(filename, body, subject):
    """
    This function is only meant to be used in conjunction with nb_report_support_dates.py, but can be tweaked to be used for other scripts.

    You must configure a .env file with the following parameters:

    EMAIL-USERNAME=""
    EMAIL-PASSWORD=""   
    """
    
    import smtplib
    import mimetypes
    import os
    from dotenv import load_dotenv
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.message import Message
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText

    load_dotenv()

    username = os.environ.get("EMAIL-USERNAME")
    password = os.environ.get("EMAIL-PASSWORD")
    emailfrom = username + "@DOMAIN-GOES-HERE"
    emailto = "EMAIL-YOU-ARE-SENDING-TO-GOES-HERE"
    fileToSend = filename
    
    server = smtplib.SMTP("SMTP-SERVER-GOES-HERE", 25)

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = subject
    body = MIMEText(body)
    msg.attach(body)

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)

    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    
    # server.starttls()
    # server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()