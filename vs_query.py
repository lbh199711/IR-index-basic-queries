import sys
import sqlite3
import math


def main():
    #connect to database
    if len(sys.argv)<5:
        print ("vs_query.py [index location] [k] [scores(Y/N)] [term_1] [term_2] ...")
        return
    else:#init
        index_dir = str(sys.argv[1])
        scores = sys.argv[3]
        k = sys.argv[2]
        terms= sys.argv[4:]  
  
    #connect database
    try:
        conn = sqlite3.connect(index_dir+'/table.db')
    except sqlite3.OperationalError:
        print ("database error")
        return
    
    #make the terms list unique
    terms.sort()
    old = " "
    i = 0
    while(i<len(terms)):
        if terms[i] == old:
            terms.pop(i)
            
        else:
            old = terms[i]
            i+=1         
    print (terms)   

    #tf-idf scheme for the term weights
    #N(# of documents in the collection):
    c = conn.cursor()#get all IDs 
    c.execute("SELECT DISTINCT movie_id FROM searchIndex;")
    total = len(c.fetchall())

    #calculate idf weight for each term
    term_idf = []
    for term in terms:
        #get idf
        c= conn.cursor()
        c.execute("SELECT DISTINCT movie_id FROM searchIndex WHERE word='"+term+"';")
        df = float(len(c.fetchall()))
        idf = 0
        if df!= 0: 
            idf = math.log10(total/df)
            term_idf.append([term,idf])

            
    print(term_idf)
main()
