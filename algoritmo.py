import re
from collections import defaultdict

# Función para leer la gramática desde un archivo
def leer_gramatica(archivo):
    with open(archivo, 'r') as f:
        gramatica = {}
        for linea in f:
            # Separa la cabeza de la producción del cuerpo
            cabeza, cuerpo = linea.split('::=')
            cabeza = cabeza.strip()
            # Divide el cuerpo por '|', es decir, las diferentes alternativas
            producciones = [produccion.strip().split() for produccion in cuerpo.split('|')]
            gramatica[cabeza] = producciones
    return gramatica

# Función para calcular el conjunto de primeros (FIRST)
def calcular_primeros(gramatica):
    primeros = defaultdict(set)

    def primeros_de_simbolo(simbolo):
        if simbolo not in gramatica:  # Es un terminal
            return {simbolo}
        if simbolo in primeros and primeros[simbolo]:  # Ya calculado
            return primeros[simbolo]
        
        for produccion in gramatica[simbolo]:
            for s in produccion:
                simbolos = primeros_de_simbolo(s)
                primeros[simbolo].update(simbolos - {'ε'})
                if 'ε' not in simbolos:  # Si ε no está en el conjunto de primeros, paramos
                    break
            else:
                primeros[simbolo].add('ε')
        return primeros[simbolo]

    # Calcular primeros para todos los símbolos
    for simbolo in gramatica:
        primeros_de_simbolo(simbolo)
    
    return dict(primeros)

# Función para calcular el conjunto de siguientes (FOLLOW)
def calcular_siguientes(gramatica, primeros):
    siguientes = defaultdict(set)
    start_symbol = next(iter(gramatica))  # El primer símbolo no terminal
    siguientes[start_symbol].add('$')  # Símbolo de fin de cadena

    def agregar_siguientes(simbolo, produccion):
        for i, s in enumerate(produccion):
            if s not in gramatica:  # Si es un terminal, lo ignoramos
                continue
            if i + 1 < len(produccion):
                siguientes[s].update(primeros[produccion[i+1]] - {'ε'})
                if 'ε' in primeros[produccion[i+1]]:
                    siguientes[s].update(siguientes[simbolo])
            else:
                siguientes[s].update(siguientes[simbolo])

    # Iterar hasta que no se actualicen más los conjuntos de siguientes
    cambian = True
    while cambian:
        cambian = False
        for cabeza, producciones in gramatica.items():
            for produccion in producciones:
                tamaño_antes = sum(len(s) for s in siguientes.values())
                agregar_siguientes(cabeza, produccion)
                tamaño_despues = sum(len(s) for s in siguientes.values())
                if tamaño_despues > tamaño_antes:
                    cambian = True
    
    return dict(siguientes)

# Función para calcular el conjunto de predicción (PREDICT)
def calcular_prediccion(gramatica, primeros, siguientes):
    prediccion = defaultdict(set)

    for cabeza, producciones in gramatica.items():
        for produccion in producciones:
            conjunto_prediccion = set()
            for s in produccion:
                if s in primeros:  # Si 's' es un no terminal
                    conjunto_prediccion.update(primeros[s] - {'ε'})
                else:  # Si 's' es un terminal
                    conjunto_prediccion.add(s)
                    break  # Si es terminal, no se sigue a otro símbolo
                if 'ε' not in primeros[s]:
                    break
            else:
                conjunto_prediccion.update(siguientes[cabeza])
            prediccion[(cabeza, tuple(produccion))] = conjunto_prediccion

    return dict(prediccion)


# Función principal
def analizar_gramatica(archivo):
    gramatica = leer_gramatica(archivo)
    primeros = calcular_primeros(gramatica)
    siguientes = calcular_siguientes(gramatica, primeros)
    prediccion = calcular_prediccion(gramatica, primeros, siguientes)

    print("Conjuntos de primeros (FIRST):")
    for nt, conjunto in primeros.items():
        print(f"{nt}: {conjunto}")
    
    print("\nConjuntos de siguientes (FOLLOW):")
    for nt, conjunto in siguientes.items():
        print(f"{nt}: {conjunto}")

    print("\nConjuntos de predicción (PREDICT):")
    for (nt, produccion), conjunto in prediccion.items():
        print(f"{nt} -> {' '.join(produccion)}: {conjunto}")

# Ejemplo de uso
if __name__ == "__main__":
    archivo_gramatica = 'gramatica.txt'  # Especifica el nombre de tu archivo de gramática
    analizar_gramatica(archivo_gramatica)

