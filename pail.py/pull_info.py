import getpass, imaplib, email.parser, os, re, glob,create_message
#Stable, finished, functions:
def createdirectory(start,name):
    if not os.path.exists(start+"/"+name):
        os.makedirs(start+"/"+name)

guess = "<Unknown>"
def start():
    global doneIDs, mailboxes, done, origin
    doneIDs      = []
    mailboxes   = {}
    done={}
    origin      = "C:/Users/Peter/Desktop/Andy's python project.py/pail/pail.py/"
    createdirectory("C:/Users/Peter/Desktop/Andy's python project.py/pail/pail.py/","mail")
    os.chdir("C:/Users/Peter/Desktop/Andy's python project.py/pail/pail.py/mail/")
    mailboxes = glob.glob('*')
    for mailbox in mailboxes:
        os.chdir("C:/Users/Peter/Desktop/Andy's python project.py/pail/pail.py/mail/"+mailbox)
        tags = glob.glob('*')
        for tag in tags:
            os.chdir("C:/Users/Peter/Desktop/Andy's python project.py/pail/pail.py/mail/"+'/'+mailbox+'/'+tag)
            latestIDs = glob.glob('*')
            count = -1
            for ID in latestIDs:
                count+=1
                ID = '/'.join(ID.split("\ "[:1]))
                latestIDs[count] = ID.split('/')[len(ID.split('/'))-1]
            for ID in latestIDs:
                doneIDs.append(ID)

    createdirectory(origin,"mail")

    mailboxes = {}
start()
def load_messages(mail_file):
    os.chdir(mail_file)
    mailboxes = glob.glob('*')
    messages = glob.glob('*\*\*')
    FinalMessages = []
    for message in messages:
        pass

def getvalue(header,CurLine):
    CurLine=CurLine.strip().lower()
    if CurLine[:len(header)] == header.lower():
        return CurLine[len(header):].strip()

def str2bool(v):
    if v.lower() == "true":
        return True
    elif v.lower == "false":
        return False
    else:
        return False

def login(host,username,password,name):

    createdirectory(origin+"/mail",name)
    createdirectory(origin+"/mail/"+name,"unsorted")
    mailboxes[name]=(imaplib.IMAP4_SSL("imap."+host))
    mailboxes[name].login(username, password)
    mailboxes[name].select()

def get_new_ID(mail,check):
    global doneIDs
    largest = 0
    for ID in doneIDs:
        if doneIDs != [] and int(ID.strip().strip(',').strip()) > int(largest):
            largest = ID
    print "largest is" + str(largest)
    if largest != 0:
        try:
            print origin
            infos = glob.glob(origin+'mail/' + mail+'/*/'+largest+'/info')
            for info in infos:
                try:
                    info1 = open(info,'r')
                    info = info1
                except:
                    pass
            count = 0
            while True:
                CurLine = info.readline()
                if not CurLine:
                    break
                count += 1
                if count == 9:
                    LastDate = processdate(CurLine[7:], True)
                    print LastDate
        except:
            pass
    LastDate = LastDate.split()
    FormattedLastDate = LastDate[1] +'-' + LastDate[2] + '-' + LastDate[3]
    rv, new_ID = mailboxes[mail].uid('search', None,'(SINCE ' + FormattedLastDate + ')')
    new_ID = new_ID[0].split()
    #new_ID should be a list of uids (in the form of integers) specifying all of the messages sent either on the same day as the last message downloaded or afterwards

    #the code below removes any uids that have already been done, but were included because time cannot be specified, and they were sent on the same date as the last message
    non_duplicated = []
    temp = ''
    for ID in new_ID:
        try:
            for DoneID in doneIDs:
                if DoneID == ID:
                    raise Exception('Duplicate')
            non_duplicated.append(ID)
        except:
            pass
    return non_duplicated

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

