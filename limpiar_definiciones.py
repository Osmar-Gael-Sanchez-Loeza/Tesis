import requests
import json
import os
import re

import nltk
from nltk.stem import SnowballStemmer
try:
    nltk.data.find('stemmers/snowball_spanish')
except LookupError:
    nltk.download('snowball_data')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def tokenizar(texto):
    p = r'[][_.,·:;¡!¿?<>=/^*-]+'
    definicion = ' ' + texto.lower() + ' '

    for i in range(len(definicion)):
        if definicion[i] == '(':
            cont = 1
            j = i + 1

            while cont:
                if j == len(definicion):
                    j -= 1
                    break
                if definicion[j] == '(':
                    cont += 1
                elif definicion[j] == ')':
                    cont -= 1
                j += 1

            if re.search(r'[-}/\w]', definicion[i-1]):
                if definicion[i:j].count(' ') < 2:
                    definicion = definicion[:i] + definicion[i:j].replace(' ', '_') + definicion[j:]
                else:
                    definicion = definicion[:i] + ' ' + definicion[i+1:j-1] + ' ' + definicion[j:]
            elif not re.search(r'[/\w^]', definicion[j]) or definicion[i:j].count(' '):
                definicion = definicion[:i] + ' ' + definicion[i+1:j-1] + ' ' + definicion[j:]
                
    return re.sub(rf' +{p} +|{p} +{p}|{p} +| +{p}|  +', r' ', definicion).strip()

representaciones = {
    '00': ['', ''],
    '01': ['', 'primera'],
    '02': ['dos', 'segunda', 'medios'],
    '03': ['tres', 'tercera', 'tercios'],
    '04': ['cuatro', 'cuarta', 'cuartos'],
    '05': ['cinco', 'quinta', 'quintos'],
    '06': ['seis', 'sexta', 'sextos'],
    '07': ['siete', 'séptima', 'séptimos'],
    '08': ['ocho', 'octava', 'octavos'],
    '09': ['nueve', 'novena', 'novenos'],
    '10': ['diez', 'décima'],
    '11': ['once', 'undécima'],
    '12': ['doce', 'duodécima'],
    '13': ['trece', 'decimotercera'],
    '14': ['catorce', 'decimocuarta'],
    '15': ['quince', 'decimoquinta'],
    '16': ['dieciséis', 'decimosexta'],
    '17': ['diecisiete', 'decimoséptima'],
    '18': ['dieciocho', 'decimoctava'],
    '19': ['diecinueve', 'decimonovena'],
    '20': ['veinte', 'vigésima'],
    '22': ['veintidós'],
    '23': ['veintitrés'],
    '24': ['veinticuatro'],
    '25': ['veinticinco'],
    '26': ['veintiséis'],
    '27': ['veintisiete'],
    '28': ['veintiocho'],
    '29': ['veintinueve'],
    '30': ['treinta', 'trigésima'],
    '40': ['cuarenta', 'cuadragésima'],
    '50': ['cincuenta', 'quincuagésima'],
    '60': ['sesenta', 'sexagésima'],
    '70': ['setenta', 'septuagésima'],
    '80': ['ochenta', 'octogésima'],
    '90': ['noventa', 'nonagésima'],
    '000': ['', ''],
    '100': ['ciento', 'centésima'],
    '200': ['doscientos', 'ducentésima'],
    '300': ['trescientos', 'tricentésima'],
    '400': ['cuatrocientos', 'cuadringentésima'],
    '500': ['quinientos', 'quingentésima'],
    '600': ['seiscientos', 'sexcentésima'],
    '700': ['setecientos', 'septingentésima'],
    '800': ['ochocientos', 'octingentésima'],
    '900': ['novecientos', 'noningentésima'],
    1: ['décimas'],
    2: ['centésimas'],
    3: ['milésimas'],
    4: ['diezmilésimas'],
    5: ['cienmilésimas'],
    6: ['millonésimas'],
    7: ['diezmillonésimas'],
    8: ['cienmillonésimas'],
    9: ['milmillonésimas'],
    'I': [1],
    'V': [5],
    'X': [10],
    'L': [50],
    'C': [100],
    'D': [500],
    'M': [1000]
}

ajustes = {
    '01': ['uno', 'un', 'un'],
    '21': ['veintiuno', 'veintiún', 'veintiún'],
    '_': ['', 'mil', 'millones']
}

def representacionNumerica(valorNumerico):
    representacion = ''
    if valorNumerico[0] == '-':
        representacion = 'menos '
        valorNumerico = valorNumerico[1:].strip()
    valorNumerico2 = valorNumerico
    while True:
        parte = valorNumerico.split(',', 1)[0].replace('.', '').zfill(9)
        if parte == '000000000':
            completo = 'cero'
        else:
            completo = ''
            for i in range(3):
                frac = parte[-3:]
                parte = parte[:-3]
                if frac == '000':
                    continue
                if frac == '100':
                    x = 'cien'
                else:
                    x = representaciones[frac[0] + '00'][0]
                    if frac[1] < '3':
                        frac_1 = frac[1:]
                        if frac_1 in ajustes:
                            x += ' ' + ajustes[frac_1][i]
                        else:
                            x += ' ' + representaciones[frac_1][0]
                    else:
                        x += ' ' + representaciones[frac[1] + '0'][0]
                        if frac[2] != '0':
                            if frac[2] == '1':
                                x += ' y ' + ajustes['0' + frac[2]][i]
                            else:
                                x += ' y ' + representaciones['0' + frac[2]][0]
                x = x + ' ' + ajustes['_'][i]
                completo = x.strip() + ' ' + completo
        representacion += completo.strip()
        if valorNumerico.find(',') == -1:
            if valorNumerico2.find(',') != -1:
                representacion += ' ' + representaciones[len(valorNumerico2.split(',', 1)[1])][0]
            return representacion.replace('un millones', 'un millon').replace('un mil', 'mil')
        valorNumerico = valorNumerico.split(',', 1)[1]
        representacion += ' punto '

