import sys
import os
import sqlite3
from utils import *
    
def create_index(pathname,name,conn):
    #go through the file and input every word into db
    fp = open(pathname,'r')
    name = name.split("_")
    movie_id = name[1]
    i = 0
    file_index = {}
    for line in fp:

        text = line.split()
        
        for word in text:
            word = clean_word(word)
            if word == "":
                continue
            try:
                file_index[word].append(i)
            except KeyError:
                file_index[word] = [i]
            i += 1
    for word in file_index:
        #input into database
        c = conn.cursor()
        position = str(file_index[word])[1:-1]#list tsqlo string to store in db
        query = 'INSERT INTO searchIndex VALUES("'+word+'",'+str(movie_id)+',"'+position+'")'
        try:#if table already exist then pass
            c.execute(query)
        except sqlite3.IntegrityError:
            continue
    conn.commit()

         
			
	
	
def main():
    #init+check argument
    if len(sys.argv) > 2:
        print ("invalid arguement")
        return 
    elif len(sys.argv)== 1:
        index_dir = "."
    else:
        index_dir = str(sys.argv[1])

    #load file
    try:
        filename_list = os.listdir(index_dir)
    except: 
        print ("error when loading directory")
        return
	
    #create SQL table
    conn = sqlite3.connect('table.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS searchIndex(word text, movie_id integer,position text, PRIMARY KEY (word,movie_id))")
    conn.commit()


    filenum = 0
    for filename in filename_list:
        if filename[-4:] != ".txt":
            continue
        #add path to filename
        pathname = index_dir+"/"+filename
        #call function to index the file
        create_index(pathname,filename,conn)
        filenum += 1
        print(filenum,"done")
        
    
    #create index for the table so it's faster
    c = conn.cursor()
    try:#if index already exist then pass
        c.execute("CREATE INDEX word_idx ON searchIndex(word,movie_id);")
    except sqlite3.OperationalError:
        pass
        
    conn.close()
main()
