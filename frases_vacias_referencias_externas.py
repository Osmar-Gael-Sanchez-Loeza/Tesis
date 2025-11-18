def frases_vacias_referencias_externas(content):
    # Comparaciones directas y enlaces de sinonimia
    content = sustraer(rf'( +|\n *|^ *)((()términos (?i:{re.escape(titulo)}) y (?i:{re.escape(titulo)}) son))(?=([ \n]|$))', rf'# {titulo} son', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(?i:{re.escape(titulo)})( y (?i:{re.escape(titulo)}))?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Ver (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Término similar a (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Coloquial|Desuso):? igual a (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Su nombre común es (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)

    # Relaciones de pertenencia o definición relativa
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()De(l| l(a|os)) (?i:{re.escape(titulo)})s?( \(?o (?i:{re.escape(titulo)})\)?,?)? o relacionado con (él|ell[oa]s?)\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Relativo a la (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()El (?i:{re.escape(titulo)}) es el (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)

    # Punteros de confusión o contraposición
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(que )?[Nn]o debe confundirse con[^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Generalmente por contraposición a:? [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se usa con incidencia de manera laxo como si fuera sinónimo de: (?i:{re.escape(titulo)})(, la)?\.))(?=([ \n]|$))', rf'#', content)

    # Listados de denominaciones alternativas
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Tiene también otros muchos sinónimos [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()([Tt]ambién )?([Ss]e le conoce como|[Cc]onocida|([Hh]abitualmente )?[Dd]enominad[oa]|[Ss]e denomina)( también)? (?i:{re.escape(titulo)})( o (?i:{re.escape(titulo)}))?[.,]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Vv]éase también: [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Nombre del [^.]+\.))(?=([ \n]|$))', rf'#', content)

    # Tipos/Clasificaciones (Punteros)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]+ del tipo de (?i:{re.escape(titulo)}) XYZ[^.]+\.))(?=([ \n]|$))', rf'#', content)

    # Definiciones tautológicas de inicio
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ll]a (?i:{re.escape(titulo)})(,| es| designa) una (?i:{re.escape(titulo)}),))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()El (?i:{re.escape(titulo)}) (en [^. ]+) \(o (?i:{re.escape(titulo)})\)))(?=([ \n]|$))', re.sub(r'°(\d+)°', r'\\\1', rf'#\n~{titulo}~ °5°'), content)
    return content
