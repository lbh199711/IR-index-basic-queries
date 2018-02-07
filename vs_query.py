import sys
import sqlite3
import math
def delete_dup(input_list):
    #sort and remove duplicates from a list
    input_list.sort()
    i = 0
    old = -1
    while(i<len(input_list)):
        if input_list[i] == old:
            input_list.pop(i)
        else:
            old = input_list[i]
            i += 1
    return input_list
    
def main():
    #connect to database
    if len(sys.argv)<5:
        print ("vs_query.py [index location] [k] [scores(Y/N)] [term_1] [term_2] ...")
        return
    else:#init
        index_dir = str(sys.argv[1])
        scores = sys.argv[3]
        k = sys.argv[2]
        raw_terms= sys.argv[4:]  
  
    #connect database
    try:
        conn = sqlite3.connect(index_dir+'/table.db')
    except sqlite3.OperationalError:
        print ("database error")
        return
    
    #make the terms list unique
    terms = delete_dup(raw_terms)  

    #tf-idf scheme for the term weights
    #N(# of documents in the collection):
    c = conn.cursor()#get all IDs 
    c.execute("SELECT DISTINCT movie_id FROM searchIndex;")
    total = len(c.fetchall())
    

    #calculate idf weight for each term
    test_documents=[]#this contains all the documents that contains any terms
    term_idf = {}
    for term in terms:
        #get idf
        c= conn.cursor()
        c.execute("SELECT DISTINCT movie_id FROM searchIndex WHERE word='"+term+"';")
        df = c.fetchall()#contains all the movie_id with term
        
        idf = 0
        if len(df)!= 0: 
            idf = math.log10(total/float(len(df)))
            #print([term,idf]) #test only
            if idf >= 0.05:#if the term is too common just ignore it
                term_idf[term]=idf
                test_documents = test_documents+(df)
    #take all the duplicate out
    test_documents = delete_dup(test_documents)
    
    print("all related documents",test_documents)
    print("term_idf",term_idf)
    
    #create dictionary with{'id':[weight matrix column]}
    weight_matrix = {}
    for movie_id in test_documents:
        matrix_column = []
        for term in terms:
            c=conn.cursor()
            c.execute("SELECT position FROM searchIndex WHERE word='"+term+"' AND movie_id ="+str(movie_id[0])+";")
            #there should be only one line(unique constraint)
            position_output = c.fetchone()
            if position_output is not None:#make sure there are things coming out
                list_pos = len(position_output[0].split(","))#turn position into a list,length is the word frequency
                #calculate the weight and add it to the column list
                matrix_column.append((1+math.log10(list_pos))*term_idf[term])
                #print ("list_pos:",list_pos)#for testing 
            else: #else just return 0
                matrix_column.append(0)
        weight_matrix[str(movie_id[0])]=matrix_column
        
    print ("weight_matrix",weight_matrix)
                        
            

         
 
main()



