def representacionOrdinalFemenina(valorNumerico):
    if valorNumerico == 1000:
        return 'milésima'
    representacion = representaciones[str(valorNumerico // 100 * 100).zfill(2)][1]
    if valorNumerico % 100 < 21:
        return (representacion + ' ' + representaciones[str(valorNumerico % 100).zfill(2)][1]).strip()
    representacion += ' ' + representaciones[str((valorNumerico % 100) // 10 * 10)][1]
    return (representacion + ' ' + representaciones[str(valorNumerico % 10).zfill(2)][1]).strip()

def representacionFraccionaria(numerador, denominador):
    representacion_numerador = representacionNumerica(numerador)
    denominador = denominador.replace('.', '')
    if int(denominador) < 10:
        representacion_denominador = representaciones['0' + denominador][2]
    elif denominador[0] == '1' and int(denominador[1:]) == 0:
        representacion_denominador = representaciones[len(denominador) - 1][0]
    else:
        representacion_denominador = representacionNumerica(denominador).replace('veintiuno', 'veintiun').replace(' uno', 'un') + 'avos'
    representacion_numerador = representacion_numerador.replace(' uno', ' un')
    if representacion_numerador == 'un':
        representacion_denominador = representacion_denominador[:-1]
    return representacion_numerador + ' ' + representacion_denominador

def representacionRomana(valorRomano):
    valorNumerico = 0
    anterior = 10000
    for i in valorRomano:
        if representaciones[i][0] > anterior:
            valorNumerico -= 2 * anterior
        anterior = representaciones[i][0]
        valorNumerico += anterior
    return representacionNumerica(str(valorNumerico))

def representacionOrdinalRomana(valorRomano):
    valorNumerico = 0
    anterior = 10000;
    for i in valorRomano:
        if representaciones[i][0] > anterior:
            valorNumerico -= 2 * anterior
        anterior = representaciones[i][0]
        valorNumerico += anterior
    return (representacionOrdinalFemenina(valorNumerico) + ' ').replace('a ', 'o ').replace('primero', 'primer').replace('tercero', 'tercer')[:-1]

def quitarGuiones(titulo):
    titulo = re.sub(r'  +', r' ', titulo)
    for j in [' - ', '- ', ' -', '_']:
        titulo = titulo.replace(j, '-')
    return re.sub(r'^[ -]+|[ -]+$', '', titulo.lower())

def colocar(equivalentes, partes):
    contador = 0
    for k in range(len(partes[0]) - 1, -1, -1):
        if partes[0][k] in ['a', 'e', 'i', 'o', 'u']:
            contador += 1
            if contador == 2:
                equivalentes[(partes[0][:k + 1] + partes[1][1:]).lower()] = partes[0].lower()
                break

def quitar_acentos(texto):
    for k in range(len(texto)):
        if texto[k] == 'á':
            texto = texto[:k] + 'a' + texto[k+1:]
        elif texto[k] == 'é':
            texto = texto[:k] + 'e' + texto[k+1:]
        elif texto[k] == 'í':
            texto = texto[:k] + 'i' + texto[k+1:]
        elif texto[k] == 'ó':
            texto = texto[:k] + 'o' + texto[k+1:]
        elif texto[k] == 'ú':
            texto = texto[:k] + 'u' + texto[k+1:]
    return texto

def sustituir_siglas(content):
    content = re.sub(r'(?<![\w-])[Ss]istema[ -]RAA(?![\w-])', r'sistema renina-angiotensina-aldosterona', content)
    content = re.sub(r'(?<![\w-])Fc([αβßγελδζµκ])RI(?![\w-])', r'receptor Fc tipo 1 de inmunoglobulina \1', content)
    content = re.sub(r'(?<![\w-])MTTP(?![\w-])', r'proteína microsomal de transferencia de triglicéridos', content)
    content = re.sub(r'(?<![\w-])MHC-(II?I?)(?![\w-])', r'complejo mayor de histocompatibilidad  de clase \1', content)
    content = re.sub(r'(?<![\w-])MMPI(?![\w-])', r'Inventario de Personalidad de Minnesota Multiphasic', content)
    content = re.sub(r'(?<![\w-])LLG-T(?![\w-])', r'leucemia de linfocitos grandes granulares de origen T', content)
    content = re.sub(r'(?<![\w-])HTLV-(II?I?)(?![\w-])', r'virus linfotrópico de células T humanas tipo \1', content)
    content = re.sub(r'(?<![\w-])(ARN[tT]|[tT]ARN)(?![\w-])', r'ácido ribonucleico de transferencia', content)
    content = re.sub(r'(?<![\w-])OSHA(?![\w-])', r'administración de Seguridad y Salud Ocupacional', content)
    content = re.sub(r'(?<![\w-])LEOC(?![\w-])', r'litotricia extracorpórea por ondas de choque', content)
    content = re.sub(r'(?<![\w-])SDRN(?![\w-])', r'síndrome de dificultad respiratorio neonatal', content)
    content = re.sub(r'(?<![\w-])LDL(-colesterol)?(?![\w-])', r'lipoproteínas de baja densidad', content)
    content = re.sub(r'(?<![\w-])CPT[ -]?(II?)(?![\w-])', r'carnitina palmitoiltransferasa \1', content)
    content = re.sub(r'(?<![\w-])V(LDL|ldl)(?![\w-])', r'lipoproteínas de muy baja densidad', content)
    content = re.sub(r'(?<![\w-])LP-([BT])(?![\w-])', r'leucemia prolinfocítica de origen \1', content)
    content = re.sub(r'(?<![\w-])NEO-PI-R(?![\w-])', r'Inventario de Personalidad NEO Revisado', content)
    content = re.sub(r'(?<![\w-])siARN(?![\w-])', r'ácido ribonucleico interferentes pequeños', content)
    content = re.sub(r'(?<![\w-])FADH2(?![\w-])', r'dinucleótido de flavina y adenina reducido', content)
    content = re.sub(r'(?<![\w-])snRNP(?![\w-])', r'pequeñas ribonucleoproteínas nucleares', content)
    content = re.sub(r'(?<![\w-])ARNmp(?![\w-])', r'ácido ribonucleico mensajero precursor', content)
    content = re.sub(r'(?<![\w-])HIPEC(?![\w-])', r'quimioterapia hipertérmico intraperitoneal', content)
    content = re.sub(r'(?<![\w-])NADH(?![\w-])', r'nicotinamida-adenina-dinucleótido reducido', content)
    content = re.sub(r'(?<![\w-])TTPa(?![\w-])', r'tiempo de tromboplastina parcial activada', content)
    content = re.sub(r'(?<![\w-])SIDA(?![\w-])', r'síndrome de inmunodeficiencia adquirida', content)
    content = re.sub(r'(?<![\w-])PICC(?![\w-])', r'catéter central de inserción periférica', content)
    content = re.sub(r'(?<![\w-])EHRN(?![\w-])', r'enfermedad hemolítica del recién nacido', content)
    content = re.sub(r'(?<![\w-])SRAA(?![\w-])', r'sistema renina-angiotensina-aldosterona', content)
    content = re.sub(r'(?<![\w-])MCMI(?![\w-])', r'Inventario Clínico Multiaxial de Millon', content)
    content = re.sub(r'(?<![\w-])LLG(?![\w-])', r'leucemia de linfocitos grandes granulares', content)
    content = re.sub(r'(?<![\w-])RNA-seq(?![\w-])', r'secuenciación de ácido ribonucleico', content)
    content = re.sub(r'(?<![\w-])snARN(?![\w-])', r'pequeños ácido ribonucleico nucleares', content)
    content = re.sub(r'(?<![\w-])EPQ(?![\w-])', r'Cuestionario de Personalidad de Eysenck', content)
    content = re.sub(r'(?<![\w-])T(RH|rh)(?![\w-])', r'hormona liberadora de tirotropina', content)
    content = re.sub(r'(?<![\w-])EHP(?![\w-])', r'edema, hiperproteinuria e hipertensión', content)
    content = re.sub(r'(?<![\w-])RHPT(?![\w-])', r'reacción hemolítica postransfusional', content)
    content = re.sub(r'(?<![\w-])DDC(?![\w-])', r'displasia del desarrollo de la cadera', content)
    content = re.sub(r'(?<![\w-])MHC(?![\w-])', r'complejo mayor de histocompatibilidad', content)
    content = re.sub(r'(?<![\w-])(ARNm|mARN)(?![\w-])', r'ácido ribonucleico mensajero', content)
    content = re.sub(r'(?<![\w-])(AMPc|cAMP)(?![\w-])', r'adenosín monofosfato cíclico', content)
    content = re.sub(r'(?<![\w-])GnRH(?![\w-])', r'hormona liberadora de gonadotropina', content)
    content = re.sub(r'(?<![\w-])F(\d+),(\d+)BP(?![\w-])', r'fructosa-\1,\2-bifosfato', content)
    content = re.sub(r'(?<![\w-])VDDI(?![\w-])', r'ventrículo derecho de doble salido', content)
    content = re.sub(r'(?<![\w-])IDL(?![\w-])', r'lipoproteína de densidad intermedia', content)
    content = re.sub(r'(?<![\w-])ECA(?![\w-])', r'enzima convertidora de angiotensina', content)
    content = re.sub(r'(?<![\w-])VSG(?![\w-])', r'velocidad de sedimentación globular', content)
    content = re.sub(r'(?<![\w-])PH(\d+)(?![\w-])', r'hiperoxaluria primaria tipo \1', content)
    content = re.sub(r'(?<![\w-])CH(?![\w-])', r'forma clásica de esclerosis nodular', content)
    content = re.sub(r'(?<![\w-])CPDA(?![\w-])', r'citrato-fosfato-dextrosa-adenina', content)
    content = re.sub(r'(?<![\w-])AINE(?![\w-])', r'antiinflamatorios no esteroideos', content)
    content = re.sub(r'(?<![\w-])VRI(?![\w-])', r'capacidad de reserva inspiratorio', content)
    content = re.sub(r'(?<![\w-])VIH(?![\w-])', r'virus de inmunodeficiencia humana', content)
    content = re.sub(r'(?<![\w-])LAK(?![\w-])', r'asesinas activadas por linfocinas', content)
    content = re.sub(r'(?<![\w-])D&C(?![\w-])', r'legrado por dilatación y curetaje', content)
    content = re.sub(r'(?<![\w-])PEL(?![\w-])', r'límites de exposición permisibles', content)
    content = re.sub(r'(?<![\w-])HSC(?![\w-])', r'hiperplasia suprarrenal congénita', content)
    content = re.sub(r'(?<![\w-])(\d+)-FTHF(?![\w-])', r'\1-formiltetrahidrofolato', content)
    content = re.sub(r'(?<![\w-])DE?XA(?![\w-])', r'absorciometría dual de rayos X', content)
    content = re.sub(r'(?<![\w-])OMS(?![\w-])', r'Organización Mundial de la Salud', content)
    content = re.sub(r'(?<![\w-])TAC(?![\w-])', r'tomografía axoideo computarizada', content)
    content = re.sub(r'(?<![\w-])SI(?![\w-])', r'Sistema Internacional de Unidades', content)
    content = re.sub(r'(?<![\w-])(\d+)-MTHF(?![\w-])', r'\1-metiltetrahidrofolato', content)
    content = re.sub(r'(?<![\w-])DHFR(?![\w-])', r'enzima dihidrofolato reductasa', content)
    content = re.sub(r'(?<![\w-])fMRI(?![\w-])', r'resonancia magnética funcional', content)
    content = re.sub(r'(?<![\w-])EMA(?![\w-])', r'Agencia Europea de Medicamentos', content)
    content = re.sub(r'(?<![\w-])TΨC(?![\w-])', r'timidina-pseudouridina-citidina', content)
    content = re.sub(r'(?<![\w-])VH(B|C|D)(?![\w-])', r'virus de la hepatitis \1', content)
    content = re.sub(r'(?<![\w-])EROs(?![\w-])', r'especies reactivas de oxígeno', content)
    content = re.sub(r'(?<![\w-])GMPc(?![\w-])', r'guanosina monofosfato cíclico', content)
    content = re.sub(r'(?<![\w-])HDL(?![\w-])', r'lipoproteínas de alta densidad', content)
    content = re.sub(r'(?<![\w-])hCG(?![\w-])', r'gonadotropina coriónica humana', content)
    content = re.sub(r'(?<![\w-])DWI(?![\w-])', r'imágenes de difusión ponderada', content)
    content = re.sub(r'(?<![\w-])(\d+,\d+)BPG(?![\w-])', r'\1-bisfosfoglicerato', content)
    content = re.sub(r'(?<![\w-])A-ADN(?![\w-])', r'ácido desoxirribonucleico A', content)
    content = re.sub(r'(?<![\w-])ARNr(?![\w-])', r'ácido ribonucleico ribosomal', content)
    content = re.sub(r'(?<![\w-])CIV(?![\w-])', r'comunicación interventricular', content)
    content = re.sub(r'(?<![\w-])Fc([αβßγελδζµκ])R(?![\w-])', r'receptor Fc \1', content)
    content = re.sub(r'(?<![\w-])HLA(?![\w-])', r'antígeno leucocitario humano', content)
    content = re.sub(r'(?<![\w-])LLC(?![\w-])', r'leucemia linfocítica crónica', content)
    content = re.sub(r'(?<![\w-])FSH(?![\w-])', r'hormona foliculo estimulante', content)
    content = re.sub(r'(?<![\w-])TSV(?![\w-])', r'taquicardia supraventricular', content)
    content = re.sub(r'(?<![\w-])TAT(?![\w-])', r'test de apercepción temática', content)
    content = re.sub(r'(?<![\w-])HPVs?(?![\w-])', r'virus del papiloma humano', content)
    content = re.sub(r'(?<![\w-])dAMP(?![\w-])', r'desoxiadenosín monofosfato', content)
    content = re.sub(r'(?<![\w-])LLA(?![\w-])', r'leucosis linfoblástico alto', content)
    content = re.sub(r'(?<![\w-])SWA(?![\w-])', r'síndrome de wiskott-aldrich', content)
    content = re.sub(r'(?<![\w-])FEV(?![\w-])', r'volumen espiratorio forzado', content)
    content = re.sub(r'(?<![\w-])(\d+)-HTP(?![\w-])', r'\1-hidroxitriptófano', content)
    content = re.sub(r'(?<![\w-])LCA(?![\w-])', r'ligamento cruzado anterior', content)
    content = re.sub(r'(?<![\w-])RAA(?![\w-])', r'reumatismo articular agudo', content)
    content = re.sub(r'(?<![\w-])DDAVP(?![\w-])', r'acetato de desmopresina', content)
    content = re.sub(r'(?<![\w-])DHAP(?![\w-])', r'dihidroxiacetona fosfato', content)
    content = re.sub(r'(?<![\w-])TEC(?![\w-])', r'terapia electroconvulsiva', content)
    content = re.sub(r'(?<![\w-])ADN(?![\w-])', r'ácido desoxirribonucleico', content)
    content = re.sub(r'(?<![\w-])LEV(?![\w-])', r'linfoma esplénico velloso', content)
    content = re.sub(r'(?<![\w-])MBG(?![\w-])', r'membrana basal glomerular', content)
    content = re.sub(r'(?<![\w-])Ig([A-Z])(?![\w-])', r'inmunoglobulina \1', content)
    content = re.sub(r'(?<![\w-])IgRh(?![\w-])', r'globulina inmune Rhesus', content)
    content = re.sub(r'(?<![\w-])HIE(?![\w-])', r'hipertensión gestacional', content)
    content = re.sub(r'(?<![\w-])SSW(?![\w-])', r'síndrome de sturge-weber', content)
    content = re.sub(r'(?<![\w-])CPT(?![\w-])', r'capacidad pulmonar total', content)
    content = re.sub(r'(?<![\w-])GNL(?![\w-])', r'glomerulonefritis lúpico', content)
    content = re.sub(r'(?<![\w-])Ba\(NO3\)2(?![\w-])', r'nitrato de bario', content)
    content = re.sub(r'(?<![\w-])F(\d+)P(?![\w-])', r'fructosa-\1-fosfato', content)
    content = re.sub(r'(?<![\w-])ATPasa(?![\w-])', r'adenosintrifosfatasa', content)
    content = re.sub(r'(?<![\w-])FPP(?![\w-])', r'fecha probable de parto', content)
    content = re.sub(r'(?<![\w-])LMA(?![\w-])', r'leucemia mieloide aguda', content)
    content = re.sub(r'(?<![\w-])TCR(?![\w-])', r'receptores de células T', content)
    content = re.sub(r'(?<![\w-])IMC(?![\w-])', r'indice de masa corporal', content)
    content = re.sub(r'(?<![\w-])CD(?![\w-])', r'grupos de diferenciación', content)
    content = re.sub(r'(?<![\w-])G(\d+)P(?![\w-])', r'glucosa-\1-fosfato', content)
    content = re.sub(r'(?<![\w-])CVC(?![\w-])', r'catéter venoso central', content)
    content = re.sub(r'(?<![\w-])L&H(?![\w-])', r'Lacunar y Histiocítica', content)
    content = re.sub(r'(?<![\w-])LDH(?![\w-])', r'lactato deshidrogenasa', content)
    content = re.sub(r'(?<![\w-])OI(?![\w-])', r'osteogénesis imperfecta', content)
    content = re.sub(r'(?<![\w-])RE(?![\w-])', r'retículo endoplasmático', content)
    content = re.sub(r'(?<![\w-])(\d+)-FU(?![\w-])', r'\1-fluorouracilo', content)
    content = re.sub(r'(?<![\w-])(\d+)PG(?![\w-])', r'\1-fosfoglicerato', content)
    content = re.sub(r'(?<![\w-])HSG(?![\w-])', r'histerosalpingografía', content)
    content = re.sub(r'(?<![\w-])vWF(?![\w-])', r'factor Von Willebrand', content)
    content = re.sub(r'(?<![\w-])VEB(?![\w-])', r'virus de Epstein-Barr', content)
    content = re.sub(r'(?<![\w-])PL(?![\w-])', r'predominio linfocítico', content)
    content = re.sub(r'(?<![\w-])ARNs?(?![\w-])', r'ácido ribonucleico', content)
    content = re.sub(r'(?<![\w-])EEG(?![\w-])', r'electroencefalograma', content)
    content = re.sub(r'(?<![\w-])BH4(?![\w-])', r'tetrahidrobiopterina', content)
    content = re.sub(r'(?<![\w-])TP(?![\w-])', r'tiempo de protrombina', content)
    content = re.sub(r'(?<![\w-])EH(?![\w-])', r'enfermedad de Hodgkin', content)
    content = re.sub(r'(?<![\w-])PIO(?![\w-])', r'presión intraocular', content)
    content = re.sub(r'(?<![\w-])TPP(?![\w-])', r'tiamina pirofosfato', content)
    content = re.sub(r'(?<![\w-])SAM(?![\w-])', r'S-adenosilmetionina', content)
    content = re.sub(r'(?<![\w-])CI(?![\w-])', r'cociente intelectual', content)
    content = re.sub(r'(?<![\w-])LH(?![\w-])', r'hormona luteinizante', content)
    content = re.sub(r'(?<![\w-])BaCl2(?![\w-])', r'cloruro de bario', content)
    content = re.sub(r'(?<![\w-])BaSO4(?![\w-])', r'sulfato de bario', content)
    content = re.sub(r'(?<![\w-])H&D(?![\w-])', r'Hurter y Driffield', content)
    content = re.sub(r'(?<![\w-])ECG(?![\w-])', r'electrocardiograma', content)
    content = re.sub(r'(?<![\w-])PKA(?![\w-])', r'proteína quinasa A', content)
    content = re.sub(r'(?<![\w-])TS(?![\w-])', r'taquicardia sinusal', content)
    content = re.sub(r'(?<![\w-])PR(\d+)(?![\w-])', r'proteinasa \1', content)
    content = re.sub(r'(?<![\w-])HbS-C(?![\w-])', r'hemoglobina s-c', content)
    content = re.sub(r'(?<![\w-])EN(?![\w-])', r'esclerosis nodular', content)
    content = re.sub(r'(?<![\w-])mEq(?![\w-])', r'miliequivalentes', content)
    content = re.sub(r'(?<![\w-])CMV(?![\w-])', r'citomegalovirus', content)
    content = re.sub(r'(?<![\w-])MPO(?![\w-])', r'mieloperoxidasa', content)
    content = re.sub(r'(?<![\w-])MM(?![\w-])', r'mieloma múltiple', content)
    content = re.sub(r'(?<![\w-])EP(?![\w-])', r'embolia pulmonar', content)
    content = re.sub(r'(?<![\w-])DHF(?![\w-])', r'dihidrofolato', content)
    content = re.sub(r'(?<![\w-])vW(?![\w-])', r'Von Willebrand', content)
    content = re.sub(r'(?<![\w-])PM(?![\w-])', r'peso molecular', content)
    content = re.sub(r'(?<![\w-])RS(?![\w-])', r'Reed-Sternberg', content)
    content = re.sub(r'(?<![\w-])HA(?![\w-])', r'hemaglutinina', content)
    content = re.sub(r'(?<![\w-])UV(?![\w-])', r'ultravioleta', content)
    content = re.sub(r'(?<![\w-])miARN(?![\w-])', r'microARN', content)
    content = re.sub(r'(?<![\w-])CoA(?![\w-])', r'coenzima A', content)
    return content

def sustituir_abreviaturas(content):
    ROMANO = r'((CM|CD|D?C?C?C?)(XC|XL|L?X?X?X?)(IX|IV|VI?I?I?|II?I?)|(CM|CD|D?C?C?C?)(XC|XL|LX?X?X?|XX?X?)|CM|CD|DC?C?C?|CC?C?)'
    content = re.sub(r'(?<![\w-])V\. (cholerae|parahaemolyticus|vulnificus|alginolyticus|hollisae|damsela|mimicus|fluvialis|furnisii|metschnikovii|cincinnatiensis)(?![\w-])', r'Vibrio \1', content)
    content = re.sub(r'(?<![\w-])H\. (ducreyi|parahaemolyticus|aegyptius|(para)?influenzae)(?![\w-])', r'Haemophilus \1', content)
    content = re.sub(r'(?<![\w-])M\. (tuberculosis|leprae|ulcerans)(?![\w-])', r'Mycobacterium \1', content)
    content = re.sub(r'(?<![\w-])SAG\.M\.(?![\w-])', r'solución salina-adenina-glucosa-manitol', content)
    content = re.sub(r'(?<![\w-])g\.( d\.)? l\.(?![\w-])', r'grado de libertad', content)
    content = re.sub(r'(?<![\w-])H\.( capsulatum)(?![\w-])', r'histoplasma\1', content)
    content = re.sub(r'(?<![\w-])(p(or |[.,] ?))?[Ee]j[.:]', r'por ejemplo', content)
    # content = re.sub(r'(?<![\w-])O(BS|bs)\.:?(?![\w-])', r'Observaciones:', content)
    content = re.sub(r'(?<![\w-])H\.( pylori)(?![\w-])', r'Helicobacter\1', content)
    content = re.sub(r'(?<![\w-])EE\. UU[^\w](?![\w-])', r'Estados Unidos', content)
    content = re.sub(r'(?<![\w-])p\.m\.(?![\w-])', r'después del mediodía', content)
    content = re.sub(r'(?<![\w-])d\. C\.(?![\w-])', r'después de Cristo', content)
    content = re.sub(r'(?<![\w-])a\.m\.(?![\w-])', r'antes del mediodía', content)
    content = re.sub(r'(?<![\w-])a\. C\.(?![\w-])', r'antes de Cristo', content)
    content = re.sub(rf'(?<![\w-])s\. {ROMANO}(?![\w-])', r'siglo \1', content)
    content = re.sub(r'(?<![\w-])(A|a)br\.(?![\w-])', r'abreviatura', content)
    content = re.sub(r'(?<![\w-])S(IN|in)\.(?![\w-])', r'Sinónimos', content)
    content = re.sub(r'(?<![\w-])i\.m\.(?![\w-])', r'intramuscular', content)
    content = re.sub(r'(?<![\w-])coloq\.(?![\w-])', r'Coloquial', content)
    content = re.sub(r'(?<![\w-])etc\.([,)])(?![\w-])', r'\1', content)
    content = re.sub(r'(?<![\w-])desus\.(?![\w-])', r'Desuso', content)
    content = re.sub(r'(?<![\w-])Fórm\.(?![\w-])', r'fórmula', content)
    content = re.sub(r'(?<![\w-])loc\.(?![\w-])', r'Locución', content)
    content = re.sub(r'(?<![\w-])O(BS|bs)\.:?(?![\w-])', r'', content)
    content = re.sub(r'(?<![\w-])ingl\.(?![\w-])', r'ingles', content)
    content = re.sub(r'(?<![\w-])etc\.(?![\w-])', r'.', content)
    content = re.sub(r'(?<![\w-])Símb\. ', r'símbolo ', content)
    content = re.sub(r'(?<![\w-])Dra\. ', r'doctora ', content)
    content = re.sub(r'(?<![\w-])Dr\. ', r'doctor ', content)
    content = re.sub(r'(?<![\w-])St\.', r'San', content)
    return content

def sustituir_simbolos(content):
    content = re.sub(r'(?<![\w-])(Hz|[Hh]er(z|cio|tz(ios?)?))(?![\w-])', r'hercios', content)
    content = re.sub(r'(?<=/)[Ll](?=[ .,;&)-])|(?<![\w-])[Ll](?=[,/])', r'litros', content)
    content = re.sub(r'(?<=[\d}])( )m(?![\w-])|(?<![\w-])()m(?=\^)', r'\1metros', content)
    content = re.sub(r'(?<![\w-])mm[Hh]g(?![\w-])', r'milímetros de mercurio', content)
    content = re.sub(r'(?<=[/\d}]) ?gr?(?![\w-])|(?<!\w)gr?(?=/)', r' gramos', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ][lL](?![\w-])', r' microlitros', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ]Wb(?![\w-])', r' micro-webers', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ]mol(?![\w-])', r' micromoles', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ]V(?![\w-])', r' microvoltios', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ]g(?![\w-])', r' microgramos', content)
    content = re.sub(r'(?<![a-zA-Z-])[µμμ]m(?![\w-])', r' micrómetros', content)
    content = re.sub(r'(?<![\w-])mmol([^.])(?![\w-])', r'milimoles\1', content)
    content = re.sub(r'(?<![\w-])mOsm(ol)?(?![\w-])', r'miliosmoles', content)
    content = re.sub(r'(?<![\w-])3D(?=[ .,;)-])', r'tridimensional', content)
    content = re.sub(r'(?<![\w-])(kD|Kd)(?![\w-])', r'kilodaltons', content)
    content = re.sub(r'(?<![a-zA-Z])=(?![a-zA-Z])', r' igual a ', content)
    content = re.sub(r'(?<![\w-])cms?(?![\w-])', r'centímetros', content)
    content = re.sub(r'(?<![\w-])d[Ll](?![\w-])', r'decilitros', content)
    content = re.sub(r'(?<![\w-])m[Ll](?![\w-])', r'mililitros', content)
    content = re.sub(r'(?<![\w-])pb(?![\w-])', r'par de bases', content)
    content = re.sub(r'(?<![\w-])≠(?![\w-])', r' distinto de ', content)
    content = re.sub(r'(°|º|\^{o}) ?C', r' grados centígrados', content)
    content = re.sub(r'(?<![\w-])kDa(?![\w-])', r'kilodalton', content)
    content = re.sub(r'(?<![\w-])mV(?![\w-])', r'milivoltios', content)
    content = re.sub(r'(?<![\w-])mill(?![\w-])', r'millones', content)
    content = re.sub(r'(?<![\w-])mg(?![\w-])', r'miligramos', content)
    content = re.sub(r'(?<![\w-])kg(?![\w-])', r'kilogramos', content)
    content = re.sub(r'(?<![\w-])mm(?![\w-])', r'milímetros', content)
    content = re.sub(r'(?<![\w-])ng(?![\w-])', r'nanogramos', content)
    content = re.sub(r'(?<![\w-])nm(?![\w-])', r'nanometros', content)
    content = re.sub(r'(?<![\w-])dB(?![\w-])', r'decibelios', content)
    content = re.sub(r'(?<![\w-])Kb(?![\w-])', r'kilobases', content)
    content = re.sub(r'(?<![\w-])y [-/] o(?![\w-])', r'y/o', content)
    content = re.sub(r'(?<![\w-])min(?![\w-])', r'minutos', content)
    content = re.sub(r'(?<![\w-])Hg(?![\w-])', r'mercurio', content)
    content = re.sub(r'(?<![\w-])±(?![\w-])', r'más-menos', content)
    content = re.sub(r'([a-zA-Z])([αβßγελδζµκ])', r'\1_\2', content)
    content = re.sub(r'([αβßγελδζµκ])([a-zA-Z])', r'\1_\2', content)
    content = re.sub(r'(?<![(\w-])h(?![\n\w-])', r'horas', content)
    content = re.sub(r'(?<![\w-])gr(?![\w-])', r'griego', content)
    content = re.sub(r'(?<![\w-])Wb(?![\w-])', r'weber', content)
    content = re.sub(r'(?<=\w)\+(?!\w)', r' positivo ', content)
    content = re.sub(r'(?<!\w)>(?!\w)', r'mayor que', content)
    content = re.sub(r'(?<!\w)<(?!\w)', r'menor que', content)
    content = re.sub(r'(?<!\w)Rh(?!\w)', r'Rhesus', content)
    content = re.sub(r'≤', r' menor o igual que ', content)
    content = re.sub(r'≥', r' mayor o igual que ', content)
    content = re.sub(r'°F', r' grados fahrenheit', content)
    content = re.sub(r'\.{3}', r', etcétera. ', content)
    content = re.sub(r'\^{\+}', r' positivo ', content)
    content = re.sub(r'\^{-}', r' negativo ', content)
    content = re.sub(r'α|&alpha;', r'Alpha', content)
    content = re.sub(r'β|ß|&beta;', r'Beta', content)
    content = re.sub(r'γ|&gamma;', r'Gamma', content)
    content = re.sub(r'¾', r'tres cuartos', content)
    content = re.sub(r'®', r' registrado', content)
    content = re.sub(r'º ?K', r' kelvin', content)
    content = re.sub(r'[º°]', r' grados', content)
    content = re.sub(r'¼', r'un cuarto', content)
    content = re.sub(r'[ÄÅåàãâā]', r'a', content)#Tal vez
    content = re.sub(r'[èëêĕěē]', r'e', content)#Tal vez
    content = re.sub(r'[òøöōôő]', r'o', content)#Tal vez
    content = re.sub(r'[δΔ]', r'Delta', content)
    content = re.sub(r'[ωΩ]', r'Omega', content)
    content = re.sub(r'[Σς]', r'Sigma', content)
    content = re.sub(r'∞', r'infinito', content)
    content = re.sub(r'ε', r'Épsilon', content)
    content = re.sub(r'ό', r'Ómicron', content)
    content = re.sub(r'[ιί]', r'Iota', content)
    content = re.sub(r'[µμμ]', r'Mu', content)
    content = re.sub(r'\+', r' más ', content)
    content = re.sub(r'λ', r'Lambda', content)
    content = re.sub(r'κ', r'Kappa', content)
    content = re.sub(r'θ', r'Theta', content)
    content = re.sub(r'[ìīï]', r'i', content)#Tal vez
    content = re.sub(r'[ùцŭ]', r'u', content)#Tal vez
    content = re.sub(r'ζ', r'Zeta', content)
    content = re.sub(r'[łл]', r'l', content)#Tal vez
    content = re.sub(r'[ńη]', r'n', content)#Tal vez
    content = re.sub(r'²', r'^{2}', content)
    content = re.sub(r'³', r'^{3}', content)
    content = re.sub(r'₃', r'_{3}', content)
    content = re.sub(r'τ', r'Tau', content)
    content = re.sub(r'χ', r'Chi', content)
    content = re.sub(r'×', r'por', content)
    content = re.sub(r'š', r'sch', content)
    content = re.sub(r'π', r'pi', content)
    content = re.sub(r'æ', r'ae', content)
    content = re.sub(r'ы', r'bi', content)
    content = re.sub(r'î', r'iu', content)
    content = re.sub(r'φ', r'Fi', content)
    content = re.sub(r'œ', r'oe', content)
    content = re.sub(r'Б', r'b', content)
    content = re.sub(r'ç', r'c', content)
    content = re.sub(r'ρ', r'p', content)
    content = re.sub(r'ş', r's', content)
    content = re.sub(r'т', r't', content)
    content = re.sub(r'ŷ', r'y', content)
    return content

def aplicar_sustituciones(content):
    content = re.sub(r'(?<![\w-])([Uu]na?[ -])?([Cc]olor(ación)?|[Tt](ono|inte))[ -]azulad[ao][ -](de|en)[ -]la[ -]piel([ -]y[ -]las[ -](membranas[ -])?mucosas)?([ -]debido[ -]a[ -](la[ -])?((falta|insuficiencia|baja[ -]saturación)[ -]de[ -]oxígeno|baja[ -]oxigenación)([ -](de|en)[ -]la[ -]sangre)?)?(?![\w-])', r'cianosis', content)
    content = re.sub(r'(?<![\w-])(TDAH|[Tt]rastorno[ -](de|por)[ -](hiperactividad[ -]y[ -])?déficit[ -]de[ -]atención([ -](e[ -]hiperactividad|(y[ -]comportamiento[ -]perturbador)?))?)(?![\w-])', r'trastorno por déficit de atención e hiperactividad', content)
    content = re.sub(r'(?<![\w-])([Tt]omografía[ -](axial[ -]computarizada[ -])?(por|de)[ -][Ee]misión[ -]de[ -][Ff]otón[ -][Úú]nico|S(PECT|pect))(?![\w-])', r'tomografía axial computarizada por emisión de fotón único', content)
    content = re.sub(r'(?<![\w-])(EPOC|[Ee]nfermedad[ -]pulmonar[ -]obstructiv[oa][ -]crónic[oa]|[Ll]imitación[ -]inveterado[ -]del[ -]flujo[ -]neumático)(?![\w-])', r'enfermedades pulmonares obstructivas crónicas', content)
    content = re.sub(r'(?<![\w-])[Mm]icción[ -]frecuente|[Nn]ecesidad[ -]de[ -]orinar[ -]frecuentemente|[Ff]recuencia[ -]urinaria|[Ii]ncidencia[ -]urinario|[Pp]oliuria(?![\w-])', r'polaquiuria', content)
    content = re.sub(r'(?<![\w-])(translocación[ -](genética|cromosómica)[ -])?t\((\d+);(\d+)\)([ -]translocación[ -](genética|cromosómica))?(?![\w-])', r'translocación entre los cromosomas \3 y \4', content)
    content = re.sub(r'(?<![\w-])(FDA|Administración[ -]de[ -]Alimentos[ -]y[ -]Medicamentos)(?![\w-])', r'Administración de Alimentos y Medicamentos de los Estados Unidos', content)
    content = re.sub(r'(?<![\w-])(FAD|[Dd]inucleótido[ -]de[ -]flavina[ -]y[ -]adenina|[Ff]lavín[ -]aden(ín|ina)[ -]dinucleótido)(?![\w-])', r'flavina-adenina-dinucleótido', content)
    content = re.sub(r'(?<![\w-])([Cc]iclo[ -]de)(l[ -]ácido[ -]tricarboxílico|[ -](krebs|los ácidos[ -]tricarboxílicos))(?![\w-])', r'\1l ácido cítrico', content)
    content = re.sub(r'(?<![\w-])(RMN?|[Rr]esonancias?[ -]magnéticas?[ -]nuclear(es)?|Magnetic[ -]Resonance[ -]Imaging)(?![\w-])', r'resonancia magnética', content)
    content = re.sub(r'(?<![\w-])(tomografía[ -]de[ -]coherencia[ -](óptico|ocular)|OCT)(?![\w-])', r'tomografía axial computarizada de coherencia ocular', content)
    content = re.sub(r'(?<![\w-])(ACTH|([Aa]dreno)?[Cc]orticotro[pf]ina|[Hh]ormona[ -]adenocorticotropa)(?![\w-])', r'hormona corticotropa', content)
    content = re.sub(r'(?<![\w-])(ANCA|[Aa]nticuerpos?[ -]anticitoplasma[ -]del?[ -]neutrófilo)(?![\w-])', r'anticuerpo anticitoplasma de neutrófilo', content)
    content = re.sub(r'(?<![\w-])(AMP|[Mm]onofosfato[ -]de[ -]adenosina|[Aa]denos(in[ -]?|ín-)monofosfato)(?![\w-])', r'adenosín monofosfato', content)
    content = re.sub(r'(?<![\w-])(DTI|[Ii]magenología[ -]de[ -]tensor[ -]de[ -]difusión)(?![\w-])', r'resonancia magnética de tensor de difusión', content)
    content = re.sub(r'(?<![\w-])(ATP|[Tt]rifosfatos?[ -]de[ -]adenosina|[Aa]denos(in[ -]?|ín-)trifosfato)(?![\w-])', r'adenosín trifosfato', content)
    content = re.sub(r'(?<![\w-])(ARNi|[Ii]nterferencia[ -]por([ -]el)?[ -]ácido[ -]ribonucleico)(?![\w-])', r'ácido ribonucleico interferente', content)
    content = re.sub(r'(?<![\w-])(dolor y entumecimiento en|daño en los nervios de) las manos y los pies(?![\w-])', r'neuropatía periférico', content)
    content = re.sub(r'(?<![\w-])(ADP|[Dd]ifosfato[ -]de[ -]adenosina|[Aa]denos(in[ -]?|ín-)difosfato)(?![\w-])', r'adenosín difosfato', content)
    content = re.sub(r'(?<![\w-])(NAD|[Dd]inucleótido[ -]de[ -]nicotinamida[ -]y[ -]adenina)(?![\w-])', r'nicotinamida-adenina-dinucleótido', content)
    content = re.sub(r'(?<![\w-])([Ee]xpulsión[ -]de[ -]sangre[ -]de[ -]origen[ -]digestivo|[Vv]ómito[ -]negro)(?![\w-])', r'hematemesis', content)
    content = re.sub(r'(?<![\w-])([Nn]iacina|[Áá]cido[ -](nicotínico|niacina)|[Vv]itamina[ -](pp|[Bb]_\{[3]\}))(?![\w-])', r'vitamina B3', content)
    content = re.sub(r'(?<![\w-])[Ee]xp(ulsión[ -]de[ -]sangre[ -]por[ -]la[ -]boca|ectoración[ -]de[ -]sangre)(?![\w-])', r'hemoptisis', content)
    content = re.sub(r'(?<![\w-])(T(SH|sh)|[Hh]ormona[ -](tirotropa|estimulante[ -]de(l|[ -]la)?[ -]tiroides))(?![\w-])', r'tirotropina', content)
    content = re.sub(r'(?<![\w-])(OGM|[Oo]rganismo[ -]genéticamente[ -]modificado)(?![\w-])', r'organismos genéticamente modificados', content)
    content = re.sub(r'(?<![\w-])(ETS|[Ee]nfermedades[ -]sexualmente[ -]transmisibles)(?![\w-])', r'enfermedades de transmisión sexual', content)
    content = re.sub(r'(?<![\w-])(I(ST|TS)|[Ii]nfección[ -]sexualmente[ -]transmisible)(?![\w-])', r'infecciones de transmisión sexual', content)
    content = re.sub(r'(?<![\w-])(NGS|[Ss]ecuenciación[ -]de[ -]próxima[ -]generación)(?![\w-])', r'secuenciación de nueva generación', content)
    content = re.sub(r'(?<![\w-])(FAB|French-American-British)(?![\w-])', r'franco-británico-estadounidense', content)
    content = re.sub(r'(?<![\w-])[Dd]olor[ -](o[ -]incomodidad[ -])?(al[ -]orinar|durante[ -]la[ -]micción)(?![\w-])', r'disuria', content)
    content = re.sub(r'(?<![\w-])([Gg]angrena[ -]pulmonar|[Nn]eumonía[ -](necrosante|gangrenoso))(?![\w-])', r'absceso pulmonar', content)
    content = re.sub(r'(?<![\w-])(TC|[Tt]omografías?[ -]computa(da|rizadas))(?![\w-])', r'tomografía computarizada', content)
    content = re.sub(r'(?<![\w-])[Vv]irus[ -](de[ -]la[ -]hepatitis[ -])?delta(?![\w-])', r'virus de la hepatitis d', content)
    content = re.sub(r'(?<![\w-])([Ff]olacina|[Áá]cido[ -]fólico|[Vv]itamina[ -][Bb]_\{9\})(?![\w-])', r'vitamina B9', content)
    content = re.sub(r'(?<![\w-])[Ii]nflamación[ -]aguda[ -]de[ -]los[ -]glomérulos(?![\w-])', r'glomerulonefritis', content)
    content = re.sub(r'(?<![\w-])(IL|[Ii]nterleuquina)(-\d+[αβßγελδζµκ]?|)(?![\w-])', r'interleucina\2', content)
    content = re.sub(r'(?<![\w-])([Pp]resencia[ -]de[ -])?[Ss]angre[ -]en[ -]la[ -]orina(?![\w-])', r'hematuria', content)
    content = re.sub(r'(?<![\w-])[Pp]íldora[ -]micro[ -]progestativa(?![\w-])', r'píldora progestativa', content)
    content = re.sub(r'(?<![\w-])[Pp]resencia[ -]de[ -]proteínas[ -]en[ -]la[ -]orina(?![\w-])', r'proteinuria', content)
    content = re.sub(r'(?<![\w-])([Áá]cido[ -]pantoténico|[Vv]itamina[ -][Bb]_\{5\})(?![\w-])', r'vitamina B5', content)
    content = re.sub(r'(?<![\w-])([Rr]iboflavina|[Vv]itamina[ -]([Gg]|[Bb]_\{2\}))(?![\w-])', r'vitamina B2', content)
    content = re.sub(r'(?<![\w-])[Dd]escenso[ -]de[ -]la[ -]tensión[ -]arterial(?![\w-])', r'hipotensión', content)
    content = re.sub(r'(?<![\w-])(GTP|[Gg]uanos(ina|ín)[ -]trifosfato)(?![\w-])', r'trifosfato de guanosina', content)
    content = re.sub(r'(?<![\w-])(ITU|infección urinario)(?![\w-])', r'infecciones del tracto urinario', content)
    content = re.sub(r'(?<![\w-])(FMN|[Ff]lavín[ -]mononucleótido)(?![\w-])', r'mononucleótido de flavina', content)
    content = re.sub(r'(?<![\w-])([Cc]obalamina|[Vv]itamina[ -][Bb]_\{12\})(?![\w-])', r'vitamina B12', content)
    content = re.sub(r'(?<![\w-])([Bb]iotina|[Vv]itamina[ -][Bb]_\{[78]\})(?![\w-])', r'vitamina B7', content)
    content = re.sub(r'(?<![\w-])([Pp]iridoxina|[Vv]itamina[ -][Bb]_\{6\})(?![\w-])', r'vitamina B6', content)
    content = re.sub(r'(?<![\w-])([Tt]iamina|[Vv]itamina[ -][Bb]_\{1\})(?![\w-])', r'vitamina B1', content)
    content = re.sub(r'(?<![\w-])[Ii]nflamación[ -]del[ -]páncreas(?![\w-])', r'pancreatitis', content)
    content = re.sub(r'(?<![\w-])(DMO|[Dd]ensidad[ -]ósea)(?![\w-])', r'densidad mineral ósea', content)
    content = re.sub(r'(?<![\w-])(CO2|[Gg]as[ -]carbónico)(?![\w-])', r'dióxido de carbono', content)
    content = re.sub(r'(?<![\w-])(THF|[Tt]etrahidrofolato)(?![\w-])', r'ácido tetrahidrofólico', content)
    content = re.sub(r'(?<![\w-])[Ss]angrado[ -]por[ -]la[ -]nariz(?![\w-])', r'epistaxis', content)
    content = re.sub(r'(?<![\w-])[Ii]nglés[ -]y[ -]alemán(?![\w-])', r'lenguas germánicas', content)
    content = re.sub(r'(?<![\w-])[Ff]oliculoestimulante(?![\w-])', r'foliculo estimulante', content)
    content = re.sub(r'(?<![\w-])[Ss]ed[ -](excesivo|importante)(?![\w-])', r'polidipsia', content)
    content = re.sub(r'(?<![\w-])(SNR|[Ss]eñal-ruido)(?![\w-])', r'relación señal-ruido', content)
    content = re.sub(r'(?<![\w-])[Ii]nflamación[ -]del[ -]colon(?![\w-])', r'colitis', content)
    content = re.sub(r'(?<![\w-])(ligad[ao]s? al )([XY])(?![\w-])', r'\1cromosoma \2', content)
    content = re.sub(r'(?<![\w-])([Dd]éficit|[Cc]arencia)(?![\w-])', r'deficiencia', content)
    content = re.sub(r'(?<![\w-])[Cc]ólico[ -]nefrítico(?![\w-])', r'cólico renal', content)
    content = re.sub(r'(?<![\w-])[Vv]itamina[ -][Cc](?![\w-])', r'ácido ascórbico', content)
    content = re.sub(r'(?<![\w-])[Dd]el[ -]neonato(?![\w-])', r'neonatal', content)
    content = re.sub(r'(?<![\w-])pseudquistes(?![\w-])', r'pseudoquistes', content)
    content = re.sub(r'(?<![\w-])izqierdos(?![\w-])', r'izquierdos', content)
    content = re.sub(r'(?<![\w])[Kk]orsakoff(?![\w])', r'kórsakov', content)
    content = re.sub(r'(?<![\w-])métdos(?![\w-])', r'métodos ', content)
    content = re.sub(r'(?<![\w-])LeFort(?![\w-])', r'Le Fort', content)
    content = re.sub(r'(?<![\w-])auuda(?![\w-])', r'ayuda', content)
    content = sustituir_siglas(content)
    content = sustituir_abreviaturas(content)
    content = sustituir_simbolos(content)
    return content

def limpiar_html_abreviaturas(content, nombreArchivo, equivalentes, igualaciones):
    ROMANO = r'((CM|CD|D?C?C?C?)(XC|XL|L?X?X?X?)(IX|IV|VI?I?I?|II?I?)|(CM|CD|D?C?C?C?)(XC|XL|LX?X?X?|XX?X?)|CM|CD|DC?C?C?|CC?C?)'
    content = re.sub(r'<!--(.*?)-->', r'', content, flags=re.DOTALL)
    content = content.replace('&quot;', '"').replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<').replace('\t', ' ').replace(' ', ' ').replace(' ', ' ').replace(' ', ' ').replace('�', ' ').replace('\u200b', ' ')
    content = re.sub(r'<(h(1[^>]*>(.*?)</h1|2[^>]*>(.*?)</h2|3[^>]*>(.*?)</h3|4[^>]*>(.*?)</h4)|(center[^>]*>(.*?)</center|table[^>]*>(.*?)</table|tbody[^>]*>(.*?)</tbody|tr[^>]*>(.*?)</tr|td[^>]*>(.*?)</td|ul[^>]*>(.*?)</ul))>', r'', content, flags=re.DOTALL)
    content = re.sub(r'<((sup|SUP)[^>]*> *</(sup|SUP)|sub[^>]*> *</sub|img[^>]*)>', r'', content)
    content = re.sub(r' +(<(sup|SUP)[^>]*>(.*?)</(sup|SUP)>)(\w+)', r' \5\1', content)
    content = re.sub(r' *<(sup|SUP)[^>]*> *(.*?)( *)</(sup|SUP)>', r'^{\2}\3', content)
    content = re.sub(r' +(<sub[^>]*>(.*?)</sub>)(\w+)', r' \3\1', content)
    content = re.sub(r' *<sub[^>]*> *(.*?)( *)</sub>', r'_{\1}\2', content)
    while re.search(r'<span[^>]*>(.*?)</span>', content, flags=re.DOTALL):
        content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', content, flags=re.DOTALL)
    while re.search(r'<li[^>]*>(.*?)</li>', content, flags=re.DOTALL):
        content = re.sub(r'<li[^>]*>(.*?)</li>', r'·\1', content, flags=re.DOTALL)
    while re.search(r'<strong[^>]*>(.*?)</strong>', content):
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', content)
    while re.search(r'<empty[^>]*>(.*?)</empty>', content):
        content = re.sub(r'<empty[^>]*>(.*?)</empty>', r'\1', content)
    while re.search(r'<small[^>]*>(.*?)</small>', content):
        content = re.sub(r'<small[^>]*>(.*?)</small>', r'\1', content)
    while re.search(r'<i[^>]*>(.*?)</i>', content):
        content = re.sub(r'<i[^>]*>(.*?)</i>', r'\1 ', content)
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', content, flags=re.DOTALL)
    content = re.sub(r'<ol[^>]*>(.*?)</ol>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<font[^>]*> *(.*?)</font>', r'\1', content)
    content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', content)
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'\1', content)
    content = re.sub(r'<ni[^>]*>(.*?)</ni>', r'\1', content)
    content = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', content)
    content = re.sub(r'<b[^>]*>(.*?)</b>', r'\1', content)
    content = re.sub(r'<s[^>]*>(.*?)</s>', r'\1', content)
    content = re.sub(r'<I[^>]*>(.*?)</I>', r'\1', content)
    content = re.sub(r'<[bh]r[^>]*/>', r'\n', content)
    content = re.sub(r'>( ?>)+', r'>', content)
    content = re.sub(r'<( ?<)+', r'<', content)
    content = re.sub(r'(?<=\n)([^\n]+: *)?(\n+ *\d+\. [^\n]+)+\n+ *(?!\d)', r'', '\n' + content)
    content = re.sub(r'(?<=\n)\d+', r'', content)
    content = '\n ' + nombreArchivo + ' \n' + content + '\n'
    content = content.replace('–', '-').replace('−', '-').replace('—', '-').replace('¬', '-')
    content = re.sub(r'([©®] Clínica Universidad de Navarra(\.| 2023)|\((véase la entrada correspondiente|[Vv]er (la )?tabla [^)]*)\)|> Cómo se trata el acné|, (ca|va|ria)\.)', r'', content)
    content = re.sub(r'(\(([^)(\n]*\([^)(\n]*\))*[^)\n]*|\[([^][\n]*\[[^][\n]*\])*[^]\n]*)(?=\n)', r' ', content)
    content = re.sub(r'\[(\d+|[^][]*( [^][]*|(\[[^][]*\][^][]*){1,2}))\]', r'', content)
    content = re.sub(r' - ([^()\n-]*\([^)-]*\)(.*?)) - ', r' (\1) ', content)
    content = re.sub(r'\[\.{3}\]|…', r'[puntos suspensivos]', content)
    content = re.sub(r' - ([^(){}\n-]*) -([ ,])', r' (\1)\2', content)
    content = re.sub(r'(?<=\n)([^[]*)\](.*?)(?=\n)', r'\1', content)
    content = re.sub(r'(?<![\w-])de el(?![\w-])', r'del', content)
    content = re.sub(r'(?<=\n) *Foto: ©(.*?)(?=\n)', r'', content)
    content = re.sub(r'(?<![\w-])a el(?![\w-])', r'al', content)
    content = re.sub(r' -(\w(.*?)\w)-([ ,])', r' (\1)\3', content)
    content = re.sub(r'(?<=\d)([<>])(?=\d)', r' \1', content)
    content = re.sub(r'(?<=\n) *l(?![\w-])', r'El', content)
    content = re.sub(r'> Saber (.*?)(?=\n)', r'', content)
    content = re.sub(r'(?<=\n) *¿(.*?)\?', r'', content)
    content = re.sub(r'(?<=\d):(?=\d)', r' a ', content)
    content = re.sub(r'([<>])(?=\d)', r'\1 ', content)
    content = re.sub(r'\S*https://\S*', r'', content)
    content = re.sub(r' - (?=\d)', r' -', content)
    content = re.sub(r'\n-+\n', r'\n', content)
    content = re.sub(r'\\times', r'X', content)
    content = re.sub(r'=( *=)+', r'=', content)
    content = re.sub(r'\(v\.?\)', r'', content)
    content = re.sub(r'[«“"”»©]', r'', content)
    content = re.sub(r'[‘’′´]', r"'", content)
    content = re.sub(r'\|\|', r'\n', content)
    content = re.sub(r'\\[()]', r'', content)
    content = re.sub(r'\(se\)', r'', content)
    content = re.sub(r'\^{®}', r'', content)
    content = re.sub(r'\^{a}', r'', content)
    content = re.sub(r'\^{b}', r'', content)
    content = re.sub(r'→', r':', content)
    content = re.sub(r'([\w,-]+)\'+([\w,-]+)\'+([\w,-]+)', r'\1\2\3', content)
    content = re.sub(r'(\w{1,3})\'+(\w{1,3})\'+', r'\1 prima \2 prima ', content)
    content = re.sub(r'([\w,-]+)\'+([\w,-]+)\'+', r'\1\2', content)
    content = re.sub(r'(\w+)\'+(\w+)', r'\1 \2', content)
    content = re.sub(r'([\w-]+)\'+([\w-]+)', r'\1\2', content)
    content = re.sub(r'(?<!\w)\'+(.*?)\'+', r'\1', content)
    content = re.sub(r'(?<!\w)(\w{1,3})\'+', r'\1 prima ', content)
    content = re.sub(r'(?<=[ (<>])((\d+\.?)*\d*,?\d+)%?( ?- ?)((\d+\.?)*\d*,?\d+)[ _]?%(?=[ .,;)])', r'\1\3\4 por ciento', content)
    content = re.sub(r'\\frac{([^{}\n]*({[^{}\n]*}[^{}\n]*)*)}{([^{}\n]*({[^{}\n]*}[^{}\n]*)*)}', r'(\1)/(\3)', content)
    content = re.sub(r'(?<=[ (<>])((\d+\.?)*\d*,?\d+)[ _]?%(?=[ .,;)])', r'\1 por ciento', content)
    content = re.sub(r'\(:', r'(', content)
    while re.search(r'(?<=\n)[ ,;y)]*(tr|pl|adj|adv|intr|n\.p|(s\.)?[mf]|v(\.\(?prnl)?)\.', content):
        content = re.sub(r'(?<=\n)[ ,;y)]*(tr|pl|adj|adv|intr|n\.p|(s\.)?[mf]|v(\.\(?prnl)?)\.', r'', content)
    bandera = 0
    numerosOrdinales = re.findall(r'(((\d+(\.\d\d\d)*)\.|\d+ *)ª)', content)
    for numero in numerosOrdinales:
        content = re.sub(numero[0], ' ' + representacionOrdinalFemenina(int(numero[1].replace('.', ''))) + ' ', content, count=1)
    content = re.sub(r'(?<![\w-])(sn|mi|si|m|t|T)(RNA|ARN)(s|m|t|T|mp|)(?![\w-])', r'\1ARN\3', content)
    content = re.sub(r'(?<![\w-])((des)?proporción) LH/FSH(?![\w-])', r'\1 de LH a FSH', content)
    content = re.sub(r'(?<![\w-])(A-|)(DNA|ADN|dna)(?![\w-])', r'\1ADN', content)
    content = re.sub(r'(?<![\w-])VIH/SIDA(?![\w-])', r'VIH con SIDA', content)
    content = re.sub(r'(?<![\w-])LLC/PL(?![\w-])', r'LLC con PL', content)
    content = aplicar_sustituciones(content)
    content = re.sub(r'\(Observaciones:?\)', r'', content)
    content = re.sub(r'Coloquial;', r'', content)
    content = re.sub(r'ª|\'', r'', content)
    content = re.sub(r'([^\w]|\d)σ([^\w]|\d)', r'\1 desviación estándar\2', content)
    content = re.sub(r'(?<=[ (])(\^{[^}]+}(_{[^}]+})?)([\w-]+)', r'\3\1', content)
    #Algoritmo para reemplazar los numeros romanos ordinales
    while re.search(rf'(?<![\w-]){ROMANO}([ ,]+([a-zA-Z]{0,4}[ ,]+)*(ventrículos?|par(es)?|nervios?|espacio|vértebra))(?=[ .,;)])', content):
        match = re.search(rf'(?<![\w-]){ROMANO}([ ,]+([a-zA-Z]{0,4}[ ,]+)*(ventrículos?|par(es)?|nervios?|espacio|vértebra))(?=[ .,;)])', content)
        content = re.sub(rf'(?<![\w-]){ROMANO}([ ,]+([a-zA-Z]{0,4}[ ,]+)*(ventrículos?|par(es)?|nervios?|espacio|vértebra))(?=[ .,;)])', lambda match: '' + representacionOrdinalRomana(match.group(1)) + '' + match.group(7), content, count=1)
    #En el siguiente algoritmo se buscan apariciones de numeros romanos a partir de palabras
    #clave previas, siempre que no tengan en el medio palabras negativas.
    #Por otra parte, tambien se compara en general que el parrafo anterior y contenedor del numero
    #romano no contenga otra seccion de palabras negativas (para ello se usa j)
    j = 0
    i = 1
    while content.find('\n', i + 1) != -1 or content.find('.', i + 1) != -1:
        posSalto = content.find('\n', i + 1)
        posPunto = content.find('.', i + 1)
        if posSalto != -1:
            if posPunto != -1:
                pos = min(posSalto,posPunto)
            else:
                pos = posSalto
        else:
            pos = posPunto
        if not re.search(r'(?<!\w)(influenzae?|timpanogramas?|multiproteico|tetrosas?|peptidoglicano|serina|Sanfilippo)(?![\w-])', content[j:pos + 1]):
            texto = content[i:pos + 1]
            inicio = 0
            while re.search(r'(?<!\w)(siglos?|(sub)?[tT]ipos?|clase|type|ganglios?|[aA]ngiotensina|Billroth|palmitoiltransferasa|fosfodiesterasa|glucogenosis|[eE]stadios?|neurofibromatosis|nivel(es)?|histocompatibilidad|topoisomerasa|Mobitz|cortical(es)?|polimerasa|coagulación|(meta|pro|ana|telo)fase|grados?|meiosis|segmentos?|Le Fort|simple|par(es)?|grupo|craneal(es)?|nervios?|protoporfirina|capas?|trisomía|[aA]ntitrombina|[f|F]actor(es)?|ventrículo|romanos?|formas?|complejo|fases?|derivaciones|eje|Lista|glicoproteína|categoría|Bender-Gestalt|ciclohidrolasa|carbónica|califa|peptidasa|Gower|reyes|Kohler|ovocito)(?![\w-])', texto[inicio:]):
                match = re.search(r'(?<!\w)(siglos?|(sub)?[tT]ipos?|clase|type|ganglios?|[aA]ngiotensina|Billroth|palmitoiltransferasa|fosfodiesterasa|glucogenosis|[eE]stadios?|neurofibromatosis|nivel(es)?|histocompatibilidad|topoisomerasa|Mobitz|cortical(es)?|polimerasa|coagulación|(meta|pro|ana|telo)fase|grados?|meiosis|segmentos?|Le Fort|simple|par(es)?|grupo|craneal(es)?|nervios?|protoporfirina|capas?|trisomía|[aA]ntitrombina|[f|F]actor(es)?|ventrículo|romanos?|formas?|complejo|fases?|derivaciones|eje|Lista|glicoproteína|categoría|Bender-Gestalt|ciclohidrolasa|carbónica|califa|peptidasa|Gower|reyes|Kohler|ovocito)(?![\w-])', texto[inicio:])
                inicio = inicio2 = inicio + match.start() + len(match.group())
                if match.group() in ['forma', 'formas'] and not re.search(rf'^ {ROMANO}(?=[ .,;)\n])', texto[inicio2:]):
                    continue
                while re.search(rf'(?<![\w-]){ROMANO}(?=[ .,;)\n])', texto[inicio2:]):
                    match2 = re.search(rf'[^\w-]{ROMANO}[ .,;)\n]', texto[inicio2:])
                    text = match2.group()
                    if text[0] == '(' and text[-1] == ')' and match.group() not in ['nervio', 'nervios']:
                        break
                    inicio3 = inicio2 + match2.start() + 1
                    if re.search(r'(?<!\w)(rayos|vitaminas?|cromosomas?|proteínas?|banda|radiaci(ones|ón)|[Ii]nmunoglobulina|mitomicina|antígeno|células|retrovirus|hemoglobin(as|opatía)|símbolo|hepatitis|fosfolipasa|bandeo|fibras|por|letra|proteincinasa|síndrome|línea|denominados?|Rhesus|lanatosido|secretan|ondas|dímero|conos|(anti)?hemofilia|somatomedina)(?![\w-])', texto[inicio2:inicio3]):
                        match = re.search(r'(?<!\w)(rayos|vitaminas?|cromosomas?|proteínas?|banda|radiaci(ones|ón)|[Ii]nmunoglobulina|mitomicina|antígeno|células|retrovirus|hemoglobin(as|opatía)|símbolo|hepatitis|fosfolipasa|bandeo|fibras|por|letra|proteincinasa|síndrome|línea|denominados?|Rhesus|lanatosido|secretan|ondas|dímero|conos|(anti)?hemofilia|somatomedina)(?![\w-])', texto[inicio2:inicio3])
                        inicio = inicio2 + match.start() + len(match.group())
                        break
                    texto = texto[:inicio2] + texto[inicio2:].replace(text, text[0] + representacionRomana(text[1:-1]) + text[-1], 1)
            content = content[:i] + texto + content[pos + 1:]
            pos = len(content[:i] + texto) - 1
        j = i
        i = pos
    ##Leucemia de células plasmáticas (LCP)
    ##depleción linfoide (DL)
    ##ligamento colateral medial (LCM)
    ##Reacción en Cadena de la Polimerasa (PCR)
    ##arteriovenoso (AV)
    ##hormona antidiurética (ADH)
    ##Volumen residual (VR)
    ##neuraminidasa (NA)
    ##Leucemia mieloide aguda indiferenciada (M1)
    ##Trombosis venosa profunda vs Taquicardia ventricular paroxística (TVP)
    ##balistocardiografía vs Bacillus Calmette-Guérin (BCG)
    ##polietileno glicol vs fosfoenolpiruvato (PEP)
    ##infarto de miocardio vs intramedular (IM)
    ##trastornos del comportamiento alimentario (TCA)
    ##superóxido-dismutasa (SOD)
    ##tomografía computarizada vs Colesterol total (CT)
    ##tomografía por emisión de positrones (PET)
    
    #malignización maculoso senil (DMAE)
    #n-acetilglucosamina (GlcNAc)
    #radioterapia de intensidad modulada (IMRT) y la radioterapia guiada por imágenes (IGRT)
    #Sievert (Sv)
    #nano-webers (nWb)
    #lectrorretinografía (ERG)
    #estrógenos (secreción psicógeno sexual femenina)
    #fecundación in vitro (FIV)
    #enfermedad inflamatorio pélvico (EIP)
    #lesión tubular proximal y basal (malignización vacuolizar)
    #arn-polimerasa reversa nucleósido (ITIN)
    #polaquiuria (aumento en la producción de micción)
    #polaquiuria (producción excesivo de micción)
    #presión parcial de dióxido de carbono (PaCO2)
    #órgano intracelular neural neurovegetativo (SNA)
    #dilatación de las pupilas (midriasis)
    #oxigenoterapia por capa extracorpóreo (ECMO)
    #segundos s
    _cambio = 1
    if content.count('(') < 51:
        while re.search(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)\)(.*?)(?=\n)', content):
            while re.search(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)(\d+| \w)\)(.*?)(?=\n)', content):
                if re.search(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)(\d+)\)(.*?)(?=\n)', content):
                    _cambio *= 2
                elif re.search(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)( \w)\)(.*?)(?=\n)', content):
                    if _cambio > 0:
                        _cambio = -_cambio
                content = re.sub(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)(\d+| \w)\)(.*?)(?=\n)', r'\1\n·\5', content, count=1)
            content = re.sub(r'(?<=\n)(([^()]*\(([^()]*\([^()]*\))*[^()]*\))*[^()]*)\)(.*?)(?=\n)', r'\1\4', content, count=1)
    if _cambio < -1:
        content = re.sub(r'(?<=\n)(·[^\n]+\n)+', r'', content)
    content = re.sub(r'(?<![\w-])(\d+)((?: +\d{3})+)(?![\w-])', lambda m: m.group(1) + m.group(2).replace(' ', ''), content)
    #Fracciones
    #Reglas:
    #   ~Si 'visión' entonces 'numero1 numero2'
    #   ~Si 'arterial' entonces 'numero1 sobre numero2'
    #   ~Si 'numero1/numero2 algo1/algo2' entonces 'numero1 a numero2'
    #   ~Si 'de/del' antes o despues de numero1/numero2, entonces representacionFraccionaria(numero1,numero2)
    #   ~else: 'numero1' de 'numero2'
    numeros = re.findall(r'(?<=[ (])(\d+(\.\d\d\d)*(,\d+)?)/(\d+(\.\d\d\d)*(,\d+)?)(?=[ .,)])', content)
    for numero in numeros:
        if re.search(r'(?<=\n)[^\n]*visión[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'( |\.|,|\))[^\n]*(?=\n)', content) or re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'( |\.|,|\))[^\n]*visión[^\n]*(?=\n)', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?=[ .,)])', representacionNumerica(numero[0]) + '-' + representacionNumerica(numero[3]), content, count=1)
        elif re.search(r'(?<=\n)[^\n]*arterial[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'( |\.|,|\))[^\n]*(?=\n)', content) or re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'( |\.|,|\))[^\n]*arterial[^\n]*(?=\n)', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?=[ .,)])', representacionNumerica(numero[0]) + ' sobre ' + representacionNumerica(numero[3]), content, count=1)
        elif re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r' \w+/\w+[^\n]*(?=\n)', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?= )', representacionNumerica(numero[0]) + ' a ' + representacionNumerica(numero[3]), content, count=1)
        elif re.search(r'(?<=\n)[^\n]* del? ' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'( |\.|,|\))[^\n]*(?=\n)', content) or re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r' del? [^\n]*(?=\n)', content):
            if numero[0].replace('.', '').isdigit() and numero[3].replace('.', '').isdigit():
                content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?=[ .,)])', representacionFraccionaria(numero[0], numero[3]), content, count=1)
            else:
                content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?=[ .,)])', representacionNumerica(numero[0]) + ' entre ' + representacionNumerica(numero[3]), content, count=1)
        else:
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '/' + re.escape(numero[3]) + r'(?=[ .,)])', representacionNumerica(numero[0]) + ' de ' + representacionNumerica(numero[3]), content, count=1)
    numeros = re.findall(r'(?<=[ (])(\d+(\.\d\d\d)*(,\d+)?)(?=/)', content)
    for numero in numeros:
        if re.search(r'(?<=[ (])' + re.escape(numero[0]) + r'/(?=\d)', content) or re.search(r'(?<=\n)[^\n]*[^\w](fórmula|gráfico)[^\w][^\n]*( |\()' + re.escape(numero[0]) + r'/[^\n]*(?=\n)', content) or re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + r'/[^\n]*[^\w](fórmula|gráfico)[^\w][^\n]*(?=\n)', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'/', representacionNumerica(numero[0]) + ' entre ', content, count=1)
        else:
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'/', representacionNumerica(numero[0]) + ' por ', content, count=1)
    #Rangos
    numeros = re.findall(r'(?<=[ (])((\d+,?)*\d*\.\d+)( ?[-:] ?)((\d+,?)*\d*\.\d+)([.,:;)]*)(?=[ \n])', content)
    for numero in numeros:
        if len(numero[0].split('.')[1]) != 3:
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + numero[2] + re.escape(numero[3]) + re.escape(numero[5]) + r'(?=[ \n])', numero[0].replace(',', '#').replace('.', ',').replace('#', '.') + numero[2] + numero[3].replace(',', '#').replace('.', ',').replace('#', '.') + numero[5], content, count=1)
    numeros = re.findall(r'(?<=[ (])(\d+(,\d\d\d)+)( ?[-:] ?)(\d+(,\d\d\d)+)([.,:;)]*)(?=[ \n])', content)
    for numero in numeros:
        if numero[0][-1] == '0':
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + numero[2] + re.escape(numero[3]) + re.escape(numero[5]) + r'(?=[ \n])', numero[0].replace(',', '.') + numero[2] + numero[3].replace(',', '.') + numero[5], content, count=1)
    numeros = re.findall(r'(?<=[ (])(\d+(\.\d\d\d)*(,\d+)?)( ?[-:] ?)(\d+(\.\d\d\d)*(,\d+)?)([,:;)]*)(?=[ .\n])', content)
    for numero in numeros:
        content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + numero[3] + re.escape(numero[4]) + re.escape(numero[7]) + r'(?=[ .\n])', representacionNumerica(numero[0]) + ' a ' + representacionNumerica(numero[4]) + numero[7], content, count=1)
    ######
    #Numeros simples
    numeros = re.findall(r'(?<=[ (])((\d+,?)*\d*\.\d+)(?=([ .,;)]|$))', content)
    for numero in numeros:
        if len(numero[0].split('.')[1]) != 3:
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'(?=([ .,;)]|$))', numero[0].replace(',', '#').replace('.', ',').replace('#', '.'), content, count=1)
    numeros = re.findall(r'(?<=[ (])(\d+(,\d\d\d)+)(?=[ .,;)])', content)
    for numero in numeros:
        if numero[0][-1] == '0':
            content = re.sub(r'(?<=[ (])' + numero[0] + r'(?=[ .,;)])', numero[0].replace(',', '.'), content, count=1)
    #No debe funcionar en /1/
    numeros = re.findall(r'(?<=[ (])((- ?)?(\d+(\.\d\d\d)*(,\d+)?))(?=([ /:;)]|$))', content)
    for numero in numeros:
        if re.search(r'(?<=[ (])' + re.escape(numero[0]) + r'(?=/)', content):
            if re.search(r'(?<=[ (])' + re.escape(numero[0]) + r'/(?=\d)', content) or re.search(r'(?<=\n)[^\n]*[^\w](fórmula|gráfico)[^\w][^\n]*( |\()' + re.escape(numero[0]) + r'/[^\n]*(?=\n)', content) or re.search(r'(?<=\n)[^\n]*( |\()' + re.escape(numero[0]) + r'/[^\n]*[^\w](fórmula|gráfico)[^\w][^\n]*(?=\n)', content):
                content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'/', representacionNumerica(numero[0]) + ' entre ', content, count=1)
            else:
                content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'/', representacionNumerica(numero[0]) + ' por ', content, count=1)
        elif re.search(r'(?<=[ ])' + re.escape(numero[0]) + r'(?=([ :;)]|$))', content):
            content = re.sub(r'(?<= )' + re.escape(numero[0]) + r'(?=([ :;)]|$))', representacionNumerica(numero[0]), content, count=1)
        else:
            content = re.sub(r'(?<=[(])' + re.escape(numero[0]) + r'(?=([ :)]|$))', representacionNumerica(numero[0]), content, count=1)
    numeros = re.findall(r'(?<=[ (])((- ?)?(\d+(\.\d\d\d)*(,\d+)?))(\.|,)(?=( |$|\n))', content)
    for numero in numeros:
        content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + re.escape(numero[5]), representacionNumerica(numero[0]) + numero[5], content, count=1)
    numeros = re.findall(r'/((- ?)?(\d+(\.\d\d\d)*(,\d+)?))(?=([ :;)]|$))', content)
    for numero in numeros:
        content = re.sub(r'/' + re.escape(numero[0]) + r'(?=([ :;)]|$))', ' entre ' + representacionNumerica(numero[0]), content, count=1)
    '''
    numeros = re.findall(r'(?<=[ (/])((- ?)?(\\d+(\\.\\d\\d\\d)*(,\\d+)?))(?=([ /:;).,]|$))', content)
    for numero in numeros:
        if re.search(r'(?<=[ (])' + re.escape(numero[0]) + r'(?=/)', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'/', representacionNumerica(numero[0]) + ' por ', content, count=1)
        elif re.search(r'(?<=/)' + re.escape(numero[0]) + r'(?=([ :;)]|$))', content):
            content = re.sub(r'/' + re.escape(numero[0]) + r'(?=([ :;)]|$))', ' entre ' + representacionNumerica(numero[0]), content, count=1)
        elif re.search(r'(?<=[ (])' + re.escape(numero[0]) + r'([.,](?=( |$|\n))|(?=([ :;)]|$)))', content):
            content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + r'(?=([ /:;).,]|$))', representacionNumerica(numero[0]), content, count=1)
    '''
    numeros = re.findall(r'·((- ?)?(\d+(\.\d\d\d)*(,\d+)?))(?=([ :;)]|$))', content)
    for numero in numeros:
        content = re.sub(r'·' + re.escape(numero[0]) + r'(?=([ :;)]|$))', ' por ' + representacionNumerica(numero[0]), content, count=1)
    while re.search(r' +\n|\n[ :;]+', content):
        content = re.sub(r' +\n|\n[ :;]+', r'\n', content)
    while re.search(r'(^[^¿]*)\?', content):
        content = re.sub(r'(^[^¿]*)\?', r'\1', content)
    content = re.sub(r'(?<![\w-])(\(([^()]+ [^()]+)\)/\(([^()]+ [^()]+)\))(?![\w-])', r'\1 entre \2', content)
    content = re.sub(r'(?<![\w-])((mili)?gramos)%', r'\1 por cada cien mililitros', content)
    content = re.sub(r' - (\w+ ?[,()])', r'\1', content)
    content = re.sub(r'\)\.(?![\n ])', r').', content)
    content = re.sub(r'\n+(·+)\n+', r'\n\1', content)
    content = re.sub(r'\.( *\.)+', r'.', content)
    content = re.sub(r',( *,)+', r',', content)
    content = re.sub(r':( *:)+', r':', content)
    content = re.sub(r'\n\n+', r'\n', content)
    content = re.sub(r' +\)', r')', content)
    content = re.sub(r'\( +', r'(', content)
    content = re.sub(r' +\.', r'.', content)
    content = re.sub(r'· +', r'·', content)
    content = re.sub(r'{ +', r'{', content)
    content = re.sub(r' +}', r'}', content)
    content = re.sub(r' +:', r':', content)
    content = re.sub(r' +;', r';', content)
    content = re.sub(r' +,', r',', content)
    content = re.sub(r'  +', r' ', content)
    content = content.replace('σ', 'Sigma')
    content = content.replace('.)', ')')
    content = content.replace('.,', ';')
    content = content.replace('.;', ';')
    content = content.replace('%', '')
    titulo, content = content[1:].split('\n', 1)
    if not len(content):
        return [], ""
    for i in [':', 'también', 'conocida']:
        titulo = titulo.split(i)[0]
    for i in ['.', '?', '™', 'Definición de', 'Definición', '¿Qué es', 'Qué es la', 'qué es la']:
        titulo = titulo.replace(i, '')
    titulo = titulo.replace('/', ' por ')
    titulo = titulo.replace('&', 'y')
    titulo = re.sub(r'\((.*?) (.*?)\)', r'', titulo.strip())
    titulo = re.sub(r'(^[^(]*)\)(.*?)$', r'\1', titulo)
    titulo = re.sub(r'^([eE]l|[lL]as?) ', r'', titulo)
    titulo = re.sub(r'\((.*?)\)', r'', titulo)
    titulo = re.sub(r'\[(.*?)\]', r'', titulo)
    titulo = re.sub(r'--+', r'-', titulo)
    for i in [' o ', ' u ']:
        titulos = titulo.split(i)
        if len(titulos) > 1:
            if titulos[0].find(', ') != -1:
                titulos = titulos[0].split(', ') + [titulos[1]]
            elif titulos[0].find(' ') != -1 and ('a' <= titulos[1][0] <= 'z' or len(titulos[1]) == 1) and titulos[0].split(' ')[0].lower() != titulos[1].split(' ')[0].lower():
                titulos[1] = titulos[0].split(' ')[0] + ' ' + titulos[1]
            break
    for j in [', ', '; ']:
        i = 0
        while i < len(titulos):
            if titulos[i].find(j) != -1:
                if ' y ' in titulo:
                    return [], ""
                partes = titulos[i].split(j)
                if len(partes[1]) and (partes[0].isupper() or partes[1].isupper()):
                    titulos.append(partes[1])
                    titulos[i] = partes[0]
                elif len(partes[1]) and partes[1][0] == '-':
                    if partes[0][-2:] in ['oa', 'ob']:
                       partes[0] = partes[0][:-1]
                    if partes[1][-2:] in ['aa', 'ab']:
                       partes[1] = partes[1][:-1]
                    if partes[0][-1] == 'o' and partes[1][-1] == 'a':
                        _bandera = True
                        for k in range(len(partes[1]) - 2, 0, -1):
                            if partes[0][-(len(partes[1]) - k)] != partes[1][k]:
                                _bandera = False
                                break
                        if _bandera:
                            partes[0] = quitarGuiones(partes[0])
                            equivalentes[(partes[0][:-1] + partes[1][-1]).lower()] = partes[0].lower()
                        else:
                            colocar(equivalentes, partes)
                    else:
                        if partes[0][-1] == partes[1][1]:
                            parte = quitar_acentos(partes[0])
                            equivalentes[(parte + partes[1][2:]).lower()] = partes[0].lower()
                        elif partes[0][-1] != '-':
                            colocar(equivalentes, partes)
                    titulos[i] = partes[0]
                else:
                    titulos[i] = partes[1] + ' ' + partes[0]
            i += 1
    validos = ['0', '1', '2', '3' '4', '5' '6', '7', '8', '9', 'á', 'é', 'í', 'ó', 'ú', 'ñ']
    for i in range(len(titulos)-1, -1, -1):
        titulos[i] = quitarGuiones(titulos[i])
        if len(titulos[i]) == 1 or (len(titulos[i]) in (2, 3) and all(c not in validos for c in titulos[i])):
            del titulos[i]
            if not len(titulos):
                return [], ""
    content = re.sub(r'(^| )\([^()\n]*(\([^()\n]*(\([^()\n]*\)[^()\n]*)*\)[^()\n]*)*\)', r'', content)
    content = re.sub(r'(\n *|^ *)[^\n]*Algunos autores prefieren[^\n]+(?=(\n|$))', r'', content)
    content = re.sub(r'(\n *|^ *)El terapia de las? [^\n]+(?=(\n|$))', r'', content)
    content = re.sub(r' Por ejemplo, puede ser necesario [^.]+\.', r'', content)
    content = re.sub(r'(?<![.:])\n', r'.\n', content)
    content = re.sub(r'\n(Esta )', r' \1', content)
    content = content.replace(' - ', ' ')
    content = content.replace('- ', ' ')
    content = content.replace(' -', ' ')
    ####
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()Los términos ([^.,;]+)(, [^.,;]+)+ y ([^.,;]+) se usan con frecuencia de forma intercambiable, como si fueran sinónimos\.)(?=([ \n]|$))', content)
    for linea in iguales:
        _pt1 = linea[3].replace('(', '-').replace(')', '-').lower().strip()
        _pt2 = linea[5].replace('(', '-').replace(')', '-').lower().strip()
        pt1 = _pt1.replace('-', ' ')
        pt2 = _pt2.replace('-', ' ')
        if len(pt1) > 4 and len(pt2) > 4 and pt1 != pt2 and f' {pt1} ' not in f' {pt2} ' and f' {pt2} ' not in f' {pt1} ' and [_pt1, _pt2] not in igualaciones and [_pt2, _pt1] not in igualaciones:
            igualaciones.append([_pt1, _pt2])
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()[Cc]on frecuencia abreviado a ([^.;]+)[.;])(?=([ \n]|$))', content)
    for linea in iguales:
        if ' en ' not in linea[3]:
            _pt1 = re.sub(r'(,| [eyou]) [^\n]+', r'', linea[3])
            _pt1 = _pt1.replace('(', '-').replace(')', '-').split(' cuando ')[0].lower().strip()
            pt1 = _pt1.replace('-', ' ')
            pt2 = titulos[0].replace('-', ' ')
            if len(pt1) > 4 and len(pt2) > 4 and pt1 != pt2 and f' {pt1} ' not in f' {pt2} ' and f' {pt2} ' not in f' {pt1} ' and [titulos[0], _pt1] not in igualaciones and [_pt1, titulos[0]] not in igualaciones:
                igualaciones.append([titulos[0], _pt1])
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()[Pp]uede verse también ([^.;]+)[.,;])(?=([ \n]|$))', content)
    for linea in iguales:
        if ':' not in linea[3] and ' a ' not in linea[3] and linea[3][:3] != 'en ' and linea[3][:4] != 'con ' and linea[3][:5] != 'todo ':
            _pt1 = re.sub(r'(,| [eyou])[ ,][^\n]+', r'', f' {linea[3]} ')
            _pt1 = _pt1.replace('(', '-').replace(')', '-').lower().strip()
            if _pt1[:3] == 'la ':
                _pt1 = _pt1.split()[-1]
            pt1 = _pt1.replace('-', ' ')
            pt2 = titulos[0].replace('-', ' ')
            if len(pt1) > 4 and len(pt2) > 4 and pt1 != pt2 and f' {pt1} ' not in f' {pt2} ' and f' {pt2} ' not in f' {pt1} ' and [titulos[0], _pt1] not in igualaciones and [_pt1, titulos[0]] not in igualaciones:
                igualaciones.append([titulos[0], _pt1])
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()(Coloquial|Sinónimos): ([^.,;]+)[.;])(?=([ \n]|$))', content)
    for linea in iguales:
        if ':' not in linea[4]:
            _pt1 = re.sub(r'(,| [eyou]) [^\n]+', r'', linea[4])
            _pt1 = _pt1.replace('(', '-').replace(')', '-').lower().strip()
            pt1 = _pt1.replace('-', ' ')
            pt2 = titulos[0].replace('-', ' ')
            if len(pt1) > 4 and len(pt2) > 4 and pt1 != pt2 and f' {pt1} ' not in f' {pt2} ' and f' {pt2} ' not in f' {pt1} ' and [titulos[0], _pt1] not in igualaciones and [_pt1, titulos[0]] not in igualaciones:
                igualaciones.append([titulos[0], _pt1])
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()(((Coloquial|Desuso|Locución):? )?igual a|Sinónimos:) ([^\n.]+)[.;])(?=([ \n]|$))', content)
    for linea in iguales:
        if ':' not in linea[6]:
            _pt1 = re.sub(r'(,| [eyou]) [^\n]+', r'', linea[6])
            _pt1 = _pt1.replace('(', '-').replace(')', '-').replace('_', '-').split('^{a}')[0].split('^{b}')[0].lower().strip('-').strip()
            pt1 = _pt1.replace('-', ' ')
            pt2 = titulos[0].replace('-', ' ')
            if len(pt1) > 4 and len(pt2) > 4 and pt1 != pt2 and f' {pt1} ' not in f' {pt2} ' and f' {pt2} ' not in f' {pt1} ' and [titulos[0], _pt1] not in igualaciones and [_pt1, titulos[0]] not in igualaciones:
                igualaciones.append([titulos[0], _pt1])
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    iguales = re.findall(r'(; +|\. +|\n *|^ *)(()Plural([^.;]+)[.;])(?=([ \n]|$))', content)
    for linea in iguales:
        if ':' not in linea[3]:
            _pt1 = re.sub(r'(,| [eyou]) [^\n]+', r'', linea[3])
            plural = _pt1.replace('(', '-').replace(')', '-').replace('irregular', '').replace('-', ' ').strip().lower()
            if plural != titulos[0].replace('-', ' '):
                equivalentes[plural] = titulos[0]
        content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Los síntomas [^.,;:]+ pueden( variar en intensidad y pueden)? incluir|[^.,;:]+ incluyen?|Existen varias formas|[^.,;:]+ está compuesto por los siguientes órganos y estructuras|Entre los [^.,;:]*tipos [^.,;:]+ se encuentran|Histológicamente [^.,;:]+ se clasifica en [^.,;:]+ tipos|Los más relevantes son|[^.,;:]+ pueden actuar de varias maneras, incluyendo|[^.,;:]+ es la siguiente):))(?=(\n|$))', rf'#', content)
    content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Por ejemplo|Sin embargo|También|En resumen|Por lo tanto|Además|Por otro lado|No obstante|En conclusión|Asimismo|A lo (longitud|largo) de la historia|(Cabe destacar|Es importante (recordar|señalar|destacar)) que|En general|Generalmente|Por el contrario|Así|Por último|En su definición más general|En este contexto|Independientemente del contexto|En algunos casos?|De todas formas|A veces|Al mismo tiempo|Por ello|Finalmente|Dependiendo de las circunstancias|Por eso|En ocasiones|Del mismo modo|En contraste|Concretamente|En definitiva|En otras palabras),( (es importante mencionar que|([^\n,.]{{19}})\.))?))(?=([ \n]|$))', rf'#', content)
    content = sustraer(rf'(, +|\n *|^ *)((()(cuando por el contexto se sobrentiende|especialmente en el registro coloquial|y con la excepción de este último|pues|como su propio nombre indica|sobre todo|etcétera|en su caso|es decir|también|sin finalidad|a veces|entre otras|en particular|por lo tanto|por extensión|por otro lado|por lo general|en ocasiones|en algunos casos?)([.,;])))(?=([ \n]|$))', rf'#', content)
    content = re.sub(r'[\n ]+\n[\n ]+|[\n ]+\n|\n[\n ]+', r'\n', content)
    content = re.sub(r' +(\.|,|;)', r'\1', content)
    content = re.sub(r'[.,;]\.', r'.', content)
    content = re.sub(r';\n', r'.\n', content)
    content = re.sub(r'  +', r' ', content)
    content = content.replace('~ ,', '~')
    content = content.replace(',,', ',')
    return titulos, content.strip()