def processto(rawData):
    users = []
    mails = []
    currentMail=""
    currentUser=""
    mode = "user"
    usernameGiven = False
    rawData = rawData.split(",")
    for userAddressPair in rawData:
        for character in userAddressPair:
    # to test if mode should change:
            if character == "<":
                mode = "mail"
                usernameGiven = True
            elif character == ">":
                mode = "user"
                currentUser = currentUser.strip()
                usernameGiven = True
                if currentUser.strip() == "":
                    currentUser = guess
                users.append(currentUser)
                mails.append(currentMail)
                currentMail=""
                currentUser=""
    #now it has been established the mode will not change
            elif mode == "mail":
                currentMail+=character
            elif mode == "user":
                currentUser+=str(character)
#   the reason that it puts 'currentUser' in the 'mails' section is, when a client does not include a username, it will not put little arrow marks (< or >) in at all. Thus, instead of putting in a bunch of code to test for marks and use two different strategies depending on whether or not they exist, I chose to simply turn the 'username' into the address should the username not be defined.
    if usernameGiven:
        usermail = [users,mails]
    else:
        usermail = [[guess], [currentUser]]
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

def dateproc2(date, month1, month2, monthnum, deconvert):
    """This function simply checks if the month is equal to either month1 or month2 and, if it is, converts it to monthnum. It was getting tiresome to copy/paste this in constantly. if deconvert is true then it will instead return the month1 if date == monthnum"""
    if deconvert:
        option1 = monthnum #This is here to swap the values with the normal values
        option2 = monthnum
        convert_to = month1
    else:
        option1 = month1.lower()
        option2 = month2.lower()
        convert_to = monthnum
    if deconvert and date == option1 or date == option2 and len(date) < 3:
        return convert_to
    elif not deconvert:
        if date.strip().strip(',').strip().strip('"').strip().strip("'").strip().lower() == option1 or date.strip().strip(',').strip().strip('"').strip().strip("'").strip().lower() == option2 and date > 1:
            return monthnum

def processdate(raw_date,deconvert=False):
    """takes date and converts it to a dict e.g. {'time': '7:13:20', 'month': 4, 'year': '2013', 'weekday': 1, 'day': '22'} in utc"""
    newdate = {
        "weekday" : guess,
        "day":guess,
        "month":guess,
        "time":guess,
        "year":guess
    }
    if not deconvert:
        raw_date = raw_date.strip().split()
    else:
        new_raw_date = []
        raw_date = raw_date[1:int(len(raw_date))-2].split('><')
        new_raw_date.append(raw_date[1])
        new_raw_date.append(raw_date[2])
        new_raw_date.append(raw_date[3])
        new_raw_date.append(raw_date[4])
        new_raw_date.append(raw_date[0])
        count = -1
        for item in new_raw_date:
            count += 1
            try:
                new_raw_date[count] = int(new_raw_date[count])
            except:
                pass
        raw_date = new_raw_date
    newdate["day"] = raw_date[1]
    newdate["year"] = raw_date[3]
