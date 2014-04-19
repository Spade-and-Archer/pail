import getpass, imaplib, email.parser, os, re
#Stable, finished, functions:
def createdirectory(start,name):
    if not os.path.exists(start+"/"+name):
        os.makedirs(start+"/"+name)

guess = "<Unknown>"
def start():
    global doneID, mailboxes, done, origin
    doneID      = []
    mailboxes   = {}
    done={}

    origin      = os.getcwd()
    createdirectory(origin,"mail")

def getvalue(header,CurLine):
    CurLine=CurLine.strip()
    if CurLine[:len(header)] == header:
        return CurLine[len(header):].strip()

def str2bool(v):
    if v.lower() == "true":
        return True
    elif v.lower == "false":
        return False
    else:
        return False

def login(host,username,password,name):
    try:
        createdirectory(origin+"/mail",name)
        createdirectory(origin+"/mail/"+name,"unsorted")
        mailboxes[name]=(imaplib.IMAP4_SSL("imap."+host))
        mailboxes[name].login(username, password)
        mailboxes[name].select()
    except:
        print 'Invalid username, password, or directory name'
        print 'Errors may include: slashes, punctuation, spaces, unrecognized characters or invalid usernames or passwords'

def get_new_ID(mail,check):
    global doneID
    rv, new_ID = mailboxes[mail].uid('search', None,'UnSeen')
    new_ID = new_ID[0].split()
    duplicate = False
    if check:
        for ID in new_ID:
            for DID in doneID:
                if DID == ID:
                    new_ID.remove(ID)
                    duplicate=True
                    break
            if not duplicate:
                doneID.append(ID)
    return new_ID

def GetFullMessage(ID,mailbox):
    typ, msg_data = mailboxes[mailbox].uid('fetch', ID, '(RFC822)')
    mailboxes[mailbox].uid('STORE', ID, '-FLAGS', '(\Seen)')
    if typ != 'OK':
        print "ERROR getting message", ID
    else:
#        return email.message_from_string(msg_data[0][1])
        msg_data = "".join(str(email.message_from_string(msg_data[0][1])).split("=\r\n"))
        return msg_data

def createraw(ID,mailbox):
    msg = GetFullMessage(ID,mailbox)
    createdirectory(origin+"/mail/"+mailbox+"/unsorted",ID)
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw1", "a").close()
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw1", "w")
    raw.write(str(msg))
    raw.close()
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "a").close()
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw1", "r")
    values = mail_list(raw)
    raw.close()
    rawwrite=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "w")
    value="\n".join(values)
    rawwrite.write(value)
    rawwrite.close()

#Less stable functions:
def mail_list(msg):
    body=[""]
    count=0
    try:
        while True:
            line=msg.readline()
            if not line:
                break
            else:
                lines=line.split(";")
                counter = 0
                for string in lines:
                    counter +=1
                    try:
                        if lines[0] != line and counter ==2:
                            count+=1
                            counter+=1
                            body.append(string.strip())
                        else:
                            raise Exception('spam')
                    except:
                        if string[0:1]== " " or string == "":
                            body[count]=body[count]+string[:len(string)].strip()
                        else:
                            count+=1
                            body.append(string[0:len(string)].strip())
        return body
    except:
        pass

def processto(to):
    users = []
    mails = []
    curmail=""
    curuser=""
    mode = "user"
    defined = False
    to = to.split(",")
    for group in to:
        for char in group:
    # to test if mode should change:
            if char == "<":
                mode = "mail"
                defined = True
            elif char == ">":
                mode = "user"
                curuser = curuser.strip()
                defined = True
                if curuser.strip() == "":
                    curuser= guess
                users.append(curuser)
                mails.append(curmail)
                curmail=""
                curuser=""
    #now it has been established the mode will not change
            elif mode == "mail":
                curmail+=char
            elif mode == "user":
                curuser+=str(char)
    if defined:
        usermail = [users,mails]
    else:
        usermail = [[guess], [curuser]]
    return usermail

def processfrom(From):
    mail=""
    user=""
    mode = "user"
    for char in From:
# to test if mode should change:
        if char == "<":
            mode = "mail"
        elif char == ">":
            mode = "user"
        elif mode == "mail":
            mail+=char
        elif mode == "user":
            user+=char
    usermail = [user.strip().strip('"').strip("'"),mail.strip()]
    return usermail

def processhtml(html):
    mode = "none"
    current = ""
    for char in html:
        if char == "<":
            mode = "begin phrase"
        elif char == ">":
            mode = "none"
#now it has been established the mode will not change
        elif mode == "begin phrase"and char.lower() == "i" or char.lower() == "m" or char.lower() == "g":
            current += char
            counter +=1
            if counter == 3:
                pass
        else:
            counter = 0
            curent = ""

def dateproc2(date2, month1, month2, monthnum):
    try:
        if date2.strip().lower() == month1 or date2.strip().lower() == month2 and len(date2) > 1:
            return monthnum
        else:
            return date2
    except:
        return date2


