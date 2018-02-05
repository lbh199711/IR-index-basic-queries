import sys
import sqlite3

total = []

def boolean_query(op,list1,list2):
    #init pointers
    x = 0 
    y = 0 
    outputlist= []
    if op.upper() == 'AND':#AND operation
        #intersect 2 lists
        while(1):
            #check if lists ended
            if (x==len(list1)) or (y==len(list2)):
                break 

            #x pointer compare with y pointer
            if list1[x]==list2[y]:#if eq then move onto next
                outputlist.append(list1[x])
                x += 1#move pointer
                y += 1
            elif list1[x]<list2[y]:#if one list is smaller then move it
                x += 1
            elif list1[x]>list2[y]:
                y += 1

            
            
    elif op.upper() == 'OR':#OR operation
        #add 2 lists but no duplicate
        while(1):
            #stop condition
            if (x==len(list1)):
                outputlist = outputlist+list2[y:]
                break
            elif(y==len(list2)):
                outputlist = outputlist+list1[x:]
                break
            #compare pointers
            if list1[x]==list2[y]:
                outputlist.append(list1[x])
                x += 1#move pointer
                y += 1
            elif list1[x]<list2[y]:#if they are not equal then just add the smallest one and move on
                outputlist.append(list1[x])
                x += 1
                
            elif list1[x]>list2[y]:
                outputlist.append(list2[y])
                y += 1

    else:
        #error
        return -1
    
    return outputlist


def not_query(list1,conn):
    #reverse index on list1
    global total
    if len(total)==0:#if this is the first time running
        c = conn.cursor()
        c.execute("SELECT DISTINCT movie_id FROM searchIndex ORDER BY movie_id;")
        total = c.fetchall()
    #pointers
    x = 0
    y = 0
    outputlist=[]
    while(1):
		#now total includes list1 we just need to take out list1
 	    
        if (x==len(list1)):#end when list1 end
            outputlist = outputlist+total[y:]
            break
        #compare pointers
        if list1[x]==total[y]:
            x += 1#move pointer
            y += 1
        elif list1[x]>total[y]:
            outputlist.append(total[y])
            y += 1
        elif list1[x]<total[y]:
            print("something went wrong in not_query x=",x," y=",y)
            return -1

    return outputlist
	
def main():
    #connect to database
    if len(sys.argv)>3 or len(sys.argv)==1:
        print ("invalid arguement")
        return
    elif len(sys.argv) == 2:
        print("no file location input,default as current directory")
        index_dir = "." 
        query = sys.argv[1]
    else:
        index_dir = str(sys.argv[1])
        query = sys.argv[2]
    
    #connect database
    conn = sqlite3.connect(index_dir+'/table.db')
	
    #so far assume there s no parenthesis 
    #and assume only 2 words
    query = query.lower().split()
    word_list={}
    for i in [0,2]:
        c = conn.cursor()
        c.execute("SELECT distinct movie_id FROM searchIndex WHERE word='"+query[i]+"' ORDER BY movie_id;")
        word_list[query[i]]=c.fetchall()

    IOlist = not_query(word_list[query[0]],conn)
	
    for i in IOlist:
        print(i[0])
		
	    
    conn.close()
    
    
    print (sys.argv)

main()
