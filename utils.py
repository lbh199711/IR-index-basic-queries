#little functions needed across all 



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
    

def clean_word(word):
    #clean all the unnessary punctuation from the word
    punctuation = [',','.','/','?','!',"'",'"',':',';','*','(',')','[',']','-','–']
    for i in punctuation:
        try:
            word = word.replace(i,'')
        except:
            print ("clean_word error:",word)
            continue
        
    word = word.lower()
    if len(word)>=4:
    #take out s and es in the end
        if word[-2:] == 'es':
            word = word[:-2]
        elif word[-2:]=='ss':
            pass
        elif word[-1] == 's':
            word = word[:-1]
        

    return word