def limpiar_conjunto(path, titulos_finales, path2, equivalentes, igualaciones):
    no_permitidos = {'nelfinavir', 'síndrome de lacomme', 'ciron', 'saquinavir', 'complicaciones de la viruela loco', 'pralidoxima', 'vih 2', 'sulindaco', 'ritonavir', 'zona interior', 'creatinfosfoquinasa', 'metal', 'antimonio', 'órgano intracelular nacional de salud', 'necrólisis epidérmico', 'transducción de señales de sustancias peligrosas', 'sucralfato', 'supuración esquelético', 'octreotida', 'minerva', 'turpentina', 'mensaje neural', 'anexina', 'sindemia', 'proteína tau', 'loa', 'anillo estomacal', 'altura voluntaria', 'alto voluntaria', 'apatito', 'ortosis dinámico', 'clonorchis sinensis', 'dato censurado', 'prótesis autoexpansible', 'isofosfamida', 'transtorno bipolar', 'membrana germinativo', 'clasificación baltimore', 'cinesia estereotipado', 'aparato fusiforme', 'agencia mundial antidopaje', 'fosforilcolina', 'hormigueo en los dedos', 'próstesis autoexpansible', 'síndrome del asa ciego', 'nudo de cirujano', 'tensoactivo neumónico', 'enajenación mental transitorio', 'deferroxamina', 'síndrome neumático agudo grave', 'compensación de dosis génico', 'válvula connivente', 'dermatitis ocre', 'coronavirus dos del síndrome neumático agudo grave perlada del cabeza del pene', 'región celiaquía', 'banco de huesos', 'callo de ender', 'indice de katz', 'resultados de un psicoanálisis de sangre', 'tejido óseo incisivo', 'quiste hidatídico', 'vaso arterial rostral', 'disco intercalado', 'transducción de señales de substancia peligrosas', 'rastreo de contactos', 'etretinato', 'acrodermatitis enteropática', 'triantereno', 'desarrollo en capas', 'ano imperforado', 'escintilador', 'indice de rosner', 'vakog', 'penfigoide cicatricial', 'tricobezoar', 'elmex', 'metoxaleno', 'faja ortopeda', 'toser', 'pitiriasisrubra pilaris'}
    for nombre_archivo in os.listdir(path):
        if os.path.isfile(path + nombre_archivo) and nombre_archivo.endswith(".txt"):
            with open(path + nombre_archivo, 'r', encoding='utf-8') as file:
                content = file.read()
            titulos, content = limpiar_html_abreviaturas(content, nombre_archivo[:-4], equivalentes, igualaciones)
            if len(titulos) and len(content):
                titulos_finales.add(titulos[0])
                for titulo in titulos[1:]:
                    equivalentes[titulo] = titulos[0]
                if os.path.isfile(path2 + titulos[0] + '.txt'):
                    with open(path2 + titulos[0] + '.txt', 'a', encoding='utf-8') as fl:
                        fl.write('\n' + content)
                elif titulos[0].replace('-', ' ') not in no_permitidos:
                    with open(path2 + titulos[0] + '.txt', 'w', encoding='utf-8') as fl:
                        fl.write(content)

