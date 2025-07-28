import ast
import keyword
import re

class ComplejidadVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_nivel_bucle = 0
        self.nivel_actual_bucle = 0
        self.recursion = set()
        self.funciones = set()
        self.llamadas = []

    def visit_FunctionDef(self, node):
        self.funciones.add(node.name)
        self.nivel_actual_bucle = 0
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.nivel_actual_bucle += 1
        if self.nivel_actual_bucle > self.max_nivel_bucle:
            self.max_nivel_bucle = self.nivel_actual_bucle
        self.generic_visit(node)
        self.nivel_actual_bucle -= 1
    
    def visit_While(self, node):
        self.nivel_actual_bucle += 1
        if self.nivel_actual_bucle > self.max_nivel_bucle:
            self.max_nivel_bucle = self.nivel_actual_bucle
        self.generic_visit(node)
        self.nivel_actual_bucle -= 1

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.llamadas.append(node.func.id)
        self.generic_visit(node)

    def report(self):
        recursiva = any(f in self.llamadas for f in self.funciones)
        if recursiva:
            self.recursion = set(f for f in self.funciones if f in self.llamadas)

        print(f"\nNivel máximo de bucles anidados: {self.max_nivel_bucle}")
        if self.recursion:
            print(f"¡Recursión detectada en: {', '.join(self.recursion)}!")
        if self.recursion:
            print("Complejidad probable: Exponencial o peor (¡recursión!)")
        elif self.max_nivel_bucle == 0:
            print("Complejidad probable: O(1) o O(n) (sin bucles anidados)")
        elif self.max_nivel_bucle == 1:
            print("Complejidad probable: O(n)")
        elif self.max_nivel_bucle == 2:
            print("Complejidad probable: O(n^2)")
        else:
            print(f"Complejidad probable: O(n^{self.max_nivel_bucle})")

# Nueva clase para chequear nombres inválidos
class ChequeosExtra(ast.NodeVisitor):
    def __init__(self):
        self.nombres_invalidos = set()
        self.nombres = set()
        self.nombres_funcion = set()
        self.nombres_clase = set()
        self.reservadas = set(keyword.kwlist)
        self.regex_valido = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")  # Identificador Python válido

    def visit_Name(self, node):
        self.nombres.add(node.id)
        if not self.regex_valido.match(node.id) or node.id in self.reservadas:
            self.nombres_invalidos.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.nombres_funcion.add(node.name)
        if not self.regex_valido.match(node.name) or node.name in self.reservadas:
            self.nombres_invalidos.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.nombres_clase.add(node.name)
        if not self.regex_valido.match(node.name) or node.name in self.reservadas:
            self.nombres_invalidos.add(node.name)
        self.generic_visit(node)

    def visit_arg(self, node):
        if not self.regex_valido.match(node.arg) or node.arg in self.reservadas:
            self.nombres_invalidos.add(node.arg)
        self.generic_visit(node)

# Nueva clase para chequear módulos prohibidos
class ChequeosModulos(ast.NodeVisitor):
    def __init__(self, prohibidos=None):
        self.prohibidos = set(prohibidos) if prohibidos else {"os", "sys", "subprocess"}
        self.importados_prohibidos = set()

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.prohibidos:
                self.importados_prohibidos.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in self.prohibidos:
            self.importados_prohibidos.add(node.module)
        self.generic_visit(node)

# Script principal
if __name__ == "__main__":
    print("Pegá tu código Python acá (o usá el ejemplo):\n")
    codigo = """
def suma_lista(arr):
    total = 0
    for x in arr:
        total += x
    return total

def matriz_suma(mat):
    s = 0
    for fila in mat:
        for val in fila:
            s += val
    return s

def factorial(n):
    if n == 0:
        return 1   # Faltó el ':', esto tira error de sintaxis
    return n * factorial(n-1)
"""
    # --- Verifica sintaxis ---
    try:
        tree = ast.parse(codigo)
    except SyntaxError as e:
        print("¡Error de sintaxis detectado!")
        print(f"Tipo de error: {e.msg}")
        print(f"Línea: {e.lineno}, Columna: {e.offset}")
        print(f"Texto problemático: {e.text.strip() if e.text else ''}")
        exit(1)
    
    # Chequeo de nombres
    nombres_checker = ChequeosExtra()
    nombres_checker.visit(tree)
    if nombres_checker.nombres_invalidos:
        print("\n¡Atención! Nombres de variables o funciones inválidos encontrados:")
        for n in nombres_checker.nombres_invalidos:
            print("   -", n)
    
    # Chequeo de módulos prohibidos
    modulos_checker = ChequeosModulos(prohibidos={"os", "subprocess", "sys"})
    modulos_checker.visit(tree)
    if modulos_checker.importados_prohibidos:
        print("\n¡Atención! Se usaron módulos prohibidos:")
        for m in modulos_checker.importados_prohibidos:
            print("   -", m)
    
    # Análisis de complejidad
    visitor = ComplejidadVisitor()
    visitor.visit(tree)
    visitor.report()
