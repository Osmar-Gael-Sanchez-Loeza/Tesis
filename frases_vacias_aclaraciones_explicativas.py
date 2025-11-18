from limpiar_definiciones import sustraer
import re

def frases_vacias_aclaraciones_explicativas(content, titulo):
    # Contexto y Alcance
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(?i:{re.escape(titulo)}) empleado en la (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.,;]*puede tener diversos significados en el campo de [^.,;]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ee]s un concepto amplio que puede aplicarse a diferentes contextos y situaciones médicas, [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ee]n este contexto es subjetivo[^.]*\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()En el caso de la (?i:{re.escape(titulo)}), por ejemplo,))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)

    # Información Médica/Científica Detallada
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Síntomas( y diagnóstico)? de la|[Dd]iagnóstico de la|[Tt]erapia( y manejo)? de la|Causas y tipos de) (?i:{re.escape(titulo)})[.:]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^\n]*[Cc]omo [^\n]*cualquier procedimiento [^\n]*(no está exenta de riesgos|hay riesgos asociados con su uso)[^\n]+))(?=([ \n]|$))', rf'#', content)

    # Bloque complejo (Explicativa - Desglose)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(En ([^.,;]+, también juega un papel importante|el ámbito de la medicina, tiene múltiples aplicaciones y significados, dependiendo del contexto en el que se utilice)|Esta (amplia gama de usos reflej[oa] la diversidad y complejidad de la medicina como ciencia y práctico|es una definición general y, aunque es exacta, [^.]+)|Se usa (solo en contextos históricos|ampliamente también en el registro especializado)|Otro ámbito donde se emplea el término (?i:{re.escape(titulo)}) es [^.]+|No es habitual en [^.]+|[^.]+pero (no se usa|carece de validez en [^.]+)|(Presencia de una )?((?i:{re.escape(titulo)}) o)( (?i:{re.escape(titulo)}))?|Etiología y Factores de Riesgo|[Pp]rognóstico y profilaxis|A (pesar de sus numerosas ventajas, tiene algunas limitaciones|continuación, se abordan diversas aplicaciones y beneficios [^.]+))\.))(?=([ \n]|$))', rf'#', content)
    return content