#   So you don't need to scroll around, the dateproc2 is little more than an if/else statement that checks if the variable is equal to the word month and, if it is, changes it to the number shown.the contractions of the months are capitalized so that they are capitalised when de-converting
    raw_date[2] = dateproc2(raw_date[2], "Jan", "january", 1, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Feb", "february", 2, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Mar", "march", 3, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Apr", "april", 4, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "May", "may", 5, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Jun", "june", 6, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Jul", "july", 7, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Aug", "august", 8, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Sep", "september", 9, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Oct", "october", 10, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Nov", "november", 11, deconvert)
    raw_date[2] = dateproc2(raw_date[2], "Dec", "december", 12, deconvert)
    newdate["month"] = raw_date[2]
    raw_date[0] = dateproc2(raw_date[0], "Mon", "monday", 1, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Tue", "tuesday", 2, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Wed", "wednesday", 3, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Thu", "thursday", 4, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Fri", "friday", 5, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Sat", "saturday", 6, deconvert)
    raw_date[0] = dateproc2(raw_date[0], "Sun", "sunday", 7 , deconvert)
    newdate["weekday"] = raw_date[0]
    raw_date[4] = raw_date[4].split(":")
    if not deconvert:
        time = {
            "hour"     : raw_date[4][0],
            "minute"   : raw_date[4][1],
            "second"   : raw_date[4][2]
        }
        positive = raw_date[5][:1]
        if positive.strip() == '+':
            positive = True
        else:
            positive =  False
        offset = raw_date[5].strip()[1:]
        offsetlist = []
        for number in range(4):
            offsetlist.append(offset[number])
        offset = offsetlist

    # The code below simply offsets the given time and turns it into utc time. I would have made a function, but I felt I would need to change too much of the code for it to be worth it ( I change the multiplier, the hour/minute, and the offset.)
        for num in range(4):
            offset[num] = int(offset[num])
        if offset[0] != 0:
            if positive:
                time['hour'] = int(time['hour']) + (offset[0] * 10)
            elif not positive:
                time['hour'] = int(time['hour']) - (offset[0] * 10)
        if offset[1] != 0:
            if positive:
                time['hour'] = int(time['hour']) + offset[1]
            elif not positive:
                time['hour'] = int(time['hour']) - offset[1]
        if offset[2] != 0:
            if positive:
                time['minute'] = int(time['minute']) + (offset[2] * 10)
            elif not positive:
                time['minute'] = int(time['minute']) - (offset[2] * 10)
        if offset[3] != 0:
            if positive:
                time['minute'] = int(time['minute']) + offset[3]
            elif not positive:
                time['minute'] = int(time['minute']) - offset[3]
        if offset == 0000 and not positive:
            time['hour'] = int(time['hour'] -10)
        time = str(time['hour']) + ':' + str(time['minute']) + ':' + str(time['second'])
        newdate['time'] = time
        return newdate
    else:
        time = raw_date[4]
        time = ':'.join(time)
        time = time + ' +0000'
        print time
        count = -1
        for item in raw_date:
            count += 1
            raw_date[count] = str(item)
        final_date = raw_date[0] +', '+ raw_date[1] + ' ' + raw_date[2] +' '+ raw_date[3] + ' ' + time
        return final_date

def processinfo(header):
    headers= header
#returns string of Content Type
    headers["Content-Type:"] = headers["Content-Type:"].strip()
#Returns String of Boundary in multi-part messages, if no boundary it return "<Unknown>"
    if headers['boundary'] != guess:
        headers["boundary"]=headers["boundary"].strip()[1:].strip().strip('"').strip('"')
    else:
        boundary = guess
#Returns a list that contains: a list of Recipient names (<unknown> if unknown) and a list of email addresses in such a way that To[0][4] is the name assigned to the address To[1][4]
    headers["To:"]=processto(headers["To:"])
#returns a list of: [Username,email address]
    headers["From:"]=processfrom((headers["From:"]))
#Returns a string of the Subject
    headers["Subject:"]=headers["Subject:"].strip()
#Returns a string of the Encoding, this is not likely to be used due to it already being decoded, but was included as a precaution (i.e. the more you know)
    headers["Content-Transfer-Encoding:"]=headers["Content-Transfer-Encoding:"].strip()
#Returns <day of the week><day of the month><month><year><minute><hour>
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
"us-ascii",
"ascii"

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
    s = 's'
    found_header_count = 0
    Done = False
    for line in values:
        if Done:
            break
        for  header in headers:
            if found_header_count > 8:
                Done = True
                break
            elif found_header_count == 8 and headers['List-Unsubscribe:'] == guess:
                Done = True
                break
            potential = getvalue(header,line)
            if headers[header]=="<Unknown>"and potential != None:
                found_header_count += 1
                headers[header]=potential
    errors = []
    for header in headers:
        if headers[header] == guess:
            errors.append(header)
    headers = processinfo(headers)
    return (errors,headers)

def capitalize(name):
    Final_name = name[0].upper()
    mode = 'lower'
    count = -1
    for letter in name:
        count += 1
        if letter == ' ':
            mode = 'upper'
            Final_name += ' '
        elif mode == 'upper':
            Final_name += letter.upper()
            mode = 'lower'
        elif count != 0:
            Final_name += letter.lower()
    return Final_name

def find_name(username,email,raw_name,raw_email):
    count = -1
    Final_List = []
    raw_list_N = []
    raw_list_A = []
    if type(raw_name) == list:
        raw_list_N = raw_name
    if type(raw_name) == str:
        raw_list_N.append(raw_name)
    if type(raw_email) == list:
        raw_list_A = raw_email
    if type(raw_email) == str:
        raw_list_A.append(raw_email)
    raw_list = [raw_list_N,raw_list_A]

    for name in raw_list[0]:
        count +=1
        if name == '' or len(name) <1:
            raw_list[0][count].remove()
    count = -1
    for name in raw_list[0]:
        count+=1
        if name != guess and name != '':
            name = name.strip('"').strip("'").strip('>').strip('<').strip().strip('"').strip("'").strip('>').strip('<').strip('/').strip('\ '.strip()).strip()
        else:
            name = '<unknown>'
        if raw_list[1][count].lower() == email.lower().strip()+'@gmail.com':
            name = username
        Final_name = ''
        if name == '':
            name = '<unknown>'
        Final_List.append(capitalize(name))
    return '><'.join(Final_List)

def save_info(ID,mailbox,username,email):
    """format:
    To: <xxxxx@gmail.com><yyyyyy@gmail.com><zzzzz@gmail.com>
    To: <mr.X><Mr.Y><Mr.Z>
    From: <xyz@gmail.com>
    From: <xyz>
    Content-Transfer-Encoding: <quoted-printable>
    Charset: <utf-8>
    Content-Type: <Multipart/Alternative>
    Boundary: <boundary506>
    Date: <2:12:02><3><6><5><2014> #'time': '2:12:02', 'weekday': 3, 'day': '6', 'month': 5, 'year': '2014'
    List-Unsubscribe: <Unknown>
    Subject: <we love cats>
    """
    n = '\n'
    errors,info = get_info(ID,mailbox,)
    file=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/info", "a").close()
    file=open(origin+"/mail/"+mailbox+"/unsorted/"+ID+"/info", "w")
    file_string = 'To: <'
    file_string += '><'.join(info['To:'][1])
    file_string += '>' + n
    file_string += 'To: <'
    info['To:'][0] = find_name(username,email,info['To:'][0],info['To:'][1])
    file_string += info['To:'][0]
    file_string += '>' + n
    file_string += 'From: <'
    file_string += info['From:'][1] + '>\n'
    info['From:'][0] = find_name(username,email,info['From:'][0],info['From:'][1])
    file_string += 'From: <' + info['From:'][0] + '>\n'
    file_string += 'Content-Transfer-Encoding: <' + info['Content-Transfer-Encoding:'] + '>\n'
    file_string += 'Charset: <' + info['charset'] + '>\n'
    file_string += 'Content-Type: <' + info['Content-Type:'] + '>\n'
    file_string += 'Boundary: <' + info['boundary'] + '>\n'
    file_string += 'Date: <' + str(info['Date:']['time']) + '><' + str(info['Date:']['weekday']) + '><' + str(info['Date:']['day']) + '><' + str(info['Date:']['month']) + '><' + str(info['Date:']['year']) + '>\n'
    if info['List-Unsubscribe:'] != guess:
        info['List-Unsubscribe:'] = info['List-Unsubscribe:'].strip('<').strip('>')
    file_string += 'List-Unsubscribe: <' + info['List-Unsubscribe:'] + '>\n'
    file_string += 'Subject: <' + info['Subject:'].capitalize() + '>\n'

    file.write(file_string)
    print file_string
    print ID
    file.close()

#login for testing
start()
password = open('C:\Users\Peter\Desktop\password','r')
password_string = password.readline()
username_string = password.readline()
login("gmail.com",username_string,password_string,"bluebox")
print username_string
#testing code
unread = get_new_ID("bluebox",False)
for msg in unread:
    info = save_info(msg,"bluebox",'Sam Spade',username_string)

def notes():
    """
     When processing qouted printable text the text must be decoded with https://docs.python.org/2/library/quopri.html#quopri.decode  v
    """