def atomizar(_tokens):
    invalidos = {']', '[', '.', ',', '·', ':', ';', '¡', '!', '¿', '?', '(', ')', '<', '>', '=', '/', '^', '*'}
    tokens = list()
    for token in _tokens:
        i = 0
        _token = token
        while i < len(_token) and _token[i] in invalidos:
            i += 1
        if i:
            tokens.append(_token[:i])
            _token = _token[i:]
        i = len(_token) - 1
        while i > -1 and _token[i] in invalidos:
            i -= 1
        i += 1
        j = 0
        while j < i:
            if _token[j] in ['_', '-']:
                if j:
                    tokens.append(_token[:j])
                tokens.append(_token[j])
                _token = _token[j + 1:]
                i -= j + 1
                j = -1
            j += 1
        if i:
            tokens.append(_token[:i])
        if i < len(_token):
            tokens.append(_token[i:])
        tokens.append(' ')
    if not len(tokens):
        print(_tokens)
    else:
        del tokens[-1]
    return tokens

def modificar(terminos, equivalentes, tokens):
    cambio = True
    utimo = ''
    cont = 0
    while cambio:
        #'''
        cont += 1
        if cont > 8:
            print(f'{cont}: {tokens}')
            if cont > 10:
                print(f'alto, eliminar {ultimo} = {equivalentes[ultimo]}')
                del equivalentes[ultimo]
                cont = 1
        #'''
        cambio = False
        _tokens = tokens[:]
        limite = len(_tokens)
        tokens = list()
        i = 0
        while i < limite:
            posicion = -1
            explorador = i
            termino = _tokens[i].lower()
            while termino in terminos:
                if terminos[termino] == 1 and termino in equivalentes:
                    posicion = explorador
                explorador += 1
                if explorador == limite:
                    break
                termino = ''.join(_tokens[i:explorador + 1]).replace('-', ' ').replace('_', ' ').lower()
            if posicion > -1:
                union = ''.join(_tokens[i:posicion + 1])
                limpio = union.replace('-', ' ').replace('_', ' ').lower()
                if equivalentes[limpio].replace('-', ' ').replace('_', ' ') == limpio:
                    mapeo = equivalentes[limpio] + ' '
                    content2 = ""
                    j = 0
                    for k in range(len(mapeo)):
                        if mapeo[k] in [' ', '-']:
                            if mapeo[j:k] in equivalentes:
                                content2 += equivalentes[mapeo[j:k]] + mapeo[k]
                                if equivalentes[mapeo[j:k]] != mapeo[j:k]:
                                    ultimo = mapeo[j:k]
                                    cambio = True
                            else:
                                content2 += mapeo[j:k+1]
                            j = k + 1
                    content2 = content2[:-1]
                else:
                    cambio = True
                    ultimo = limpio
                    content2 = equivalentes[limpio]
                tokens.extend(atomizar(content2.split()))
                i = posicion
            else:
                tokens.append(_tokens[i])
            i += 1
    _tokens = list()
    for i in range(len(tokens)):
        _tokens.append(tokens[i])
        for j in range(1, 11, 2):
            if len(_tokens) > 2*j and _tokens[-(2*j+1):-(j+1)] == _tokens[-j:] and ',' not in _tokens[-j:] and _tokens[-(j+1)] == ' ' and _tokens[-1] not in [' ', '/']:
                bien = True
                for k in range(len(_tokens)-j+1, len(_tokens), 2):
                    if _tokens[k] not in [' ', '-', '_'] or _tokens[k-1] in [' ', '/']:
                        bien = False
                        break
                if bien:
                    del _tokens[-(j+1):]
    tokens = list()
    for i in range(len(_tokens)):
        tokens.append(_tokens[i])
        '''
        for j in range(1, 11, 2):
            if len(tokens) > 2*(j+1) and quitar_acentos(''.join(tokens[-(2*j+3):-(j+3)])) == quitar_acentos(''.join(tokens[-(j+1):-1])) and ''.join(tokens[-(j+3):-(j+1)]) == ' (' and tokens[-1] in [')', ').', '),']:
                #print(f'${tokens[-(2*j+3):]}$')
                bien = True
                for k in range(len(tokens)-j, len(tokens)-1, 2):
                    if tokens[k] not in [' ', '-', '_'] or tokens[k-1] in [' ', '/']:
                        bien = False
                        break
                if bien:
                    extra = tokens[-1][1:]
                    del tokens[-(j+3):]
                    if len(extra):
                        tokens.append(extra)
        '''
    _tokens = list()
    for i in range(len(tokens)):
        _tokens.append(tokens[i])
        for j in range(1, 11, 2):
            if len(_tokens) > 2*j+5 and _tokens[-(2*j+3):-(j+3)] == _tokens[-(j+1):-1] and ''.join(_tokens[-(2*j+5):-(2*j+3)]) in [': ', ', '] and ''.join(_tokens[-(j+3):-(j+1)]) == ', ' and _tokens[-1] == ',':
                bien = True
                for k in range(len(_tokens)-j, len(_tokens)-1, 2):
                    if _tokens[k] not in [' ', '-', '_'] or _tokens[k-1] in [' ', '/']:
                        bien = False
                        break
                if bien:
                    del _tokens[-(j+2):]
    return f'{''.join(_tokens)}\n'

