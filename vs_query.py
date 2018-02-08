import sys
import sqlite3
import math

def delete_dup(input_list):
    #sort and remove duplicates from a list
    input_list.sort()
    i = 0
    old = -1
    output_list = []
    while(i<len(input_list)):
        if input_list[i] != old:
            output_list.append(input_list[i])
            old = input_list[i]
        i += 1
       
    return output_list
    
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
            if idf >= 0.05:#if the term is too common just ignore it
                term_idf[term]=idf
                test_documents = test_documents+(df)
    #take all the duplicate out
    test_documents = delete_dup(test_documents)


    #calculate the td-idf weight for the query
    query_tfidf={}
    for term in terms:
        if term in term_idf:
            query_tf = 0
            for raw_term in raw_terms:
                if term == raw_term:
                    query_tf += 1
            query_tf = 1+math.log10(query_tf)
            query_tfidf[term] = query_tf*term_idf[term]
    
    #create dictionary with{'id':[score]}
    weight_output = {}
    length_output = {}
    for movie_id in test_documents:
        document_score = 0.0
        length = 0.0
        for term in term_idf:
            c=conn.cursor()
            c.execute("SELECT position FROM searchIndex WHERE word='"+term+"' AND movie_id ="+str(movie_id[0])+";")
            #there should be only one line(unique constraint)
            position_output = c.fetchone()
            if position_output is not None:#make sure there are things coming out
                list_pos = len(position_output[0].split(","))#turn position into a list,length is the word frequency
                tfidf_td = (1+math.log10(list_pos))*term_idf[term]#get weight t,d
                length+= tfidf_td #track length     
                tfidf_final = tfidf_td * query_tfidf[term]#get cosine score without normalization
                #calculate the weight and add it to the list
                document_score += tfidf_final
               
                
        weight_output[str(movie_id[0])]=document_score
        length_output[str(movie_id[0])]=math.sqrt(length) 
    #normalization
    #calculate length
    
    for movie_id in test_documents:
        weight_output[str(movie_id[0])] = weight_output[str(movie_id[0])]/length_output[str(movie_id[0])]   
    
    
    #get K biggest
    K_biggest = sorted(weight_output,key=weight_output.get,reverse=True)[:int(k)]   
    #output 
    for i in range(int(k)):
        if scores.upper()=='Y':
            try:
                print(K_biggest[i]+"\t"+str(weight_output[K_biggest[i]]))
            except:
                print("-")
        else:
            try:
                print(K_biggest[i])
            except:
                print("-")

    if len(K_biggest)== 0 :
        print("no output(search terms too general or K=0)")    
    

         
 
main()



















