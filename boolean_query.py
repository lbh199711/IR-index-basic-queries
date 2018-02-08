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
            if list1[x][0]==list2[y][0]:#if eq then move onto next
                outputlist.append(list1[x])
                x += 1#move pointer
                y += 1
            elif list1[x][0]<list2[y][0]:#if one list is smaller then move it
                x += 1
            elif list1[x][0]>list2[y][0]:
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
            if list1[x][0]==list2[y][0]:
                outputlist.append(list1[x])
                x += 1#move pointer
                y += 1
            elif list1[x][0]<list2[y][0]:#if they are not equal then just add the smallest one and move on
                outputlist.append(list1[x])
                x += 1
                
            elif list1[x][0]>list2[y][0]:
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
        c = conn.cursor()#get all IDs 
        c.execute("SELECT DISTINCT movie_id FROM searchIndex ORDER BY movie_id;")
        total = c.fetchall()
    #pointers
    x = 0
    y = 0
    outputlist=[]
    print(list1)
    while(1):
		#now $total includes $list1 we just need to take out $list1
        if (x==len(list1)):#end when list1 end
            outputlist = outputlist+total[y:]
            break
        #compare pointers
        if list1[x][0]==total[y][0]:
            x += 1#move pointer
            y += 1
        elif list1[x][0]>total[y][0]:#if not eq then append outputlist
            outputlist.append(total[y])
            y += 1
        elif list1[x][0]<total[y][0]:#list1[x] should never be smaller than total[y]
            print("something went wrong in not_query x=",x," y=",y)
            return -1
    print(outputlist)
    return outputlist


def term_query(list1,list2):
    #this find the index with 2 consecutive words
    #list 1 and list 2 contains [(id,position)]
    #init pointers
    x = 0 
    y = 0 
    outputlist= []

    #intersect 2 lists
    #list2 is the word behind list1 
    while(1):
        #check if lists ended
        if (x==len(list1)) or (y==len(list2)):
            break 

        #x pointer compare with y pointer
        if list1[x][0]==list2[y][0]:#if eq then check position
            list1_pos = list(map(int,list1[x][1].split(",")))#turn position into a list
            list2_pos = list(map(int,list2[y][1].split(",")))
            posx = 0#position pointers
            posy = 0
            pos_outputlist = ""
            while(1):#go through the positions
                if posx==len(list1_pos) or posy==len(list2_pos):
                    break
                if list1_pos[posx]==list2_pos[posy]-1:#if match always report the posy
                    pos_outputlist = pos_outputlist+","+str(list2_pos[posy])#so it can match with the next word
                    posx += 1
                    posy += 1
                elif list1_pos[posx]<list2_pos[posy]-1:
                    posx+= 1
                elif list1_pos[posx]>list2_pos[posy]-1:
                    posy+= 1
            #after above loop add pos_output to output
            if len(pos_outputlist)>1:
                outputlist.append((list1[x][0],pos_outputlist[1:]))#we don't want the first ',' 
            x += 1#move pointer
            y += 1
        elif list1[x][0]<list2[y][0]:#if one list is smaller then move it
            x += 1
        elif list1[x][0]>list2[y][0]:
            y += 1
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
    try:
        conn = sqlite3.connect(index_dir+'/table.db')
    except sqlite3.OperationalError:
        print ("database error")
        return

    #split query
    query = query.replace("("," ( ")
    query = query.replace(")"," ) ")
    query = query.lower().split()
    
    #get rid of the term querys first
    term_temp = []#list of word in a term query
    term_inside = False
    for i in range(len(query)):
        word = query[i]
        if term_inside:#if it is inside a term query
            if word[-1]=="'"or word[-1]=='"':#see if it is the end
                term_temp.append(word[:-1])#add to temp list with
                
                #do term_query and add list back to (origin)query
                for j in range(len(term_temp)):
                    c = conn.cursor()
                    c.execute("SELECT DISTINCT movie_id,position FROM searchIndex WHERE word='"+term_temp[j]+"' ORDER BY movie_id;")
                    if j == 0:#if it is the start then just fetch
                        term_output = c.fetchall()
                    else:#else do term_query with last output with new term
                        term_output = term_query(term_output,c.fetchall())
                query[i] = term_output

                term_inside=False#Not inside anymore
                term_temp= []#clear out temp list
            else:#if it is not the end
                term_temp.append(word)#then just add the word
                query[i]= None#remove word from (original)query
        else:#if it is not inside
            if word[0]=="'"or word[0]=='"':#see if it is the start
                term_inside= True#inside term query
                term_temp.append(word[1:])
                query[i]=None
            else: 
                continue#else just pass
        
    #now while loop til done
    i = 0 #<- pointer
    in_sub_query=False                  
    while(1):
        if query[i]==None:#clear out the filler objects
            query.pop(i)
        elif query[i]=="(":#trying to find the most inner (
            sub_query= []#clear out the list 
            in_sub_query = True
        elif query[i]==")":#end of a subquery and do stuff
            in_sub_query= False
            
        i += 1#next
    
    conn.close()
    
    print (sys.argv)
    print (query)
main()
