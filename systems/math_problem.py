# -*- coding: utf-8 -*-
"""
Clase MathProblem - Generador de problemas matemáticos
"""

import random


class MathProblem:
    """Clase para generar y resolver problemas matemáticos donde se oculta la operación"""
    
    def __init__(self, num_range):
        self.num_range = num_range
        self.operation = None
        self.num1 = 0
        self.num2 = 0
        self.answer = 0
        self.generate(max_attempts=10)
    
    def generate(self, max_attempts=10):
        """Genera un nuevo problema matemático donde se muestra el resultado y se oculta la operación"""
        attempts = 0
        while attempts < max_attempts:
            operations = ["+", "-", "*", "/"]
            self.operation = random.choice(operations)
            
            if self.operation == "+":
                self.num1 = random.randint(self.num_range[0], self.num_range[1])
                self.num2 = random.randint(self.num_range[0], self.num_range[1])
                self.answer = self.num1 + self.num2
            
            elif self.operation == "-":
                # Asegurar que el resultado sea positivo
                self.num2 = random.randint(self.num_range[0], self.num_range[1])
                self.num1 = random.randint(self.num2, self.num_range[1])
                self.answer = self.num1 - self.num2
            
            elif self.operation == "*":
                # Limitar multiplicaciones para evitar números muy grandes
                max_val = min(self.num_range[1], 12)
                self.num1 = random.randint(self.num_range[0], max_val)
                self.num2 = random.randint(self.num_range[0], max_val)
                self.answer = self.num1 * self.num2
            
            elif self.operation == "/":
                # Generar división sin decimales
                self.num2 = random.randint(2, min(self.num_range[1], 12))
                quotient = random.randint(self.num_range[0], min(self.num_range[1], 10))
                self.num1 = self.num2 * quotient
                self.answer = quotient
            
            # Verificar que solo una operación sea correcta para esta combinación
            correct_ops = []
            if self.num1 + self.num2 == self.answer:
                correct_ops.append("+")
            if self.num1 - self.num2 == self.answer:
                correct_ops.append("-")
            if self.num1 * self.num2 == self.answer:
                correct_ops.append("*")
            if self.num2 != 0 and self.num1 / self.num2 == self.answer:
                correct_ops.append("/")
            
            # Si solo hay una solución, aceptar este problema
            if len(correct_ops) == 1:
                break
            
            attempts += 1
        
        # Si después de varios intentos aún hay múltiples soluciones, usar la primera
        if attempts >= max_attempts:
            # Asegurar que al menos la operación elegida sea correcta
            pass
    
    def check_answer(self, operation):
        """Verifica si la operación ingresada es correcta"""
        return operation == self.operation
    
    def get_text(self):
        """Retorna el texto del problema con la operación oculta"""
        return f"{self.num1} ? {self.num2} = {self.answer}"
