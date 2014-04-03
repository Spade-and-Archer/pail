import getpass, imaplib, email.parser, os, re
#part 1:
def createdirectory(start,name):
    if not os.path.exists(start+"/"+name):
        os.makedirs(start+"/"+name)
doneID      = []
mailboxes   = {}
done={}

origin      = os.getcwd()
createdirectory(origin,"mail")

#Mail Module
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
        return email.message_from_string(msg_data[0][1])

def createraw(ID,mailbox):
    msg = GetFullMessage(ID,mailbox)
    createdirectory(origin+"/mail/"+mailbox+"/unsorted",ID)
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "a").close()
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "w")
    raw.write(str(msg))
    raw.close()
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "r")
    values = mail_list(raw)
    raw.close()
    rawwrite=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "w")
    value="\n".join(values)
    rawwrite.write(value)
    rawwrite.close()

def mail_list(msg):
    body=[""]
    finalbody=[""]
    count=0
    while True:
        line=msg.readline()
        if not line:
            break
        elif line[0:1]== " " or line == "":
            body[count]=body[count]+line[:len(line)-1]#Problem is it always adds to body 0
        else:
            count+=1
            body.append(line[0:len(line)-1])
        for line in body:
            try:
                line2=line.split(";")
                for thing in line2:
                    finalbody.append(thing)
            except:
                finalbody.append(line)
    return body

def get_info(ID,mailbox):
    createraw(ID,mailbox)
    createdirectory("/mail/bluebox/unsorted/"+ID,"info")
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "r")
    MIME=True
    Boundary = False
    To      =       "<Unknown>"
    From    =       "<Unknown>"
    place   =       "<Unknown>"
    Subject =       "<Unknown>"
    ConType =       "<Unknown>"
    Encoding =      "<Unknown>"
    Date    =       "<Unknown>"
    Charset =       "<Unknown>"
    Unsubscribe =   "<Unknown>"
    headers={
    'Boundary' : False,
    'To:'          :       "<Unknown>",
    'From:'        :       "<Unknown>",
    'Subject:'     :       "<Unknown>",
    'Content-Type:':       "<Unknown>",
    'Encoding:'    :       "<Unknown>",
    'Date:'        :       "<Unknown>",
    'Charset:'     :       "<Unknown>",
    'Unsubscribe:' :       "<Unknown>",
    }

    values=mail_list(raw)
    for line in values:
        for header in headers:
            potential = getvalue(header,line)
            if headers[header]=="<Unknown>"and potential != None:
                headers[header]=potential
    print str(headers)

