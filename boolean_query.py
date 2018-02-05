import sys
import sqlite3
def boolean_query(op,list1,list2):
    #init pointers
    x = 0 
    y = 0 
    outputlist= []
    if op.upper() == 'AND':#AND operation
        #intersect 2 lists
        while(1):
            #x pointer compare with y pointer
            if list1[x]==list2[y]:#if eq then move onto next
                outputlist.append(list1[x])
                x += 1#move pointer
                y += 1
            elif list1[x]<list2[y]:#if one list is smaller then move it
                x += 1
            elif list1[x]>list2[y]:
                y += 1
            #check if lists ended
            if (x==len(list1)) or (y==len(list2)):
                break 
            
            
    elif op.upper() == 'OR':#OR operation
        #add 2 lists but no duplicate
        while(1):
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
            if (x==len(list1)):
                outputlist = outputlist+list2[y:]
                break
            elif(y==len(list2)):
                outputlist = outputlist+list1[x:]
                break
    else:
        #error
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
    query = query.split()
    word_list={}
    for i in [0,2]:
        c = conn.cursor()
        c.execute("SELECT distinct movie_id FROM searchIndex WHERE word='"+query[i]+"' ORDER BY movie_id;")
        word_list[query[i]]=c.fetchall()

    IOlist = boolean_query(query[1],word_list[query[0]],word_list[query[2]])

    for i in IOlist:
        print(i[0])    
    conn.close()
    
    
    print (sys.argv)

main()
