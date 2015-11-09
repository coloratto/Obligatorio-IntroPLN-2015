import ast
import re
import nltk
from nltk.corpus import stopwords

def diccionarioElementosSubjetivos(archivoElementosSubjetivos):
    positivosRaw = open(archivoElementosSubjetivos).read()
    positivosRaw = positivosRaw.replace(u'\ufeff', '')
    positivosRaw = positivosRaw.replace('elementoSubjetivo','')
    positivosRaw = positivosRaw.strip()
    regex = re.compile(r"%.*\n", re.IGNORECASE | re.MULTILINE)
    positivosRaw = re.sub(regex,'',positivosRaw)
    regex = re.compile(r"\)(.[^\)\(]|\s[^\)\(])*\(",re.IGNORECASE | re.MULTILINE)
    positivosRaw = re.sub(regex,').(',positivosRaw)
    arregloPositivos = positivosRaw.split('.')
    #Saco punto final
    tope = len(arregloPositivos) -1
    arregloPositivos.pop(tope)
    tuplas = ()
    #Voy a tener un diccionario palabra:valor
    for tupla in arregloPositivos:
        #print(ast.literal_eval(tupla))
        tuplas = tuplas + (ast.literal_eval(tupla.strip()),)
    
    #print (tuplas)
    diccionario = dict(tuplas)
    return diccionario

def depurar_comentarios (comentarios_peliculas):
# En primera instancia se quitan los espacios en blanco al final y al principio (espacio, tab, retorno de carro, salto de linea)
# Se recorren los datos por filas
    for i in range(0,len(comentarios_peliculas)):
    # Se accede a la fila i columna 0 (es decir el valor comentario) y se lo modifica por el mismo modificado
        comentarios_peliculas.ix[i,0] = comentarios_peliculas.ix[i,0].strip(' \t\n\r')

    # Luego se quitan las etiquetas html de los comentarios
    # Se recorren los datos por filas
    for i in range(0,len(comentarios_peliculas)):
        
        # Se obtiene el largo del comentario i
        length = len(comentarios_peliculas.ix[i,0])
        new_length = 0
        
        # Expresión regular para matchear etiquetas html
        reg = r'<\/?\w+((\s+\w+(\s*=\s*(?:".*?"|\'.*?\'|[^\'">\s]+))?)+\s*|\s*)\/?>'
        
        # Se aplica la expresión regular al comentario mientras cambien los largos
        while new_length != length:
            
            # Se cambia el comentario por el mismo sin etiquetas html
            comentarios_peliculas.ix[i,0] = re.sub(reg, "", comentarios_peliculas.ix[i,0])
            new_length = len(comentarios_peliculas.ix[i,0])        
    return comentarios_peliculas

def convert_to_list(comentarios_peliculas):
    subset = comentarios_peliculas[['ComTexto','Calificación']]
    return [tuple(x) for x in subset.values]

# Funcion que dado un numero entre (1 y 5) devuelve la clasificación asociada
# En este lab si es 5 o 4 -> positivo; 3 -> neutro; 1 o 0 -> negativo
def codificarClasificacion(num):
    if(num > 3):
        return "pos"
    elif(num == 3):
        return "neu"
    else:
        return "neg"    

def tokenizar_nltk(datos):
    # Retorna una lista de tuplas. 
    # Cada tupla posee un diccionario (dict) palabra-frecuencia del comentario y la clasificación asociada
    # En otras palabras [(dict1, clasificacion1),(dict2, clasificacion2), ... ]

    listaTuplas = []

    # Se recorren los comentarios y para cada uno de ellos se tokeniza con nltk
    for i in range(0,len(datos)):
        
        # Se crea el diccionario asociado al comentario
        dic = {}
        
        # Por cada palabra retornada de la tokenizacion del comentario

        for palabra in nltk.word_tokenize(datos[i][0]):
            
            # Si la palabra está en el diccionario del comentario, se aumenta la frecuencia
            # En caso contrario se la pone en el diccionario con valor 1
            if(palabra.lower() in dic): 
                dic[palabra.lower()] = dic[palabra.lower()] + 1
            else:
                dic[palabra.lower()] = 1
                
        # Luego de tokenizado el comentario, se agrega una tupla a la lista que contendrá
        # el diccionario de frecuencias y la clasificaion asociada al comentario
        listaTuplas.insert(i,(dic,codificarClasificacion(datos[i][1])))
    return listaTuplas

def palabras_mas_frecuentes (n,datos):
    cantPalabras = 0
    palabras = {}
    for i in range(0, len(datos)):
        for palabra in nltk.word_tokenize(datos[i][0]):
            if(palabra.lower() in palabras): 
                    palabras[palabra.lower()] = palabras[palabra.lower()] + 1
            else:
                    palabras[palabra.lower()] = 1

    palabrasOrdenadasPorFrecuencia = sorted(palabras, key=palabras.get, reverse=True)
	
    if(n==-1):
        return palabrasOrdenadasPorFrecuencia
    else:
        return palabrasOrdenadasPorFrecuencia[:n]  

def filtrar_palabras(datos, n):
    filtroSW = []
    filtroAC = []

    dominio_cine_peliculas = open('terminosNoValorativosAmbitoCine.txt').read()
    palabras_f = palabras_mas_frecuentes(n,datos)
    nltk_stopwords = stopwords.words('spanish')
    datos_train_frec = []

    #Aplico distintos filtros a las palabras de los comentarios
    for i in range(0,len(datos)):
        #elimino stopwords
        palabras_frecuentes = [w for w in nltk.word_tokenize(datos[i][0]) if w in palabras_f]
        filtroSW = [w for w in palabras_frecuentes if not w in nltk_stopwords]
        filtroAC = [w for w in filtroSW if not w in dominio_cine_peliculas]
        datos_train_frec.insert(i,(" ".join(filtroAC),datos[i][1]))
    return datos_train_frec