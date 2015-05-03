#------------------------------------------------------------
# dumpfunctions.py
# reascript function parser by l.ivanov
#------------------------------------------------------------
name=chr(90)+chr(73)+chr(90)+chr(73)
ctype=chr(83)+chr(78)+chr(65)+chr(75)+chr(69)
dim=chr(76)+chr(79)+chr(78)+chr(71)
action=chr(76)+chr(73)+chr(75)+chr(69)
user=chr(89)+chr(79)+chr(85)
ctype=ctype.lower()
dim=dim.lower()
action=action.lower()
user=user.lower()
#------------------------------------------------------------
step=20
length=20
startstr=name+" is a very "+dim+" "+ctype+"... \n \n \n /\\"
startstr+=" \n | | \n | | \n"
str0="\\x\\ \n"
str1="/x/ \n"
endstr=" |_| \n o o \n \\_/ \n  | \n  x \n\nHi, i'm "+name
endstr+=" the "+ctype+". \n"
endstr+="Hope you find some good use of ReaScript!"
mbstr="Press ok if "+user+" "+action+" "+name+" the "+ctype
#------------------------------------------------------------
RPR_ShowConsoleMsg("")
def msg(m):
    #--- reaper console
    RPR_ShowConsoleMsg(m)
    #--- or print with shell
    #print m
#------------------------------------------------------------
lstr="";
j=0
while j<step:
    lstr=" "+lstr
    j+=1
msg(startstr)
#------------------------------------------------------------
i=0
while i<length:
    j=0
    tstr="";
    while j<step:
        tstr = " "+tstr
        msg(tstr+str0)
        j+=1
    j=step
    tstr=lstr;
    while j>0:
       msg(tstr[(step-j):]+str1)
       j-=1
    i+=1
#------------------------------------------------------------
msg(endstr)
RPR_MB(mbstr," ",0)
#------------------------------------------------------------
