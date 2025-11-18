from limpiar_definiciones import sustraer
import re

def frases_vacias_aclaraciones_linguisticas(content, titulo):
    # Etimología y Origen
    content = sustraer(rf'( +|\n *|^ *)((()\(del inglés, [^.)]+\)[.,;]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Solo admisible como vocablo latino\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()En latin la palabra (?i:{re.escape(titulo)}) significa (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Fue originalmente voz coloquial, pero se usa ampliamente también en el registro especializado\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Recibió el nombre por [^.]+\.))(?=([ \n]|$))', rf'#', content)

    # Siglas y Abreviaturas
    content = sustraer(rf'( +|\n *|^ *)((()[^. ]+ corresponde a las siglas inglesas de [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'( +|\n *|^ *)((()\([^.,;:()]+, por sus siglas en inglés\),))(?=([ \n]|$))', rf'#,', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Suele abreviarse a (?i:{re.escape(titulo)}) (o, más frecuentemente, (?i:{re.escape(titulo)})|en sus formas compuestas:)))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()En forma siglada,[^.]*(?i:{re.escape(titulo)}) que (?i:{re.escape(titulo)});([^.]+\.)?))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Aa]breviatura (de (?i:{re.escape(titulo)})([^.;]+)?|ingles de [^.]+ \([^.)]*(?i:{re.escape(titulo)})\))\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()([Cc]on incidencia|[Ee]n ocasiones) abreviado a (?i:{re.escape(titulo)})(, (sustantivo [^. ]+|especialmente en [^. ]+))?[.,;]))(?=([ \n]|$))', rf'#', content)

    # Ortografía, Pronunciación y Variantes
    content = sustraer(rf'( +|\n *|^ *)((()como (?i:{re.escape(titulo)}) \(?(símbolo|o) ((?i:{re.escape(titulo)}))\)?,))(?=([ \n]|$))', rf'# {titulo},', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Sinónimo(s:( Coloquial:)?| de) (?i:{re.escape(titulo)})(, a)?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se escribe )?[Ee]n cursiva( y [^.]+)?(, por tratarse de un[^.,;]+)?[.;]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(La x basal |[^.]+, )?([Ss]e|La) pronuncia(ción)? ((original aproximada es )?/[^.]+|como (se escribe|s))\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(, +|; +|\. +|\n *|^ *)((()[Vv]ariante (en desuso|gráfica desprestigiada[^.,;]*)\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se usa mucho la acentuación [^.,;]+|La acentuación (llana|etimológica)[^.;]+)[.;]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()La primera [^.,;]+ es mudo\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()es muy frecuente llamarlo simplemente (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)

    # Gramática (Género, Número, Adjetivación)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*(Generalmente|Con incidencia|[Ss]e usa también) en plural( con el mismo significado[^.]*)?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Como nombre propio, no suele ir precedido de artículo; si lo precisa, es masculino\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Casi no se usa en plural, que es dudoso en español\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Pp]lural invariable:? (\()?l[oa]s (?i:{re.escape(titulo)})(\))?[^.]*\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Como adjetivo, es invariable en cuanto a|(En propiedad [^.]+|[^.]*[Ss]e usa (también|mucho más)|(Es incorrecto |En )?[Ss]u uso( etimológico)?|Antiguamente se usó también|[^.]+ pero en español se usa solo) (con|de)) (género|identidad sexual) [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Su adjetivo es [^.,;]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Dado que se trata de un sustantivo abstracto [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Con frecuencia en plural, como nombre de grupo medicamentoso\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Es sustantivo masculino también cuando hace referencia a personas de sexo [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Es sustantivo formado de modo irregular[^.]+\.))(?=([ \n]|$))', rf'#', content)

    # Normativa, Uso, Anglicismos y Recomendaciones
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Por influencia del inglés, )?[Ss]e usa (más|mucho) la forma (extendida|siglada inglesa) (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se recomienda precaución con este término, que se usa con significados muy distintos\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Puede suscitar rechazo por considerarse ((extranjerismo|redundante|anglicismo|término impropio|erróneo|calco)[^.]*|híbrido etimológico(\. No obstante, su uso es abrumador)?)\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()La RANME (desaconseja (su|el) uso( de este término)? (por considerarlo [^.]+|de extranjerismos innecesarios)|es partidaria de sustituir los extranjerismos crudos por alguno de sus sinónimos en español o equivalentes castellanizados|(recomienda|aconseja) precaución con el uso [^.;]+)\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()La terminología es sumamente confusa y varía mucho de una escuela a otra;))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Es en propiedad más correcto, pero de uso minoritario\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Error frecuente por influencia del inglés [^.(]+( \([^.)]+\))?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Es anglicismo incorrectamente formado|La transliteración (?i:{re.escape(titulo)}) es incorrecta) en español, pero de uso abrumador( por influencia del inglés)?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Es|La) forma (castellanizada (es|del inglés): )?((?i:{re.escape(titulo)}), )?pero casi no se usa\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se usa (más el anglicismo (?i:{re.escape(titulo)})|frecuentemente con anteposición del[^.,;]+)\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Localismo de uso restringido a algunas zonas de España; no se usa en América\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Ninguna de las traducciones propuestas ha logrado hasta ahora imponerse en la práctic[oa]\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()Las variantes que incorporan el [^.]+ suscitan rechazo entre [^.]+\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Es]s (error|equivocación) frecuente el uso [^\n]+))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se desaconseja )?[Ee]n los textos (modernos|actuales)(;|, se considera anglicismo\.)))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.,;]*[Ll]a RAE[^.]*\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()([^.]*[Ss]e usa (((mucho|muchísimo) )?más[^.;]*|de forma abrumadora|sobre todo|prácticamente de forma exclusiva) en [^.]+|Por semejanza de campo temático, existe riesgo importante de[^.]+|Las [^.;]+|[^.,]*[Ee]n (esta|todas sus)) acepci(ón|ones)[^.]*\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ll]a preferencia (por|entre) ((?i:{re.escape(titulo)})(, (?i:{re.escape(titulo)}))* [yo] [^.]+|una? (sinónimo|variante) u otr[oa]) depende( del contexto)?(( y)? de[^.]+)?[.;]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ss]u uso es abrumador\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(([Ll]as? (formas?|respectivas variantes con) [^.;]+ )?([Ee]s|[Ss]on|[Ss]e considera) (incorrectas?|impropias)|[Ss]e desaconsejan?)([^.]+)?\.))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Pp]uede verse (también ([^.,;]+, variante en desuso|(escrito )?en inglés [^.;]+|(?i:{re.escape(titulo)})( \(?[yo] (?i:{re.escape(titulo)})\)?)?(,? \(?variante [^.,;]+)?(, que es anglicismo sintáctico, o)?|[^.,;]*(, que se considera latinismo innecesario|con la grafía [^.,;]+))|en yuxtaposición [^.;]+:[^.;]+)[.;]))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Tiene un marcado polimorfismo|[^.]+no son sinónimos estrictos[^.]+|[^.]+más restringido, referido al[^.]+|En propiedad[^.]+que es impropio y confuso|[^.]*[Ss]e deriva del griego[^.]+que significa[^.]+|Prácticamente no se usa en singular|Se usa muy poco en [^.]+)\.))(?=([ \n]|$))', rf'#', content)

    # Bloque complejo (Linguistica - Desglose)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()((Se confunde a menudo con el:)[^.,;]+|(La yuxtaposición de sustantivos se considera anglicismo sintáctico)|(el artículo se consignan solo algunos de los muchos sinónimos arcaicos [^.]+|España, [^.]+)|(debe evitarse en el registro escrito)|(puede verse utilizado tanto en un sentido como en otro|también variantes asimismo en desuso)|(Localismo de uso en [^.]+)|(Término impreciso, [^.,;]+)|(se usó de forma preferente en la primera) acepción[^.]*)\.))(?=([ \n]|$))', rf'#', content)
    return content
