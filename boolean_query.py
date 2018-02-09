import sys
import sqlite3
from utils import *

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
        

def condition_query(query_list,conn):
    #get a list of word and check the length then do query
    output = []
    if len(query_list)==3:#this is boolean query
        #this is the word/list to query for,middle one is op
        for i in [0,2]:
            if type(query_list[i]) == list:
                output.append(query_list[i])
            else: 
                c = conn.cursor()
                c.execute("SELECT DISTINCT movie_id FROM searchIndex WHERE word='"+query_list[i]+"';")
                output.append(c.fetchall())
        op = query_list[1]
        output = boolean_query(op,output[0],output[1])
    elif len(query_list)==1:#this is to just find the term
        if type(query_list[0])==list:
            output=query_list[0]
        else:
            c = conn.cursor()
            c.execute("SELECT DISTINCT movie_id FROM searchIndex WHERE word='"+query_list[0]+"';")
            output=c.fetchall()
    else:#error
        return -1
    return output
         

	
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
    for i in range(len(query)):
        if query[i][0]=='"' or query[i][0]=="'" or query[i][-1]=='"' or query[i][-1]=="'":
            continue 
        if query[i] != "(" and query[i] != ")":
            query[i] = clean_word(query[i])

    #get rid of the term querys first
    term_temp = []#list of word in a term query
    term_inside = False

    for i in range(len(query)):
        word = query[i]
        if word == '' or word == ' ' or word is None:#if word is empty
            continue
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
    if query[0] != '(' or query[-1]!=')':
        query.insert(0,'(')
        query.append(')')
    while(1):

        if query[i] == -1:
            "invalid query"
            break

        if query[i]==None or query[i]==' ' or query[i] == '':#clear out the filler objects
            query.pop(i)
            i-= 1
        elif query[i]=="(":#trying to find the most inner (
            sub_query= []#clear out the list 
            in_sub_query = True
        elif query[i]==")":#end of a subquery and do stuff
            in_sub_query= False
            query[i] = condition_query(sub_query,conn)

            for j in range(len(sub_query)+1):
                i -= 1#go back
                query[i] = None#remove from the query
            #go one back and check if it is NOT
            if query[i-1] == 'not' or query[i-1] == 'NOT':
                query[i-1] = None
                query[i+len(sub_query)+1] = not_query(query[i+len(sub_query)+1],conn)#do not query 
            sub_query=[]#clear out the list
            i = 0 #go from the beginning
            continue
        elif in_sub_query:#if in subquery just add it 
            sub_query.append(query[i])       
            
        i += 1#next

        #check end condition
        if len(query)==1:
            if query[0] == -1:
                print ("invalid input")
            break
        elif i == len(query):
            i = 0#loop around
            if in_sub_query:#if it go to the end but didn't finish sub_query
                print("invalid input")
                return -1
        
    conn.close()
    
    for i in query[0]:
        print (i[0])

 
main()
