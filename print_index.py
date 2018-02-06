import sys
import sqlite3
def main():
    #connect to database
    if len(sys.argv) > 2:
        print ("invalid arguement")
        return 
    elif len(sys.argv)== 1:
        index_dir = "."
    else:
        index_dir = str(sys.argv[1])
    
    
    try:
        conn = sqlite3.connect(index_dir+'/table.db')
    except sqlite3.OperationalError:
        print ("database error")
        return

    c = conn.cursor()
    try:
        c.execute("SELECT * from searchIndex order by word,movie_id")
    except sqlite3.OperationalError:
        print("Table don't exist, run create_index.py first")
        return
    
    row = c.fetchone()
    old = ""
    word = row[0]
    z = 1
    while(1):
        z += 1
        movie_id = str(row[1])
        position = row[2].replace(",","").split(" ")

        

        if word != old:
            print (word,end="\t")
        print(movie_id,end=":")
        for i in range(len(position)):
            print(position[i],end="")
            if i != len(position)-1:
                print(",",end="")#if not at the end print ','
            
        

        #check next one
        row = c.fetchone()
        old = word
        #if next word is different then don't print ;
        if row is not None:
            word = row[0]
        else:
            break
        if word == old:
            print(";",end="")
        else:
            print("\n",end="")
         
    print("\n",end="")


main()