def processdate(date):
    date2 = {
        "day":guess,
        "month":guess,
        "time":guess,
        "year":guess
    }
    date = date.strip().split()
    date2["day"] = date[1]
    date2["month"] = date[2]
    date[2] = dateproc2(date[2], "jan", "january", 1)
    date[2] = dateproc2(date[2], "feb", "february", 2)
    date[2] = dateproc2(date[2], "mar", "march", 3)
    date[2] = dateproc2(date[2], "apr", "april", 4)
    date[2] = dateproc2(date[2], "may", "may", 5)
    date[2] = dateproc2(date[2], "jun", "june", 6)
    date[2] = dateproc2(date[2], "jul", "july", 7)
    date[2] = dateproc2(date[2], "aug", "august", 8)
    date[2] = dateproc2(date[2], "sep", "september", 9)
    date[2] = dateproc2(date[2], "oct", "october", 10)
    date[2] = dateproc2(date[2], "nov", "november", 11)
    date[2] = dateproc2(date[2], "dec", "december", 12)
    print date[2]
    return date
def processinfo(header):
    headers= header
#returns string of Content Type
    headers["Content-Type:"] = headers["Content-Type:"].strip()
#Returns String of Boundary in multi-part messages, if no boundary it return "<Unknown>"
    headers["boundary"]=headers["boundary"].strip()[1:].strip('"').strip('"')
#Returns a list that contains: a list of Recipient names (<unknown> if unknown) and a list of email addresses in such a way that To[0][4] is the name assigned to the address To[1][4]
    headers["To:"]=processto(headers["To:"])
#returns a list of: [Username,email address]
    headers["From:"]=processfrom((headers["From:"]))
#Returns a string of the Subject
    headers["Subject:"]=headers["Subject:"].strip()
#Returns a string of the Encoding, this is not likely to be used due to it already being decoded, but was included as a precaution (i.e. the more you know)
    headers["Content-Transfer-Encoding:"]=headers["Content-Transfer-Encoding:"].strip()
#Returns <day of the week><day of the month><month><year><minute><hour><time zone>
    headers["Date:"]=processdate(headers["Date:"].strip())
    headers["charset"]=processCharset(headers["charset"].strip().strip("=").strip().strip('"').strip("'").strip())
    headers["List-Unsubscribe:"] = headers["List-Unsubscribe:"]
    return headers

def processCharset(charset):
    charsets = [
"big5"        ,        # - Chinese Traditional (Big5)
"euc-kr"      ,        # - Korean (EUC)
"iso-8859-1"  ,        # - Western Alphabet
"iso-8859-2"  ,        # - Central European Alphabet (ISO)
"iso-8859-3"  ,        # - Latin 3 Alphabet (ISO)
"iso-8859-4"  ,        # - Baltic Alphabet (ISO)
"iso-8859-5"  ,        # - Cyrillic Alphabet (ISO)
"iso-8859-6"  ,        # - Arabic Alphabet (ISO)
"iso-8859-7"  ,        # - Greek Alphabet (ISO)
"iso-8859-8"  ,        # - Hebrew Alphabet (ISO)
"koi8-r"      ,        # - Cyrillic Alphabet (KOI8-R)
"shift-jis"   ,        # - Japanese (Shift-JIS)
"x-euc"       ,        # - Japanese (EUC)
"utf-8"       ,        # - Universal Alphabet (UTF-8)
"windows-1250",        # - Central European Alphabet (Windows)
"windows-1251",        # - Cyrillic Alphabet (Windows)
"windows-1252",        # - Western Alphabet (Windows)
"windows-1253",        # - Greek Alphabet (Windows)
"windows-1254",        # - Turkish Alphabet
"windows-1255",        # - Hebrew Alphabet (Windows)
"windows-1256",        # - Arabic Alphabet (Windows)
"windows-1257",        # - Baltic Alphabet (Windows)
"windows-1258",        # - Vietnamese Alphabet (Windows)
"windows-874",         # - Thai (Windows)
"UTF-8",
"KOI8",
"us-ascii"

]
    for chars in charsets:
        try:
            place=charset.lower().index(chars.lower())
            charset2 = charset[place:len(chars)+1]
            return charset2.lower()
        except:
            pass

def get_info(ID,mailbox):
    createraw(ID,mailbox)
    createdirectory("/mail/bluebox/unsorted/"+ID,"info")
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "r")
    MIME=True
    global boundaries
    boundaries = []
    headers={
    'boundary'     :              "<Unknown>",
    'To:'          :              "<Unknown>",
    'From:'        :              "<Unknown>",
    'Subject:'     :              "<Unknown>",
    'Content-Type:':              "<Unknown>",
    'Content-Transfer-Encoding:': "<Unknown>",
    'Date:'        :              "<Unknown>",
    'charset'      :              "<Unknown>",
    'List-Unsubscribe:' :         "<Unknown>",
    }

    values=mail_list(raw)
    for line in values:
        for header in headers:
            potential = getvalue(header,line)
            if headers[header]=="<Unknown>"and potential != None:
                headers[header]=potential

    headers = processinfo(headers)
    return headers

#login for testing
start()
login("gmail.com","username","********","bluebox")

#testing code
unread = get_new_ID("bluebox",False)
for msg in unread:
    print get_info(msg,"bluebox")
