defaultCaesarMove = 7
caesarMove = defaultCaesarMove
alphabet = 'abcdefghijklmnopqrstuvwxyz'
number = '0123456789'
initial = alphabet+number

def encrypt(string):    
    listInitial = list(initial)
    allMove = len(listInitial)
  
    listString = list(string)     
    for i in range(len(listString)) :
        tobe = listInitial.index(listString[i])
        en = (tobe + caesarMove) % allMove
        listString[i] = listInitial[en]
    
    return ''.join(listString)

def decrypt(string):
    listInitial = list(initial)
    allMove = len(listInitial)
    
    listString = list(string)  
    for i in range(len(listString)) :
        tobe = listInitial.index(listString[i])
        en = (tobe - caesarMove) % allMove
        listString[i] = listInitial[en]
        
    return ''.join(listString)