def buscar_lider(vertice, equivalentes):
    _vertice = vertice.replace('-', ' ')
    if _vertice not in equivalentes:
        equivalentes[_vertice] = vertice
    elif equivalentes[_vertice].replace('-', ' ') != _vertice:
        equivalentes[_vertice] = buscar_lider(equivalentes[_vertice], equivalentes)
    return equivalentes[_vertice]

def modificar_seguidores(vertice, lider, equivalentes):
    _vertice = vertice.replace('-', ' ')
    if _vertice in equivalentes and equivalentes[_vertice].replace('-', ' ') != _vertice:
        modificar_seguidores(equivalentes[_vertice], lider, equivalentes)
    equivalentes[_vertice] = lider

def actualizar_equivalentes(equivalentes, terminos):
    terminos.clear()
    for mapeo in list(equivalentes):
        buscar_lider(mapeo, equivalentes)

    for mapeo in list(equivalentes):
        pt1 = mapeo.replace('-', ' ')
        pt2 = equivalentes[mapeo].replace('-', ' ')
        if pt1 != pt2 and (' '+pt1+' ' in ' '+pt2+' ' or ' '+pt2+' ' in ' '+pt1+' '):
            del equivalentes[mapeo]

    for clave in equivalentes:
        locucion = clave.split()
        terminos[clave] = 1

        while len(locucion) > 1:
            del locucion[-1]
            term = ' '.join(locucion)
            terminos[term + ' '] = 0
            if term in terminos:
                break
            terminos[term] = 0

    for mapeo in list(equivalentes):
        pt1 = mapeo.replace('-', ' ')
        pt2 = equivalentes[mapeo].replace('-', ' ')
        tokens = pt2.split()
        utilizados = set()
        visitados = set()
        cont = 1

        while cont > 0:
            cont += 1
            if ' '.join(tokens) in visitados:
                del equivalentes[mapeo]
                break
            visitados.add(' '.join(tokens))
            limite = len(tokens)
            _tokens = tokens[:]
            tokens = list()
            cont *= -1
            i = 0

            while i < limite:
                bandera = True

                while bandera:
                    posicion = -1
                    explorador = i
                    bandera = False
                    termino = _tokens[i]

                    while termino in terminos:
                        if terminos[termino] == 1:
                            posicion = explorador
                        explorador += 1
                        if explorador == limite:
                            break
                        termino = ' '.join(_tokens[i:explorador + 1])

                    if posicion > -1 and ' '.join(_tokens[i:posicion + 1]) not in equivalentes:
                        terminos[' '.join(_tokens[i:posicion + 1])] = 0
                        bandera = True
                
                if posicion > -1:
                    content2 = list()
                    limpio = ' '.join(_tokens[i:posicion + 1])
                    _equivalencia = equivalentes[limpio].replace('-', ' ')
                    if _equivalencia == limpio:
                        for parte in _equivalencia.split():
                            if parte in equivalentes:
                                content2.extend(equivalentes[parte].replace('-', ' ').split())
                                if equivalentes[parte] != parte:
                                    if parte in utilizados:
                                        #print(f'Eliminacion {mapeo} = {equivalentes[mapeo]}')
                                        del equivalentes[mapeo]
                                        cont = 0
                                        break
                                    utilizados.add(parte)
                                    if cont < 0:
                                        cont *= -1
                            else:
                                content2.append(parte)
                        if cont == 0:
                            break
                    else:
                        if cont < 0:
                            cont *= -1
                        if limpio in utilizados:
                            del equivalentes[mapeo]
                            cont = 0
                            break
                        utilizados.add(limpio)
                        content2.extend(_equivalencia.split())
                    tokens.extend(content2)
                    i = posicion
                else:
                    tokens.append(_tokens[i])
                i += 1

    terminos.clear()
    for clave in equivalentes:
        locucion = clave.split()
        terminos[clave] = 1

        while len(locucion) > 1:
            del locucion[-1]
            term = ' '.join(locucion)
            terminos[term + ' '] = 0
            if term in terminos:
                break
            terminos[term] = 0