"""def M_Breakdown(ID,mailbox):
    global done
    done={}
    createraw(ID,mailbox)
    info=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/info", "a").close()
    info=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/info", "a")
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "r")
    MIME=True
    Boundary = False
    To = "Unknown"
    From = "Unknown"
    place = "Unknown"
    Subject = "Unknown"
    ConType = "Unknown"
    Encoding = "Unknown"
    Date = "Unknown"
    Charset = "Unknown"
    Unsubscribe = "Unknown"
    # noinspection PyStatementEffect
    while True:
            CurLine=str(raw.readline())
            From=getvalue("From:",CurLine,[False])
            Subject=getvalue("Subject:",CurLine,[False])
            ConType=getvalue("Content-Type:",CurLine,[True,"",";",True])
            if CurLine[0:3] == "To:":
                To=CurLine[4:]
                To=To.strip()
                To=re.split("([<])",To)
            elif not CurLine:
                break
                ConType=CurLine[14:place].split()
            elif CurLine[0:26] =="Content-Transfer-Encoding:":
                Encoding=CurLine[26:].split()
            elif CurLine[0:5]=="Date:":
                Date=CurLine[6:].split()
            elif CurLine[0:17]=="List-Unsubscribe":
                Unsubscribe=CurLine[18:].split()
            try:
                CurLine.index("charset")
                try:
                    begin = CurLine.index('"')
                    end = CurLine[(begin+1):].index('"')
                    end+=begin+1
                    begin+=1
                    Charset = CurLine[begin:end]
                except:
                    try:
                        begin = CurLine.index("'")
                        end = CurLine[(begin+1):].index("'")
                        end+=begin+1
                        begin+=1
                        Charset = CurLine[begin:end]
                    except:
                        begin =CurLine.index('=')
                        begin+=1
                        Charset = CurLine[begin:].split()
            except:
                    pass
            if type(Boundary) != str:
                try:
                    place=CurLine.lower().index("boundary")
                    Boundary=True
                except:
                    Boundary = False
                if Boundary:
                    try:
                        begin = CurLine.index('"')
                        end = CurLine[(begin+1):].index('"')
                        end+=begin+1
                        begin+=1
                        Boundary = CurLine[begin:end].split()
                    except:
                        try:
                            begin = CurLine.index("'")
                            end = CurLine[(begin+1):].index("'")
                            end+=begin+1
                            begin+=1
                            Boundary = CurLine[begin:end].split()
                        except:
                            begin =CurLine.index('=')
                            begin+=1
                            Boundary = CurLine[begin:].split()
            if CurLine[0:5]=="Date:":
                #########################fix
                date = CurLine[6:]
                date=date.replace(",","")
                date=date.split()
                Time=date[5]
                date=[]
                for num in date:
                    Date.append(num)
                    Date.append("~!")
                Date="".join(Date)
    values=mail_list
    for line in values:

    print From
    print Subject
    Toaddr=[]
    touser=[]
    pair=False
    n="\n"
    to=To
    count=-1
    for thing in to:
        count+=1
        try:
            place=thing.index(" ")
            if place==0:
                To[count]=thing[1:]
        except:
            pass
    for thing in To:
        if thing[0:1]!='<':
            pair = True
            touser.append(thing.strip())
        elif thing[0:1] =="<" and pair==True:
            pair= False
            Toaddr.append(thing.strip())
        else:
            Toaddr.append(thing.strip())
            touser.append("NOID")
    Touser=""
    touser
    for thing in touser:
        Touser+=thing

        
    info.write(str("~!".join(Toaddr))+n)
    info.write(Touser+n)
    adbegin=From.index("<")
    adend=From.index(">")
    if place==0:
        info.write(From[adbegin:adend]+n)
    else:
        info.write(From[0:adbegin]+"~!"+From[adbegin:adend]+n)
    info.write(Subject+n)
    info.write(str(MIME)+n)
    if MIME:
        info.write(str(ConType)+n)
        info.write(str(" ".join(Encoding))+n)
        if type(Boundary)==list:
            info.write(str(Boundary.join(" "))+n)
    info.write(Date+n)
    try:
        info.write(Charset+n)
    except:
        info.write(" ".join(Charset)+n)
    try:
        info.write(Unsubscribe.join()+n)
    except:
        pass
    info.close()
    raw.close()
    body=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/body", "a").close()
    body=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/body", "a")
    raw=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/raw", "r")
    msgbody = []
    count = -1
    go = False
    counter = 0
    boundary=False
    while 1==1:
        count+=1
        
        CurLine=str(raw.readline())

        if not CurLine:#if current line does not exist, as the message has ended, this ends the program
            break
        elif go:
            msgbody.append(CurLine)
            counter+=1
        else:
            pass        
            
    if MIME:
        for msg in msgbody:
            body.write(msg)
    else:
        body.write("MIME = False, email may not display correctly.")
        for msg in msgbody:
            body.write(msg)
    print "Content is:"+ConType
    print boundary
    body.close()
    raw.close()
"""
#hi=[False,True,False]
#print getvalue("Subject:","Subject: hi",hi)
#print str("hia")

#login for testing
login("gmail.com","username","password","bluebox")

#testing code
unread = get_new_ID("bluebox",False)
for msg in unread:
    get_info(msg,"bluebox")