def reacomodar(path2, nombre_archivo, palabras_objetivo):
    with open(path2 + nombre_archivo, 'r', encoding='utf-8') as file:
        content = file.read()
    eliminaciones = re.findall(rf'(((\. +|\n *|^ *)())(|([^.]+:|(([Ss]in embargo|[Pp]or ejemplo), )?[^.,; ]+(( [^.,; ]+){{0,10}}),) )((([Aa]l|[Uu]na|(([Aa]demás|[Dd]e hecho|[Aa] pesar de estos riesgos|[Ss]in embargo|[Gg]eneralmente|([Ee]s (importante|relevante)|[Cc]abe) destacar que|[Ss]i bien),? )?([Ee]l|[Ll][ao]s?)( término| palabra)?) ([^,.;:()]*?)s?)( (también|propiamente dicha),?)?( \(?(símbolo|o) ([^,.;:()]*?)\)?,?|, (por otro lado|en cambio|[^.,;]*en el contexto [^.,;]+),)?)((, ([^.,;]*en el contexto[^.,;]+|responsable de[^.,;]+),)? (es una|es|se|fue|solo|proviene|generalmente|son|más conocidas|consiste|designa|está|sirve|corresponde|juega|tiene|comienza|nos|pasa|funciona|utiliza|desempeña|completa|lleva|proporciona|hace|impide|deriva|implica|requiere|refiere|investiga|trabaja),? (([^\n.]{{43}})[^\n]+)))(?=(\n|$))', content)
    for linea in eliminaciones:
        _pt1 = linea[19].lower()
        _pt2 = linea[24].lower()
        if all(t not in f' {linea[29]} {linea[31]} ' for t in [' en estos ', ' el más frecuente ', ' son los ', ' la enfermedad ', ' los síntomas ']) and ' su ' not in linea[4] and len(linea[30]) > 68 and (_pt1 == _pt2 or f' {_pt1} ' not in f' {_pt2} '):
            texto = ''
            _lin = len(_pt1)
            cont = _pt1.count(' ')
            if ' ' in nombre_archivo:
                texto = re.sub(rf'([^.]+\.)+([^.]+(?i:{re.escape(nombre_archivo[:-4])})[^\n]+)|[^\n]+', rf'\2', linea[26], count=1)
            if _pt1 in palabras_objetivo and ((cont > 2 and _lin > 25) or (cont == 2 and _lin > 23) or (cont == 1 and _lin > 26) or (cont == 0 and _lin > 16)):
                content = re.sub(rf'{re.escape(linea[0])}(?=(\n|$))', rf'{linea[2]}{texto}', content, count=1)
            elif _pt1 in palabras_objetivo and linea[29] in ['trabaja'] and ((cont > 2 and _lin > 25) or (cont == 2 and _lin > 23) or (cont == 1 and _lin > 16) or (cont == 0 and _lin > 16)):
                content = re.sub(rf'{re.escape(linea[0])}(?=(\n|$))', rf'{linea[2]}{texto}', content, count=1)
            elif _pt1 in palabras_objetivo and linea[29] in ['es una'] and ((cont > 2 and _lin > 0) or (cont == 2 and _lin > 0) or (cont == 1 and _lin > 0) or (cont == 0 and _lin > 5)):
                content = re.sub(rf'{re.escape(linea[0])}(?=(\n|$))', rf'{linea[2]}{texto}', content, count=1)
    content = re.sub(r'[\n ]+\n[\n ]+|[\n ]+\n|\n[\n ]+', r'\n', content)
    content = re.sub(r'  +', r' ', content)
    content = content.replace(',,', ',')
    content = content.replace(',.', '.')
    content = content.replace(';.', '.')
    content = content.replace('..', '.')
    content = content.replace(' .', '.')
    content = content.replace(' ,', ',')
    content = content.strip()
    if content != '':
        with open(path2 + nombre_archivo, 'w', encoding='utf-8') as fl:
            fl.write(content)
    elif os.path.isfile(path2 + nombre_archivo):
        os.remove(path2 + nombre_archivo)
    for linea in eliminaciones:
        _pt1 = linea[19].lower()
        _pt2 = linea[24].lower()
        if all(t not in f' {linea[29]} {linea[31]} ' for t in [' en estos ', ' el más frecuente ', ' son los ', ' la enfermedad ', ' los síntomas ']) and ' su ' not in linea[4] and len(linea[30]) > 68 and (_pt1 == _pt2 or f' {_pt1} ' not in f' {_pt2} '):
            texto = ''
            bandera = False
            _lin = len(_pt1)
            cont = _pt1.count(' ')
            if ' ' in nombre_archivo:
                texto = re.sub(rf'([^.]+\.)+([^.]+(?i:{re.escape(nombre_archivo[:-4])})[^\n]+)|[^\n]+', rf'\2', linea[26], count=1)
            if _pt1 in palabras_objetivo and ((cont > 2 and _lin > 25) or (cont == 2 and _lin > 23) or (cont == 1 and _lin > 26) or (cont == 0 and _lin > 16)):
                bandera = True
            elif _pt1 in palabras_objetivo and linea[29] in ['trabaja'] and ((cont > 2 and _lin > 25) or (cont == 2 and _lin > 23) or (cont == 1 and _lin > 16) or (cont == 0 and _lin > 16)):
                bandera = True
            elif _pt1 in palabras_objetivo and linea[29] in ['es una'] and ((cont > 2 and _lin > 0) or (cont == 2 and _lin > 0) or (cont == 1 and _lin > 0) or (cont == 0 and _lin > 5)):
                bandera = True
            if bandera:
                with open(f'{path2}{linea[19].lower()}.txt', 'a', encoding='utf-8') as file:
                    file.write(f'\n{linea[4]}~{linea[10]}~ {linea[26][:len(linea[26])-len(texto)]}'.replace('~ ,', '~').replace('  ', ' '))
                reacomodar(path2, f'{linea[19].lower()}.txt', palabras_objetivo)

def sustraer(original, nuevo, fuente):
    if not len(fuente):
        return fuente
    _fuente = [fuente]
    _len = len(fuente)
    _fuente[-1] = re.sub(original, rf'{nuevo.replace('#', r'\1')}%', _fuente[-1], count=1)
    while len(_fuente[-1]) != _len:
        _fuente.append('')
        _fuente[-2:] = _fuente[-2].split('%', 1)
        _len = len(_fuente[-1])
        _fuente[-1] = re.sub(original, rf'{nuevo.replace('#', r'\1')}%', _fuente[-1], count=1)
    return ''.join(_fuente)

def limpiar_fuentes():
    no_intercambiables = {'psicógeno', 'tronco', 'ligadura', 'hipercaptante', 'adenoide', 'medio', 'vientre', 'trepanación', 'escáner', 'característico', 'prueba', 'angustia', 'sangría', 'infección', 'corte', 'opioideo', 'pálido', 'talla', 'medicamento', 'grupo', 'orificio', 'sulindaco', 'garganta', 'técnico', 'ictus', 'oncocito', 'título', 'operación', 'septo', 'menorragia', 'hipertiroideo', 'psique', 'médico', 'respuesta', 'solución', 'variz', 'dolor', 'amigdalitis', 'elefantiasis', 'reflejado', 'mental', 'brida', 'nevo melanocítico', 'extremidad', 'ecografía', 'vasculógeno', 'interior', 'hematoma', 'ostomía', 'marcha', 'hinchazón', 'precursor', 'biopsia excisional', 'receptor', 'oxigenoterapia', 'gonorrea', 'malar', 'radioterapia', 'residuo', 'sensitivo', 'sínfisis', 'gotiera', 'cortex', 'cristalino', 'transporte pasivo', 'obstrucción', 'supuración', 'histeria', 'lobanillo', 'tuberculoso', 'tóxico', 'hipercifosis', 'reforzamiento', 'óvulo', 'testigo', 'álcali', 'radiación', 'biauricular', 'aparato', 'anular', 'bastón', 'complejo sintomático', 'frecuencia', 'derivación', 'ansiolítico', 'dermoabrasión', 'sueño', 'shunt', 'convertir', 'hiperqueratosis', 'eminencia', 'cateterismo', 'menstruación', 'atenuación', 'enfermedad de von recklinghausen', 'somnolencia', 'obeso', 'extremo', 'anestesiador', 'disminución', 'digital', 'pituitario', 'físico', 'cuentagotas', 'cólera', 'oclusivo', 'priorización', 'citología', 'dureza', 'sustitución', 'barotrauma', 'úlcera', 'tetracosactida', 'orden', 'crisis hipertiroidea', 'radiografía', 'clavo', 'malformación de chiari', 'polaridad', 'asepsia', 'dependencia psíquica', 'reagudización', 'fase estacionaria', 'linfocito b', 'balón', 'vértice', 'efluvio', 'nefroscopio', 'maniquí', 'obstetricia', 'biovar', 'citocinina', 'barbitúrico', 'corona', 'mayor', 'pulpa', 'bioensayo', 'largo', 'fluoroscopia', 'enmascaramiento', 'reservorio', 'postura', 'trauma psíquico', 'superior', 'estenosis', 'displasia', 'arcada', 'trígono', 'linfogranuloma', 'tumoración', 'deposición', 'organizador', 'diabetes mellitus', 'azucarado', 'seborrea', 'cóctel', 'paladar', 'terapia electroconvulsiva', 'caries', 'acceso', 'espina', 'médula', 'sensación', 'injerto', 'energía calorífica', 'célula progenitora', 'arcosegundo', 'conciencia', 'basófilo'}
    no_permitidos = {'nelfinavir', 'síndrome de lacomme', 'ciron', 'saquinavir', 'complicaciones de la viruela loco', 'pralidoxima', 'vih 2', 'sulindaco', 'ritonavir', 'zona interior', 'creatinfosfoquinasa', 'metal', 'antimonio', 'órgano intracelular nacional de salud', 'necrólisis epidérmico', 'transducción de señales de sustancias peligrosas', 'sucralfato', 'supuración esquelético', 'octreotida', 'minerva', 'turpentina', 'mensaje neural', 'anexina', 'sindemia', 'proteína tau', 'loa', 'anillo estomacal', 'altura voluntaria', 'alto voluntaria', 'apatito', 'ortosis dinámico', 'clonorchis sinensis', 'dato censurado', 'prótesis autoexpansible', 'isofosfamida', 'transtorno bipolar', 'membrana germinativo', 'clasificación baltimore', 'cinesia estereotipado', 'aparato fusiforme', 'agencia mundial antidopaje', 'fosforilcolina', 'hormigueo en los dedos', 'próstesis autoexpansible', 'síndrome del asa ciego', 'nudo de cirujano', 'tensoactivo neumónico', 'enajenación mental transitorio', 'deferroxamina', 'síndrome neumático agudo grave', 'compensación de dosis génico', 'válvula connivente', 'dermatitis ocre', 'coronavirus dos del síndrome neumático agudo grave perlada del cabeza del pene', 'región celiaquía', 'banco de huesos', 'callo de ender', 'indice de katz', 'resultados de un psicoanálisis de sangre', 'tejido óseo incisivo', 'quiste hidatídico', 'vaso arterial rostral', 'disco intercalado', 'transducción de señales de substancia peligrosas', 'rastreo de contactos', 'etretinato', 'acrodermatitis enteropática', 'triantereno', 'desarrollo en capas', 'ano imperforado', 'escintilador', 'indice de rosner', 'vakog', 'penfigoide cicatricial', 'tricobezoar', 'elmex', 'metoxaleno', 'faja ortopeda', 'toser', 'pitiriasisrubra pilaris'}
    path2 = 'definiciones_limpias/'
    palabras_objetivo = set()
    equivalentes = dict()
    igualaciones = list()
    frecuencias = dict()
    diferentes = set()
    _titulos = dict()
    terminos = dict()
    plurales = set()
    titulos = set()

    for elemento in os.listdir(path2):
        ruta_completa = os.path.join(path2, elemento)
        if os.path.isfile(ruta_completa):
            os.remove(ruta_completa)
    
    limpiar_conjunto('definiciones1 Clinica_Universitaria_de_Navarra/', titulos, path2, equivalentes, igualaciones)
    limpiar_conjunto('definiciones2 Medline/', titulos, path2, equivalentes, igualaciones)
    limpiar_conjunto('definiciones3 Real_Academia_Nacional_de_Medicina_de_España/', titulos, path2, equivalentes, igualaciones)
    limpiar_conjunto('definiciones4 CCM_Salud/', titulos, path2, equivalentes, igualaciones)

    for nombre_archivo in titulos:
        archivo = nombre_archivo.replace('-', ' ')
        if archivo.find(' ') != -1 and (archivo not in equivalentes or nombre_archivo.count('-') > equivalentes[archivo].count('-')):
            equivalentes[archivo] = nombre_archivo

    for term1, term2 in igualaciones:
        if term1 not in no_intercambiables and term2 not in no_intercambiables:
            if term1 not in frecuencias:
                frecuencias[term1] = 0
            if term2 not in frecuencias:
                frecuencias[term2] = 0
            frecuencias[term1] += 1
            frecuencias[term2] += 1

    for term1, term2 in igualaciones:
        if term1 not in no_intercambiables and term2 not in no_intercambiables:
            if frecuencias[term1] > frecuencias[term2]:
                pt1 = term2
                pt2 = term1
            elif frecuencias[term1] < frecuencias[term2]:
                pt1 = term1
                pt2 = term2
            elif len(term1.replace('-', ' ').split()) > len(term2.replace('-', ' ').split()):
                pt1 = term2
                pt2 = term1
            elif len(term1.replace('-', ' ').split()) < len(term2.replace('-', ' ').split()):
                pt1 = term1
                pt2 = term2
            elif len(term1) > len(term2):
                pt1 = term2
                pt2 = term1
            elif len(term1) < len(term2):
                pt1 = term1
                pt2 = term2
            elif term1 > term2:
                pt1 = term2
                pt2 = term1
            elif term1 < term2:
                pt1 = term1
                pt2 = term2
            pt2 = buscar_lider(pt2, equivalentes)
            modificar_seguidores(pt1, pt2, equivalentes)

    actualizar_equivalentes(equivalentes, terminos)
    with open('terminos_equivalentes.txt', 'w', encoding='utf-8') as fl:
        for clave, valor in equivalentes.items():
            fl.write(f'{clave} = {valor}\n')

    for i in range(2):
        diferentes = set()
        _titulos = dict()
        plurales = dict()

        for nombre_archivo in os.listdir(path2):
            original = modificar(terminos, equivalentes, atomizar(nombre_archivo[:-4].split()))[:-1]
            if len(original) > 0 and original not in diferentes:
                diferentes.add(original)
                archivo = original.replace('-', ' ')
                _original = archivo[:]
                archivo = quitar_acentos(archivo)
                if archivo in _titulos:
                    __original = buscar_lider(original, equivalentes)
                    if len(_titulos[archivo][0]) > 0:
                        modificar_seguidores(_titulos[archivo][0], __original, equivalentes)
                    if len(_titulos[archivo][1]) > 0:
                       modificar_seguidores(_titulos[archivo][1], __original, equivalentes)
                _titulos[archivo] = [original, nombre_archivo[:-4]]

        diferentes = set()
        actualizar_equivalentes(equivalentes, terminos)
        with open('terminos_equivalentes.txt', 'w', encoding='utf-8') as fl:
            for clave, valor in equivalentes.items():
                fl.write(f'{clave} = {valor}\n')

        for nombre_archivo in os.listdir(path2):
            original = modificar(terminos, equivalentes, atomizar(nombre_archivo[:-4].split()))[:-1]
            if original not in diferentes:
                diferentes.add(original)
                transformacion = original.replace('-', ' ')
                if transformacion[-1] != 's':
                    transformacion += 's'
                if transformacion in plurales:
                    _original = original
                    if _original[-1] != 's':
                        _original += 's'
                    if len(_original[:-1]) > 3:
                        __original = buscar_lider(_original[:-1], equivalentes)
                        if len(_original) > 3:
                            modificar_seguidores(_original, __original, equivalentes)
                        if len(nombre_archivo[:-4]) > 3:
                            modificar_seguidores(nombre_archivo[:-4], __original, equivalentes)
                plurales[transformacion] = nombre_archivo[:-4]

        _titulos = dict()
        diferentes = set()
        actualizar_equivalentes(equivalentes, terminos)
        with open('terminos_equivalentes.txt', 'w', encoding='utf-8') as fl:
            for clave, valor in equivalentes.items():
                fl.write(f'{clave} = {valor}\n')

        for nombre_archivo in os.listdir(path2):
            original = modificar(terminos, equivalentes, atomizar(nombre_archivo[:-4].split()))[:-1]
            if len(original) > 4 and original not in diferentes:
                diferentes.add(original)
                transformacion = original.replace('-', ' ')
                if transformacion[-1] == 'a':
                    transformacion = transformacion[:-1] + 'o'
                if transformacion in _titulos:
                    _original = original
                    if _original[-1] == 'a':
                        _original = _original[:-1] + 'o'
                    __original = buscar_lider(_original, equivalentes)
                    modificar_seguidores(_original[:-1] + 'a', __original, equivalentes)
                _titulos[transformacion] = nombre_archivo[:-4]

        actualizar_equivalentes(equivalentes, terminos)
        with open('terminos_equivalentes.txt', 'w', encoding='utf-8') as fl:
            for clave, valor in equivalentes.items():
                fl.write(f'{clave} = {valor}\n')

    for clave, valor in equivalentes.copy().items():
        if ' de ' in valor and all(c not in valor for c in [' de la ', ' de las ']):
            parte1, parte2 = valor.split(' de ', 1)
            if parte2[-1] == 's':
                nuevaClave = f'{parte1} de las {parte2}'
            else:
                nuevaClave = f'{parte1} de la {parte2}'
            if nuevaClave not in equivalentes:
                equivalentes[nuevaClave] = valor
        if clave[-1] != 's' and ' de ' not in clave and ' del ' not in clave:
            _clave = clave.split()
            for it in range(len(_clave)):
                if _clave[it][-1] in ['a', 'e', 'i', 'o', 'u']:
                    _clave[it] += 's'
                else:
                    _clave[it] = quitar_acentos(_clave[it]) + 'es'
            nuevaClave = ' '.join(_clave)
            if nuevaClave not in equivalentes:
                equivalentes[nuevaClave] = valor

    actualizar_equivalentes(equivalentes, terminos)

    with open('terminos_equivalentes.txt', 'w', encoding='utf-8') as fl:
        for clave, valor in equivalentes.items():
            fl.write(f'{clave} = {valor}\n')
    print('Creacion de equivalencias lista')

    for nombre_archivo in os.listdir(path2):
        if not os.path.isfile(path2 + nombre_archivo):
            continue
        __content = ''
        with open(path2 + nombre_archivo, 'r', encoding='utf-8') as fl:
            parrafos = f'{nombre_archivo[:-4]}\n{fl.read()}'.split('\n')
        content = list()
        for parrafo in parrafos:
            text = modificar(terminos, equivalentes, atomizar(parrafo.split()))
            if text.strip() != '':
                content.append(text)
            else:
                print(f'Advertencia en {nombre_archivo} = {parrafo} = {parrafos}')
        parrafos = aplicar_sustituciones(''.join(content)).split('\n')
        del parrafos[-1]
        content = list()
        for parrafo in parrafos:
            content.append(modificar(terminos, equivalentes, atomizar(parrafo.split())))
        titulo = content[0][:-1]
        ___content = ''.join(content[1:])
        if nombre_archivo[:-4] != titulo:
            os.remove(path2 + nombre_archivo)
            if os.path.isfile(path2 + titulo + '.txt'):
                with open(path2 + titulo + '.txt', 'r', encoding='utf-8') as fl:
                    __content = fl.read()
        if titulo.replace('-', ' ') in no_permitidos:
            if os.path.isfile(path2 + titulo + '.txt'):
                os.remove(path2 + titulo + '.txt')
            continue
        content = ___content.split('\n')
        ___content = list()
        for i in range(len(content)-1):
            if content[i] not in ___content:
                ___content.append(content[i])
        content = f'\n{'\n'.join(___content)}\n'
        for tipo in ['Sinónimos', 'Desuso', 'Coloquial']:
            eliminaciones = re.findall(rf'(; +|\. +|\n *|^ *)((((){tipo}:( Coloquial:)?(( [^;.]+,)? (?i:{re.escape(titulo)}),){{0,20}}( [^;.]+,?)?( (?i:{re.escape(titulo)}))?)[.;]))(?=([ \n]|$))', content)
            for linea in eliminaciones:
                _linea = linea[1]
                while True:
                    if f': {titulo},' in _linea:
                        _linea = _linea.replace(f': {titulo},', f':')
                    elif f', {titulo},' in _linea:
                        _linea = _linea.replace(f', {titulo},', f',')
                    elif f', {titulo};' in _linea:
                        _linea = _linea.replace(f', {titulo};', f';')
                    elif f', {titulo}.' in _linea:
                        _linea = _linea.replace(f', {titulo}.', f'.')
                    else:
                        if f': {titulo};' in _linea or f': {titulo}.' in _linea:
                            _linea = ''
                        break
                content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', f'{linea[0]}{_linea}', content)
        for tipo in [['Con incidencia abreviado a', 'o'], ['Puede verse también', 'y']]:
            eliminaciones = re.findall(rf'(; +|\. +|\n *|^ *)((()((?i:{tipo[0]})) [^.;()]+ {tipo[1]} [^.;()]+[.;]))(?=([ \n]|$))', content)
            for linea in eliminaciones:
                _linea = linea[2]
                partes = _linea.split(f'{linea[4]} ', 1)[1].split(', ')
                for i in range(len(partes)):
                    if f' {tipo[1]} ' in partes[i]:
                        _partes = partes[i].split(f' {tipo[1]} ')
                        partes[i] = _partes[0]
                        partes.append(_partes[1])
                for i in range(len(partes)-1, -1, -1):
                    if partes[i] == titulo:
                        del partes[i]
                if len(partes):
                    content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', f'{linea[0]}{linea[4]} {partes[0]}.', content)
                elif len(partes) > 1:
                    content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', f'{linea[0]}{linea[4]} {', '.join(partes[:-1])} {tipo[1]} {partes[-1]}.', content)
                else:
                    content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', f'{linea[0]}', content)

        eliminaciones = re.findall(rf'( +|\n *|^ *)((()(es la ([^,.;:()]*?)) o ([^,.;:()]*?)([.,])))(?=([ \n]|$))', content)
        for linea in eliminaciones:
            if linea[5] == linea[6]:
                content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=([ \n]|$))', rf'{linea[0]}{linea[4]}{linea[7]}', content, count=1)
        eliminaciones = re.findall(rf'(\n *|^ *)((()([^.,;:]{{0,20}}):[^.]{{0,104}}\.))(?=(\n|$))', content)
        for linea in eliminaciones:
            if not re.search(r'[Oo]bservaciones|[Ss]inónimos|[Dd]esuso|[Cc]oloquial|[Aa]breviatura', linea[4]):
                content = re.sub(rf'{re.escape(linea[0])}{re.escape(linea[1])}(?=(\n|$))', rf'{linea[0]}', content, count=1)
        content = sustraer(rf'(\n *|^ *)((()[^.,;:]{{0,8}}\.))(?=(\n|$))', rf'#', content)
        content = sustraer(rf'( +|\n *|^ *)((()\(del inglés, [^.)]+\)[.,;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'( +|\n *|^ *)((()[^. ]+ corresponde a las siglas inglesas de [^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'( +|\n *|^ *)((()\([^.,;:()]+, por sus siglas en inglés\),))(?=([ \n]|$))', rf'#,', content)
        content = sustraer(rf'( +|\n *|^ *)((()como (?i:{re.escape(titulo)}) \(?(símbolo|o) ((?i:{re.escape(titulo)}))\)?,))(?=([ \n]|$))', rf'# {titulo},', content)
        content = sustraer(rf'( +|\n *|^ *)((()términos (?i:{re.escape(titulo)}) y (?i:{re.escape(titulo)}) son))(?=([ \n]|$))', rf'# {titulo} son', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Sinónimo(s:( Coloquial:)?| de) (?i:{re.escape(titulo)})(, a)?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(?i:{re.escape(titulo)})( y (?i:{re.escape(titulo)}))?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Por influencia del inglés, )?[Ss]e usa (más|mucho) la forma (extendida|siglada inglesa) (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*(Generalmente|Con incidencia|[Ss]e usa también) en plural( con el mismo significado[^.]*)?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Ver (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se recomienda precaución con este término, que se usa con significados muy distintos\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Puede suscitar rechazo por considerarse ((extranjerismo|redundante|anglicismo|término impropio|erróneo|calco)[^.]*|híbrido etimológico(\. No obstante, su uso es abrumador)?)\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()La RANME (desaconseja (su|el) uso( de este término)? (por considerarlo [^.]+|de extranjerismos innecesarios)|es partidaria de sustituir los extranjerismos crudos por alguno de sus sinónimos en español o equivalentes castellanizados|(recomienda|aconseja) precaución con el uso [^.;]+)\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()La terminología es sumamente confusa y varía mucho de una escuela a otra;))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Es en propiedad más correcto, pero de uso minoritario\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se escribe )?[Ee]n cursiva( y [^.]+)?(, por tratarse de un[^.,;]+)?[.;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Término similar a (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Solo admisible como vocablo latino\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Coloquial|Desuso):? igual a (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Error frecuente por influencia del inglés [^.(]+( \([^.)]+\))?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Es anglicismo incorrectamente formado|La transliteración (?i:{re.escape(titulo)}) es incorrecta) en español, pero de uso abrumador( por influencia del inglés)?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Como nombre propio, no suele ir precedido de artículo; si lo precisa, es masculino\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Su nombre común es (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()De(l| l(a|os)) (?i:{re.escape(titulo)})s?( \(?o (?i:{re.escape(titulo)})\)?,?)? o relacionado con (él|ell[oa]s?)\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Es|La) forma (castellanizada (es|del inglés): )?((?i:{re.escape(titulo)}), )?pero casi no se usa\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se usa (más el anglicismo (?i:{re.escape(titulo)})|frecuentemente con anteposición del[^.,;]+)\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Suele abreviarse a (?i:{re.escape(titulo)}) (o, más frecuentemente, (?i:{re.escape(titulo)})|en sus formas compuestas:)))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Localismo de uso restringido a algunas zonas de España; no se usa en América\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Ninguna de las traducciones propuestas ha logrado hasta ahora imponerse en la práctic[oa]\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()En forma siglada,[^.]*(?i:{re.escape(titulo)}) que (?i:{re.escape(titulo)});([^.]+\.)?))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Relativo a la (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Las variantes que incorporan el [^.]+ suscitan rechazo entre [^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(?i:{re.escape(titulo)}) empleado en la (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Es]s (error|equivocación) frecuente el uso [^\n]+))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Casi no se usa en plural, que es dudoso en español\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se desaconseja )?[Ee]n los textos (modernos|actuales)(;|, se considera anglicismo\.)))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()El (?i:{re.escape(titulo)}) es el (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()En latin la palabra (?i:{re.escape(titulo)}) significa (?i:{re.escape(titulo)})\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Se usa con incidencia de manera laxo como si fuera sinónimo de: (?i:{re.escape(titulo)})(, la)?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()Tiene también otros muchos sinónimos [^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.,;]*puede tener diversos significados en el campo de [^.,;]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Se usa mucho la acentuación [^.,;]+|La acentuación (llana|etimológica)[^.;]+)[.;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Tiene un marcado polimorfismo|[^.]+no son sinónimos estrictos[^.]+|Es sustantivo formado de modo irregular[^.]+|[^.]+más restringido, referido al[^.]+|En propiedad[^.]+que es impropio y confuso|[^.]*[Ss]e deriva del griego[^.]+que significa[^.]+|Prácticamente no se usa en singular|Se usa muy poco en [^.]+)\.))(?=([ \n]|$))', rf'#', content)
        #Reemplazos con patron
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()((Se confunde a menudo con el:|Su adjetivo es) [^.,;]+|(Nombre del|[^.]* es muy frecuente llamarlo simplemente) (?i:{re.escape(titulo)})|[^.]+ debe evitarse en el registro escrito|La (primera [^.,;]+ es mudo|yuxtaposición de sustantivos se considera anglicismo sintáctico)|En ([^.,;]+, también juega un papel importante|el ámbito de la medicina, tiene múltiples aplicaciones y significados, dependiendo del contexto en el que se utilice|el artículo se consignan solo algunos de los muchos sinónimos arcaicos [^.]+|España, [^.]+)|Esta (amplia gama de usos reflej[oa] la diversidad y complejidad de la medicina como ciencia y práctico|es una definición general y, aunque es exacta, [^.]+)|Se usa (solo en contextos históricos|ampliamente también en el registro especializado)|[^.;]*Desuso:[^.;]+|Otro ámbito donde se emplea el término (?i:{re.escape(titulo)}) es [^.]+|Fue originalmente voz coloquial, pero se usa ampliamente también en el registro especializado|[^.]*[Pp]uede verse (utilizado tanto en un sentido como en otro|también variantes asimismo en desuso)|No es habitual en [^.]+|Dado que se trata de un sustantivo abstracto [^.]+|Localismo de uso en [^.]+|Con frecuencia en plural, como nombre de grupo medicamentoso|[^.]+pero (no se usa|carece de validez en [^.]+)|Generalmente por contraposición a:? [^.]+|Recibió el nombre por [^.]+|(Presencia de una )?((?i:{re.escape(titulo)}) o)( (?i:{re.escape(titulo)}))?|Etiología y Factores de Riesgo|[Pp]rognóstico y profilaxis|Término impreciso, [^.,;]+|A (pesar de sus numerosas ventajas, tiene algunas limitaciones|continuación, se abordan diversas aplicaciones y beneficios [^.]+)|Es sustantivo masculino también cuando hace referencia a personas de sexo [^.]+|[^.]+(en la arcosegundo|se usó de forma preferente en la primera) acepción[^.]*|Con frecuencia en plural)\.))(?=([ \n]|$))', rf'#', content)
        #
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Como adjetivo, es invariable en cuanto a|(En propiedad [^.]+|[^.]*[Ss]e usa (también|mucho más)|(Es incorrecto |En )?[Ss]u uso( etimológico)?|Antiguamente se usó también|[^.]+ pero en español se usa solo) (con|de)) (género|identidad sexual) [^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(Síntomas( y diagnóstico)? de la|[Dd]iagnóstico de la|[Tt]erapia( y manejo)? de la|Causas y tipos de) (?i:{re.escape(titulo)})[.:]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^\n]*[Cc]omo [^\n]*cualquier procedimiento [^\n]*(no está exenta de riesgos|hay riesgos asociados con su uso)[^\n]+))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()En el caso de la (?i:{re.escape(titulo)}), por ejemplo,))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)
        #
        content = sustraer(rf'(, +|; +|\. +|\n *|^ *)((()[Vv]ariante (en desuso|gráfica desprestigiada[^.,;]*)\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Aa]breviatura (de (?i:{re.escape(titulo)})([^.;]+)?|ingles de [^.]+ \([^.)]*(?i:{re.escape(titulo)})\))\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ll]a preferencia (por|entre) ((?i:{re.escape(titulo)})(, (?i:{re.escape(titulo)}))* [yo] [^.]+|una? (sinónimo|variante) u otr[oa]) depende( del contexto)?(( y)? de[^.]+)?[.;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(La x basal |[^.]+, )?([Ss]e|La) pronuncia(ción)? ((original aproximada es )?/[^.]+|como (se escribe|s))\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]+ del tipo de (?i:{re.escape(titulo)}) XYZ[^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ss]u uso es abrumador\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()([Cc]on incidencia|[Ee]n ocasiones) abreviado a (?i:{re.escape(titulo)})(, (sustantivo [^. ]+|especialmente en [^. ]+))?[.,;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(([Ll]as? (formas?|respectivas variantes con) [^.;]+ )?([Ee]s|[Ss]on|[Ss]e considera) (incorrectas?|impropias)|[Ss]e desaconsejan?)([^.]+)?\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ee]s un concepto amplio que puede aplicarse a diferentes contextos y situaciones médicas, [^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ee]n este contexto es subjetivo[^.]*\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.,;]*[Ll]a RAE[^.]*\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()(que )?[Nn]o debe confundirse con[^.]+\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()([^.]*[Ss]e usa (((mucho|muchísimo) )?más[^.;]*|de forma abrumadora|sobre todo|prácticamente de forma exclusiva) en [^.]+|Por semejanza de campo temático, existe riesgo importante de[^.]+|Las [^.;]+|[^.,]*[Ee]n (esta|todas sus)) acepci(ón|ones)[^.]*\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Pp]lural invariable:? (\()?l[oa]s (?i:{re.escape(titulo)})(\))?[^.]*\.))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()([Tt]ambién )?([Ss]e le conoce como|[Cc]onocida|([Hh]abitualmente )?[Dd]enominad[oa]|[Ss]e denomina)( también)? (?i:{re.escape(titulo)})( o (?i:{re.escape(titulo)}))?[.,]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[^.]*[Pp]uede verse (también ([^.,;]+, variante en desuso|(escrito )?en inglés [^.;]+|(?i:{re.escape(titulo)})( \(?[yo] (?i:{re.escape(titulo)})\)?)?(,? \(?variante [^.,;]+)?(, que es anglicismo sintáctico, o)?|[^.,;]*(, que se considera latinismo innecesario|con la grafía [^.,;]+))|en yuxtaposición [^.;]+:[^.;]+)[.;]))(?=([ \n]|$))', rf'#', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Vv]éase también: [^.]+\.))(?=([ \n]|$))', rf'#', content)
        #, flags=re.IGNORECASE
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()[Ll]a (?i:{re.escape(titulo)})(,| es| designa) una (?i:{re.escape(titulo)}),))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)
        content = sustraer(rf'(; +|\. +|\n *|^ *)((()El (?i:{re.escape(titulo)}) (en [^. ]+) \(o (?i:{re.escape(titulo)})\)))(?=([ \n]|$))', re.sub(r'°(\d+)°', r'\\\1', rf'#\n~{titulo}~ °5°'), content)
        content = sustraer(rf'(\n *|^ *)((()((?i:{re.escape(titulo)})( \(?(símbolo|o) (?i:{re.escape(titulo)})\)?)?,)(( (también|más|comúnmente))? (conocid|llamad|abreviad|denominad)[ao]s?( también)?( por sus siglas en inglés)?( como)? (?i:{re.escape(titulo)})( \(([^,.;:()]*?)\))?,)?))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)
        content = sustraer(rf'(\n *|^ *)((()((también|comúnmente) (conocid|llamad|abreviad|denominad)[ao]s? (como )?)?(?i:{re.escape(titulo)})( \(?(símbolo|o) ([^,.;:()]*?)\)?)?,?)( (se|es|pueden?|fue|solo|proviene|generalmente|permiten?|son|más conocidas|constituye|consiste|designa|en|está|sirve|corresponde|juega|no|tiene|comienza|nos|pasa|funciona|utiliza|desempeña|completa|lleva|debe|proporciona|suele|hace|impide|deriva|implica|requiere|refiere|investiga|representa|cumple|recibe|incluye|ha|provoca|reflej[ao]|liberan),?|,))(?=([ \n]|$))', re.sub(r'°(\d+)°', r'\\\1', rf'#\n~{titulo}~ °12°'), content)
        content = sustraer(rf'(\. +|\n *|^ *)((()([Aa]l|[Uu]na?|[Ee]st[aeo]s?|[Cc]ada|(([Aa]unque|[Aa]demás|[Dd]e hecho|[Aa] pesar de estos riesgos|[Ss]in embargo|[Gg]eneralmente|([Ee]s (importante|relevante)|[Cc]abe) destacar que|[Ss]i bien),? )?([Ee]l|[Ll][ao]s?)( término| palabra)?) (?i:{re.escape(titulo)}),( (también|más|comúnmente))? (conocid|llamad|abreviad|denominad)[ao]s?( también)?( por sus siglas en inglés)? como (?i:{re.escape(titulo)})( \(([^,.;:()]*?)\))?,))(?=([ \n]|$))', rf'#\n~{titulo}~ ', content)
        eliminaciones = re.findall(rf'(((\. +|\n *|^ *)())(|([^.]+:|(([Ss]in embargo|[Pp]or ejemplo), )?[^.,; ]+((( [^.,;\d ]{{2,3}})? [^.,;\d ]+){{0,10}}),) )((([Aa]l|[Uu]na?|[Ee]st[aeo]s?|[Cc]ada|(([Aa]unque|[Aa]demás|[Dd]e hecho|[Aa] pesar de estos riesgos|[Ss]in embargo|[Gg]eneralmente|([Ee]s (importante|relevante)|[Cc]abe) destacar que|[Ss]i bien),? )?([Ee]l|[Ll][ao]s?)( término| palabra)?) (?i:{re.escape(titulo)})s?)( (también|propiamente dicha)( (conocid|llamad|abreviad|denominad)[ao]s?( también)?( por sus siglas en inglés)?( como)?(?i:{re.escape(titulo)}))?,?)?( \(?(símbolo|o) ([^,.;:()]*?)\)?,?|, (por otro lado|en cambio),)?)((, ([^.,;]*en el contexto[^.,;]+|responsable de[^.,;]+),)? (se|es|pueden?|fue|solo|proviene|generalmente|permiten?|son|más conocidas|constituye|consiste|designa|en|está|sirve|corresponde|juega|nos|tiene|comienza|pasa|funciona|utiliza|desempeña|completa|lleva|debe|proporciona|suele|hace|impide|deriva|implica|requiere|refiere|investiga|representa|cumple|recibe|incluye|ha|provoca|reflej[ao]|liberan),?|,))(?=([ \n]|$))', content)#!no
        for linea in eliminaciones:
            if 'En estos ' not in linea[4] and (len(re.sub(r'[Ee]st[aeo]s?', r'', linea[13])) or len(titulo) > 8):#evitar sindrome
                content = re.sub(rf'{re.escape(linea[1])}{linea[4]}{re.escape(linea[11])}{linea[31]}(?=([ \n]|$))', rf'{linea[2]}\n{linea[4]}~{linea[12]}~ {linea[31]}', content, count=1)
        content = re.sub(r'[\n ]+\n[\n ]+|[\n ]+\n|\n[\n ]+', r'\n', content)
        content = re.sub(r'  +', r' ', content)
        content = content.replace('~ ,', '~')
        content = content.replace(';.', '.')
        content = content.replace('..', '.')
        content = content.replace(' .', '.')
        content = content.replace(' ,', ',')
        content = content.strip()
        if len(__content):
            if len(content):
                content = f'{__content}\n{content}'.split('\n')
                _content = set()
                with open(f'{path2}{titulo}.txt', 'w', encoding='utf-8') as fl:
                    fl.write(content[0])
                    _content.add(content[0])
                    for i in range(1, len(content)):
                        if content[i] not in _content:
                            _content.add(content[i])
                            fl.write(f'\n{content[i]}')
        elif len(content):
            with open(f'{path2}{titulo}.txt', 'w', encoding='utf-8') as fl:
                fl.write(content)
        elif os.path.isfile(f'{path2}{titulo}.txt'):
            os.remove(f'{path2}{titulo}.txt')

    for nombre_archivo in os.listdir(path2):
        if os.path.isfile(path2 + nombre_archivo):
            with open(path2 + nombre_archivo, 'r', encoding='utf-8') as fl:
                content = fl.read().strip()
            if content != '':
                palabras_objetivo.add(nombre_archivo[:-4])
            else:
                print(f'sin contenido: {nombre_archivo}')
    
    for termino in ['rehabilitación', 'seguridad', 'principio', 'cuerpo']:
        palabras_objetivo.discard(termino)

    for i in range(2):
        for nombre_archivo in os.listdir(path2):
            reacomodar(path2, nombre_archivo, palabras_objetivo)

    for nombre_archivo in os.listdir(path2):
        definiciones = list()

        with open(path2 + nombre_archivo, 'r', encoding='utf-8') as file:
            _definiciones = file.read().split('\n')
        
        for parrafo in _definiciones:
            _separados = sent_tokenize(parrafo)
            cont = len(definiciones)
            separados = list()

            for i in range(len(_separados)):
                if _separados[i].count('(') != _separados[i].count(')') and i+1 < len(_separados):
                    _separados[i+1] = _separados[i] + ' ' + _separados[i+1]
                else:
                    separados.append(_separados[i])

            if len(definiciones) and len(definiciones[-1]) < 7:
                definiciones[-1] += ' ' + separados[0]
            else:
                definiciones.append(separados[0])

            for sentencia in separados[1:]:
                definiciones[-1] += '|' + sentencia

            for i in range(cont, len(definiciones)):
                if definiciones[i].count('|') > 3:
                    definiciones[i] = ' '.join(definiciones[i].split('|')[:4])

            for i in range(len(definiciones)-1, cont, -1):
                definiciones[i-1] = definiciones[i-1] + ' ' + definiciones[i]
                del definiciones[-1]

            definiciones[-1] = definiciones[-1].replace('|', ' ')

        with open(path2 + nombre_archivo, 'w', encoding='utf-8') as fl:
            fl.write(definiciones[0])
            for i in range(len(definiciones)-1):
                fl.write(f'\n{definiciones[i+1]}')

    definiciones = {'cianosis': 'es la coloración azulada en la piel y las membranas mucosas debido a la falta de oxígeno en la sangre', 'polaquiuria': 'es la necesidad de orinar frecuentemente', 'hematemesis': 'es la expulsión de sangre de origen digestivo', 'hemoptisis': 'es la expulsión de sangre por la boca', 'tirotropina': 'es la hormona estimulante de la tiroides', 'disuria': 'es el dolor o incomodidad al orinar', 'glomerulonefritis': 'es la inflamación aguda de los glomérulos', 'hematuria': 'es la presencia de sangre en la orina', 'proteinuria': 'es la presencia de proteínas en la orina', 'epistaxis': 'es el sangrado por la nariz', 'pancreatitis': 'inflamación del páncreas', 'colitis': 'es la inflamación del colon', 'polidipsia': 'es la sed excesiva', 'neuropatía periférico': 'es el daño en los nervios de las manos y los pies'}#, '': ''

    for clave, valor in definiciones.items():
        _clave = clave
        if clave in equivalentes:
            _clave = equivalentes[clave]
        if not os.path.isfile(f'{path2}{_clave}.txt'):
            texto = valor
        else:
            texto = f'\n{valor}'
        with open(f'{path2}{_clave}.txt', 'a', encoding='utf-8') as fl:
            fl.write(texto)

    print('Limpieza finalizada.')

if __name__ == '__main__':

    limpiar_fuentes()
