# -*- coding: utf-8 -*-
from crear_dataset import tokenizar
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
    ######
    #numeros = re.findall(r'(?<=[ ])(\d+(\.\d\d\d)*(,\d+)?)/(\d+(\.\d\d\d)*(,\d+)?)(?=[ .,])', content)
    #if len(numeros)>100:
    #    for numero in numeros:
    #        content = re.sub(r'(?<=[ ])' + numero[0] + '/' + numero[3] + r'(?=[ .,])', '===' + numero[0] + '/' + numero[3] + '===', content, count=1)
    #        bandera = 1
    ######
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
    #numeros = re.findall(r'(?<=[ (])(\d+(\.\d\d\d)*(,\d+)?)-(\d+(\.\d\d\d)*(,\d+)?)(?=[ :;)])', content)
    #if len(numeros) > 0:
    #    bandera = 1
    #    for numero in numeros:
    #        content = re.sub(r'(?<=[ (])' + re.escape(numero[0]) + '-' + re.escape(numero[3]) + r'(?=[ ;)])', '===' + representacionNumerica(numero[0]) + ' a ' + representacionNumerica(numero[3]) + '===', content, count=1)
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
#No modificar para enfermedad reumática: "clasifica en diez grupos: I. "
#{'1', 'í', 'ó', 'b', 'c', 'g', 'ú', 'o', 'd', 'ü', 'r', ' ', 'x', 't', 'y', '8', 'z', 's', 'ñ', '7', 'a', '9', '4', 'j', 'i', '2', 'n', 'p', '0', '-', 'm', 'é', 'á', 'f', '.', 'h', 'w', 'u', '5', 'v', 'l', 'k', 'q', 'e', '6', '3', ','}
#'Á', 'R', '1', 'S', 'v', 'É', 'g', 'é', 'z', 'T', '•', 'B', 'l', 'е', 'U', '7', '^', 's', 't', '2', 'ñ', 'H', '(', 'K', 'u', 'a', 'r', 'd', ']', 'J', '5', '{', 'O', '4', 'M', '9', 'W', 'X', ',', '=', 'e', 'V', 'F', 'Q', ')', 'Ú', 'C', 'E', 'á', '6', 'А', 'p', '8', 'q', '¡', 'k', 'м', '_', 'ý', 'а', 'A', 'Y', '*', 'ό', 'Ó', ':', 'ν', 'I', '>', 'Ü', 'x', 'í', '<', 'P', 'c', 'N', 'Í', '·', 'i', '.', 'o', 'w', '/', '}', 'n', '3', ';', 'h', 'Z', 'ú', 'ü', 'D', 'Β', 'L', '&', 'y', 'b', 'm', 'G', 'ó', 'j', '0', '[', 'f'
##########
#Prueba 1
#No anotado

#Prueba 2
#15: Precision_prueba(1/10/100): 10.17 24.32 47.64, media: 140.00, varianza: 405.99
#10: Precision_prueba(1/10/100): 12.66 29.78 48.39, media: 108.00, varianza: 411.13
#17: Precision_prueba(1/10/100): 11.66 26.55 46.90, media: 144.00, varianza: 416.65

#Prueba 3
#13: Precision_prueba(1/10/100): 12.16 32.51 56.58, media: 58.00, varianza: 374.96
#8:  Precision_prueba(1/10/100): 11.91 31.02 52.61, media: 73.00, varianza: 385.21
#18: Precision_prueba(1/10/100): 10.92 31.02 51.86, media: 75.00, varianza: 392.45

#Prueba 4
#14: 
#    Precision_prueba(1/10/100): 9.88 29.63 55.80, media: 75.00, varianza: 380.55
#    Precision_prueba(1/10/100): 8.15 26.17 51.36, media: 93.00, varianza: 396.57

#Prueba 5
#9:  Precision_prueba(1/10/100): 16.01 30.30 53.45, media: 76.50, varianza: 404.82
#10: Precision_prueba(1/10/100): 13.55 29.56 51.72, media: 92.50, varianza: 403.41
#13: Precision_prueba(1/10/100): 14.78 30.54 52.22, media: 84.00, varianza: 406.55

#Prueba 6
#8:  Precision_prueba(1/10/100): 14.73 34.11 59.30, media: 40.00, varianza: 398.50
#9:  Precision_prueba(1/10/100): 15.89 34.11 58.53, media: 39.00, varianza: 383.80
#10: Precision_prueba(1/10/100): 14.73 35.66 58.14, media: 48.50, varianza: 388.09

#Prueba 7
#7:  Precision_prueba(1/10/100): 13.62 33.85 57.59, media: 59.00, varianza: 397.46
#8:  Precision_prueba(1/10/100): 12.06 33.85 57.59, media: 43.00, varianza: 396.71

#Prueba 8
#6:  Precision_prueba(1/10/100): 19.53 35.55 55.47, media: 55.00, varianza: 403.00
#7:  Precision_prueba(1/10/100): 16.80 37.11 56.25, media: 48.00, varianza: 404.36
#9:  Precision_prueba(1/10/100): 17.19 33.59 53.91, media: 68.50, varianza: 383.06

#Prueba 9
#5:  Precision_prueba(1/10/100): 11.72 27.73 48.05, media: 114.00, varianza: 397.35
#6:  Precision_prueba(1/10/100): 10.16 33.20 55.47, media: 71.00, varianza: 389.47
#10: Precision_prueba(1/10/100): 10.94 30.47 55.47, media: 54.50, varianza: 386.13
#9:  Precision_prueba(1/10/100): 13.28 31.25 51.17, media: 78.50, varianza: 389.85

#Prueba 10
#1:  Precision_prueba(1/10/100): 18.08 35.00 58.08, media: 47.50, varianza: 392.64
#4:  Precision_prueba(1/10/100): 13.46 33.85 60.38, media: 33.50, varianza: 365.27
#5:  Precision_prueba(1/10/100): 16.15 36.92 61.54, media: 38.50, varianza: 348.57
#6:  Precision_prueba(1/10/100): 12.31 37.31 61.92, media: 39.50, varianza: 383.06
#7:  Precision_prueba(1/10/100): 14.23 37.69 61.54, media: 29.00, varianza: 348.57
#8:  Precision_prueba(1/10/100): 13.08 33.46 58.46, media: 48.00, varianza: 375.26
#9:  Precision_prueba(1/10/100): 13.85 35.38 60.00, media: 39.50, varianza: 376.61
#10: Precision_prueba(1/10/100): 12.31 36.15 64.23, media: 24.50, varianza: 378.51

#Prueba 11
#7:  Precision_prueba(1/10/100): 19.08 36.64 58.40, media: 32.50, varianza: 390.67
#6:  Precision_prueba(1/10/100): 17.94 33.59 60.31, media: 40.50, varianza: 391.18
#5:  Precision_prueba(1/10/100): 15.27 31.30 58.78, media: 56.50, varianza: 397.42
#20: Precision_prueba(1/10/100): 14.89 35.50 59.16, media: 38.00, varianza: 392.06

#Prueba 12
#8:  Precision_prueba(1/10/100): 12.60 35.88 58.02, media: 40.00, varianza: 389.20
#7:  Precision_prueba(1/10/100): 10.31 32.82 54.58, media: 65.50, varianza: 387.10
#6:  Precision_prueba(1/10/100): 12.60 34.35 58.02, media: 40.50, varianza: 397.82
#5:  Precision_prueba(1/10/100): 11.45 33.59 60.31, media: 36.50, varianza: 373.05
#1:  Precision_prueba(1/10/100): 12.60 36.64 56.11, media: 43.50, varianza: 399.84

#Prueba 13
#8:  Precision_prueba(1/10/100): 12.50 33.71 57.58, media: 52.00, varianza: 399.35
#7:  Precision_prueba(1/10/100): 9.85 31.44 58.33, media: 60.50, varianza: 391.29
#6:  Precision_prueba(1/10/100): 10.61 28.79 51.52, media: 85.50, varianza: 401.68

#Prueba 14
#10: Precision_prueba(1/10/100): 14.61 34.83 56.55, media: 52.00, varianza: 392.80
#8:  Precision_prueba(1/10/100): 11.24 28.84 55.43, media: 60.00, varianza: 399.95
#6:  Precision_prueba(1/10/100): 12.73 30.34 51.69, media: 92.00, varianza: 404.80
#15: Precision_prueba(1/10/100): 13.86 32.58 53.93, media: 56.00, varianza: 401.05

#Prueba 15
#15: Precision_prueba(1/10/100): 12.36 29.59 53.56, media: 61.00, varianza: 379.69
#10: Precision_prueba(1/10/100): 14.61 32.96 57.68, media: 46.00, varianza: 375.66
#8:  Precision_prueba(1/10/100): 13.11 29.96 54.31, media: 54.00, varianza: 370.83
#6:  Precision_prueba(1/10/100): 12.73 31.09 53.56, media: 78.00, varianza: 364.35
#3:  Precision_prueba(1/10/100): 14.23 33.33 58.43, media: 38.00, varianza: 366.52

#Prueba 16
#20: Precision_prueba(1/10/100): 14.12 28.63 51.76, media: 80.00, varianza: 378.59
#17: Precision_prueba(1/10/100): 14.12 30.20 57.65, media: 58.00, varianza: 368.32
#15: Precision_prueba(1/10/100): 12.94 33.33 63.53, media: 41.00, varianza: 347.96
#16: Precision_prueba(1/10/100): 15.29 30.98 57.25, media: 58.00, varianza: 381.99
#11: Precision_prueba(1/10/100): 14.51 29.41 52.16, media: 91.00, varianza: 377.18
#8:  Precision_prueba(1/10/100): 15.29 34.12 58.43, media: 47.00, varianza: 352.76
#5:  Precision_prueba(1/10/100): 14.12 32.94 59.22, media: 45.00, varianza: 341.18
#3:  Precision_prueba(1/10/100): 14.90 31.37 59.22, media: 40.00, varianza: 369.98

#Prueba 17
#25: Precision_prueba(1/10/100): 13.78 31.10 57.09, RRM: 19.66, media: 48.50, varianza: 374.26
#16: Precision_prueba(1/10/100): 9.84 28.74 56.30, RRM: 16.16, media: 49.50, varianza: 358.44
#12: Precision_prueba(1/10/100): 15.11 34.00 61.23, RRM: 21.79, media: 47.00, varianza: 380.02
#11: Precision_prueba(1/10/100): 13.78 37.01 59.84, RRM: 21.00, media: 39.00, varianza: 383.59
#9:  Precision_prueba(1/10/100): 12.20 33.46 55.12, RRM: 18.17, media: 56.00, varianza: 372.78
#8:  Precision_prueba(1/10/100): 14.17 35.04 61.81, RRM: 21.15, media: 39.50, varianza: 343.81

#Prueba 18
#16: Precision_prueba(1/10/100): 17.69 36.38 57.26, RRM: 24.69, media: 47.00, varianza: 383.44
#12: Precision_prueba(1/10/100): 17.69 37.57 57.65, RRM: 24.15, media: 46.00, varianza: 391.22
#8:  Precision_prueba(1/10/100): 10.93 20.28 31.41, RRM: 14.20, media: 32.00, varianza: 379.08
#    Precision_prueba(1/10/100): 17.50 38.17 60.64, RRM: 24.74, media: 39.00, varianza: 375.43
#15: Precision_prueba(1/10/100): 10.74 18.69 31.61, RRM: 13.56, media: 38.00, varianza: 373.86
#    Precision_prueba(1/10/100): 16.90 35.98 61.43, RRM: 23.32, media: 47.00, varianza: 369.92

#Prueba 19
#16: Precision_prueba(1/10/100): 20.32 40.62 58.19, RRM: 26.90, media: 28.50, varianza: 383.68 Sum
#14: Precision_prueba(1/10/100): 20.31 41.41 62.11, RRM: 27.21, media: 25.50, varianza: 367.93 Sum
#12: Precision_prueba(1/10/100): 19.14 39.45 65.23, RRM: 25.95, media: 23.50, varianza: 394.58 Sum

#Prueba 20
#20: Precision_prueba(1/10/100): 19.61 35.69 62.35, RRM: 25.17, media: 34.00, varianza: 3293.50 Sum

#Prueba 21
#16: Precision_prueba(1/10/100): 17.58 39.45 61.72, RRM: 24.85, media: 26.50, varianza: 2004.53 Sum
#14: Precision_prueba(1/10/100): 17.58 41.80 62.50, RRM: 24.87, media: 23.00, varianza: 1921.92 Sum

#Prueba 22
#16: Precision_prueba(1/10/100): 22.66 43.75 62.50, RRM: 28.41, media: 22.00, varianza: 3565.05 Sum
#14: Precision_prueba(1/10/100): 22.66 41.41 66.02, RRM: 28.64, media: 27.50, varianza: 2543.93 Sum
#13: Precision_prueba(1/10/100): 23.05 40.62 62.50, RRM: 28.59, media: 26.50, varianza: 2824.67 Ato
#    Precision_prueba(1/10/100): 22.66 42.19 62.50, RRM: 28.42, media: 25.00, varianza: 2856.60 Sum
#8:  Precision_prueba(1/10/100): 22.27 42.58 64.45, RRM: 29.43, media: 19.00, varianza: 3791.96 Sum
#3:  Precision_prueba(1/10/100): 18.75 37.11 60.94, RRM: 24.82, media: 35.00, varianza: 2568.17 Sum

#Prueba 23
#17: Precision_prueba(1/10/100): 21.88 39.84 60.55, RRM: 27.77, media: 31.00, varianza: 3290.46 Sum
#14: Precision_prueba(1/10/100): 21.48 39.84 60.94, RRM: 28.15, media: 35.50, varianza: 2881.70 Sum
#13: Precision_prueba(1/10/100): 23.44 42.19 61.72, RRM: 29.87, media: 25.00, varianza: 3239.57 Sum
#8:  Precision_prueba(1/10/100): 24.22 42.97 60.16, RRM: 30.80, media: 29.00, varianza: 2793.43 Sum
#4:  Precision_prueba(1/10/100): 23.05 39.84 58.98, RRM: 29.24, media: 30.00, varianza: 2532.83 Sum

#Prueba 24
#18: Precision_prueba(1/10/100): 18.29 42.80 64.59, RRM: 26.28, media: 27.00, varianza: 2247.25 Sum
#14: Precision_prueba(1/10/100): 19.84 39.30 59.53, RRM: 26.68, media: 33.00, varianza: 2176.86 Sum
#13: Precision_prueba(1/10/100): 18.68 39.30 61.48, RRM: 25.22, media: 30.00, varianza: 2497.06 Sum
#8:  Precision_prueba(1/10/100): 21.40 43.58 62.26, RRM: 28.12, media: 28.00, varianza: 2154.59 Sum
#4:  Precision_prueba(1/10/100): 19.46 41.63 63.04, RRM: 26.75, media: 30.00, varianza: 1612.99 Sum

#Prueba 25
#15: Precision_prueba(1/10/100): 23.26 43.41 65.50, RRM: 29.87, media: 24.00, varianza: 1755.94 Sum
#14: Precision_prueba(1/10/100): 22.87 42.64 65.89, RRM: 29.40, media: 21.50, varianza: 1996.69 Sum
#13: Precision_prueba(1/10/100): 20.54 43.80 67.44, RRM: 28.43, media: 17.00, varianza: 2345.27 Sum
#8:  Precision_prueba(1/10/100): 21.32 43.02 62.02, RRM: 28.87, media: 25.00, varianza: 2417.03 Sum
#4:  Precision_prueba(1/10/100): 19.77 38.76 61.24, RRM: 26.57, media: 26.00, varianza: 1996.57 Sum

#Prueba 25_2
#15: Precision_prueba(1/10/100): 14.29 32.82 53.28, RRM: 20.06, media: 64.00, varianza: 4094.02 Sum
#14: Precision_prueba(1/10/100): 16.22 34.36 54.05, RRM: 22.23, media: 68.00, varianza: 4225.70 Sum
#12: Precision_prueba(1/10/100): 15.06 33.98 55.21, RRM: 22.00, media: 55.00, varianza: 4537.50 Sum
#8:  Precision_prueba(1/10/100): 13.51 33.98 54.44, RRM: 19.86, media: 57.00, varianza: 4403.51 Sum
#5:  Precision_prueba(1/10/100): 15.83 35.91 55.21, RRM: 22.51, media: 57.00, varianza: 4508.85 Sum

#Prueba 26
#15: Precision_prueba(1/10/100): 20.08 39.00 64.09, RRM: 26.79, media: 33.00, varianza: 2707.48 Sum
#14: Precision_prueba(1/10/100): 19.69 42.08 68.73, RRM: 26.94, media: 19.00, varianza: 3013.71 Sum
#12: Precision_prueba(1/10/100): 19.31 42.08 65.25, RRM: 26.68, media: 20.00, varianza: 2417.21 Sum
#8:  Precision_prueba(1/10/100): 20.08 42.86 65.64, RRM: 28.06, media: 24.00, varianza: 1890.67 Sum
#5:  Precision_prueba(1/10/100): 18.53 41.70 64.09, RRM: 26.01, media: 20.00, varianza: 2277.97 Sum

#Prueba 27
#15: Precision_prueba(1/10/100): 19.23 40.00 64.23, RRM: 26.41, media: 25.00, varianza: 2431.39 Sum
#14: Precision_prueba(1/10/100): 19.23 40.38 61.15, RRM: 26.10, media: 22.50, varianza: 2693.13 Sum
#11: Precision_prueba(1/10/100): 16.92 38.46 62.31, RRM: 24.57, media: 26.00, varianza: 3236.75 Sum
#8:  Precision_prueba(1/10/100): 21.54 42.31 61.92, RRM: 27.60, media: 20.00, varianza: 3231.85 Sum
#5:  Precision_prueba(1/10/100): 18.46 40.77 66.15, RRM: 25.55, media: 25.00, varianza: 2807.58 Sum

#Prueba 28
#15: Precision_prueba(1/10/100): 21.07 42.15 63.22, RRM: 28.27, media: 30.00, varianza: 3567.15 Sum
#14: Precision_prueba(1/10/100): 19.54 44.44 65.52, RRM: 27.56, media: 21.00, varianza: 3875.29 Sum
#10: Precision_prueba(1/10/100): 21.07 41.38 63.60, RRM: 27.94, media: 26.00, varianza: 3837.58 Sum
#8:  Precision_prueba(1/10/100): 20.69 42.15 63.60, RRM: 27.47, media: 23.00, varianza: 3276.61 Sum
#5:  Precision_prueba(1/10/100): 19.92 37.93 59.77, RRM: 25.75, media: 36.00, varianza: 3379.26 Sum

#Prueba 29
#15: Precision_prueba(1/10/100): 22.31 40.77 61.15, RRM: 28.08, media: 31.00, varianza: 4005.97 Sum
#14: Precision_prueba(1/10/100): 18.85 40.77 56.54, RRM: 25.69, media: 38.00, varianza: 3806.82 Ato
#9:  Precision_prueba(1/10/100): 22.69 41.15 61.92, RRM: 28.92, media: 40.50, varianza: 3884.25 Sum
#8:  Precision_prueba(1/10/100): 20.38 40.38 60.77, RRM: 27.31, media: 30.00, varianza: 3758.26 Sum
#5:  Precision_prueba(1/10/100): 21.54 43.46 59.23, RRM: 29.22, media: 23.00, varianza: 3759.26 Ato
#    Precision_prueba(1/10/100): 20.77 43.85 59.62, RRM: 28.92, media: 23.00, varianza: 3727.31 Sum

#Prueba 30
#15: Precision_prueba(1/10/100): 15.77 29.62 54.23, RRM: 20.23, media: 61.50, varianza: 2692.66 Ato
#9:  Precision_prueba(1/10/100): 13.08 33.85 55.00, RRM: 19.62, media: 59.00, varianza: 3412.71 Sum
#8:  Precision_prueba(1/10/100): 13.85 32.69 56.54, RRM: 20.42, media: 55.00, varianza: 2673.27 Sum
#7:  Precision_prueba(1/10/100): 16.15 30.00 54.23, RRM: 21.73, media: 63.00, varianza: 2772.03 Sum
#5:  Precision_prueba(1/10/100): 13.85 32.69 53.85, RRM: 20.04, media: 62.50, varianza: 2049.58 Ato

#Prueba 31
#15: Precision_prueba(1/10/100): 20.69 40.23 63.60, RRM: 27.45, media: 29.00, varianza: 3277.31 Sum
#9:  Precision_prueba(1/10/100): 20.69 39.08 62.84, RRM: 27.06, media: 28.00, varianza: 3547.94 Sum
#7:  Precision_prueba(1/10/100): 18.39 36.02 62.45, RRM: 24.40, media: 33.00, varianza: 3484.56 Sum
#6:  Precision_prueba(1/10/100): 18.39 40.61 63.22, RRM: 25.85, media: 26.00, varianza: 3524.25 Sum
#5:  Precision_prueba(1/10/100): 19.54 38.31 58.62, RRM: 25.30, media: 36.00, varianza: 2912.72 Sum

#Prueba 32
#15: Precision_prueba(1/10/100): 22.39 35.52 59.46, RRM: 27.26, media: 27.00, varianza: 4951.32 Sum
#9:  Precision_prueba(1/10/100): 20.46 39.38 57.92, RRM: 26.78, media: 33.00, varianza: 3361.67 Sum
#6:  Precision_prueba(1/10/100): 15.83 42.47 62.55, RRM: 25.28, media: 24.00, varianza: 3688.64 Sum
#5:  Precision_prueba(1/10/100): 18.15 38.61 58.30, RRM: 25.11, media: 31.00, varianza: 4275.71 Sum

#Prueba 33
#15: Precision_prueba(1/10/100): 18.88 35.62 57.94, RRM: 24.79, media: 38.00, varianza: 2466.89 Sum
#9:  Precision_prueba(1/10/100): 18.88 40.34 63.95, RRM: 26.06, media: 22.00, varianza: 2581.01 Sum
#6:  Precision_prueba(1/10/100): 21.46 41.20 61.37, RRM: 28.43, media: 28.00, varianza: 2628.10 Sum
#5:  Precision_prueba(1/10/100): 19.31 37.77 59.23, RRM: 25.20, media: 28.00, varianza: 2383.32 Sum

#Prueba 34
#15: Precision_prueba(1/10/100): 24.14 42.24 67.24, RRM: 30.11, media: 18.00, varianza: 1667.08 Sum
#9:  Precision_prueba(1/10/100): 26.72 46.12 68.53, RRM: 33.22, media: 16.50, varianza: 2998.32 Sum
#6:  Precision_prueba(1/10/100): 21.98 42.67 65.52, RRM: 29.09, media: 19.50, varianza: 2801.87 Sum
#4:  Precision_prueba(1/10/100): 21.55 44.83 66.81, RRM: 29.06, media: 19.50, varianza: 3035.82 Sum

#Prueba 35
#15: Precision_prueba(1/10/100): 19.40 40.52 62.07, RRM: 25.71, media: 26.00, varianza: 3595.60 Sum
#10: Precision_prueba(1/10/100): 17.67 39.66 65.09, RRM: 25.01, media: 24.00, varianza: 4118.53 Sum
#9:  Precision_prueba(1/10/100): 20.69 38.36 64.66, RRM: 26.60, media: 25.00, varianza: 3665.20 Sum
#6:  Precision_prueba(1/10/100): 22.41 43.10 64.22, RRM: 28.46, media: 19.00, varianza: 3690.30 Sum

#Prueba 36
#15: Precision_prueba(1/10/100): 23.18 44.21 66.09, RRM: 30.32, media: 21.00, varianza: 2515.89 Sum
#9:  Precision_prueba(1/10/100): 24.03 42.49 67.38, RRM: 30.48, media: 18.00, varianza: 2718.02 Sum
#8:  Precision_prueba(1/10/100): 25.75 45.49 64.38, RRM: 32.62, media: 20.00, varianza: 2373.37 Sum
#6:  Precision_prueba(1/10/100): 24.46 46.35 68.24, RRM: 31.98, media: 15.00, varianza: 2120.88 Sum

#Prueba 37
#15: Precision_prueba(1/10/100): 21.89 41.63 65.24, RRM: 28.47, media: 22.00, varianza: 2829.34 Sum
#9:  Precision_prueba(1/10/100): 20.17 38.20 66.95, RRM: 26.12, media: 22.00, varianza: 2337.02 Sum
#8:  Precision_prueba(1/10/100): 23.61 43.35 66.09, RRM: 29.96, media: 19.00, varianza: 3213.43 Sum
#6:  Precision_prueba(1/10/100): 21.46 45.49 67.81, RRM: 29.03, media: 17.00, varianza: 2908.16 Sum

#Prueba 38
#15: Precision_prueba(1/10/100): 21.12 40.52 62.07, RRM: 27.72, media: 24.50, varianza: 2536.52 Sum
#14: Precision_prueba(1/10/100): 20.69 37.93 68.97, RRM: 27.04, media: 32.50, varianza: 2687.48 Sum
#8:  Precision_prueba(1/10/100): 21.55 40.09 62.93, RRM: 27.71, media: 25.50, varianza: 2587.82 Sum
#6:  Precision_prueba(1/10/100): 18.97 37.93 66.81, RRM: 26.22, media: 27.00, varianza: 2485.16 Sum

#Prueba 39
#16: Precision_prueba(1/10/100): 18.10 37.50 64.22, RRM: 25.06, media: 36.50, varianza: 2031.53 Sum
#15: Precision_prueba(1/10/100): 23.71 43.97 64.66, RRM: 30.48, media: 19.50, varianza: 2961.05 Ato
#8:  Precision_prueba(1/10/100): 21.55 40.95 67.24, RRM: 28.52, media: 20.50, varianza: 2428.54 Sum
#6:  Precision_prueba(1/10/100): 20.26 40.95 66.38, RRM: 27.51, media: 21.00, varianza: 2158.78 Ato

#Prueba 40
#15: Precision_prueba(1/10/100): 22.94 44.16 68.40, RRM: 30.03, media: 15.00, varianza: 2553.15 Sum
#8:  Precision_prueba(1/10/100): 23.81 45.45 68.83, RRM: 30.65, media: 19.00, varianza: 2193.94 Sum
#6:  Precision_prueba(1/10/100): 22.08 45.89 71.43, RRM: 30.31, media: 15.00, varianza: 2308.54 Sum
#5:  Precision_prueba(1/10/100): 23.38 43.72 66.23, RRM: 30.08, media: 18.00, varianza: 1730.24 Sum

#0.01: llegan a un punto, y van en ligera caida
#15: Precision_prueba(1/10/100): 12.99 33.77 54.98, RRM: 18.84, media: 64.00, varianza: 2708.52 Sum
#8:  Precision_prueba(1/10/100): 14.72 31.17 52.38, RRM: 19.56, media: 73.00, varianza: 2187.18 Sum
#6:  Precision_prueba(1/10/100): 15.15 29.44 53.25, RRM: 20.88, media: 68.00, varianza: 2734.72 Sum
#5:  Precision_prueba(1/10/100): 13.42 29.87 53.68, RRM: 18.81, media: 73.00, varianza: 2679.82 Sum

#0.009: osmarloeza77suaste
#15: Precision_prueba(1/10/100): 15.09 30.60 54.31, RRM: 20.12, media: 64.00, varianza: 3529.33 Sum
#8:  Precision_prueba(1/10/100): 12.50 27.59 57.33, RRM: 18.29, media: 67.50, varianza: 4020.78 Ato
#7:  Precision_prueba(1/10/100): 14.22 34.05 59.05, RRM: 20.65, media: 39.00, varianza: 3631.95 Sum
#6:  Precision_prueba(1/10/100): 14.22 31.03 55.17, RRM: 20.48, media: 76.50, varianza: 3908.50 Sum

#0.008: osmarloeza88suaste
#15: Precision_prueba(1/10/100): 14.22 26.29 56.03, RRM: 18.50, media: 61.50, varianza: 3676.65 Sum
#8:  Precision_prueba(1/10/100): 15.52 31.47 53.88, RRM: 20.98, media: 50.00, varianza: 4197.93 Ato
#7:  Precision_prueba(1/10/100): 19.40 31.47 55.17, RRM: 24.17, media: 46.50, varianza: 3401.38 Sum
#6:  Precision_prueba(1/10/100): 16.38 30.60 56.03, RRM: 21.49, media: 48.00, varianza: 3039.96 Sum

#Prueba 41
#15: Precision_prueba(1/10/100): 19.83 39.22 62.50, RRM: 26.04, media: 30.50, varianza: 3360.64 Sum
#8:  Precision_prueba(1/10/100): 18.97 42.24 68.10, RRM: 27.26, media: 19.50, varianza: 2648.44 Sum
#7:  Precision_prueba(1/10/100): 20.69 39.22 63.79, RRM: 27.44, media: 23.50, varianza: 2877.71 Sum
#6:  Precision_prueba(1/10/100): 19.83 38.36 62.93, RRM: 25.82, media: 36.00, varianza: 2889.40 Sum

#0.007: osmarloeza88suaste
#15: Precision_prueba(1/10/100): 15.95 34.48 56.47, RRM: 21.51, media: 47.00, varianza: 3275.46 Sum
#8:  Precision_prueba(1/10/100): 17.24 35.34 59.05, RRM: 23.11, media: 38.50, varianza: 3185.83 Sum
#7:  Precision_prueba(1/10/100): 20.26 43.10 66.38, RRM: 26.99, media: 30.00, varianza: 3572.68 Sum
#6:  Precision_prueba(1/10/100): 18.53 36.64 63.36, RRM: 24.13, media: 25.00, varianza: 3205.57 Sum

#0.006: osmarloeza77suaste
#15: Precision_prueba(1/10/100): 18.97 36.21 63.79, RRM: 24.19, media: 38.50, varianza: 3067.35 Sum
#8:  Precision_prueba(1/10/100): 18.53 38.79 65.09, RRM: 24.54, media: 28.00, varianza: 3664.10 Sum
#7:  Precision_prueba(1/10/100): 19.40 38.36 63.36, RRM: 25.62, media: 28.50, varianza: 3335.95 Sum
#6:  Precision_prueba(1/10/100): 17.67 37.07 64.66, RRM: 24.01, media: 27.50, varianza: 2950.50 Sum

#Prueba 42: 0.59 - 0.62
#15: Precision_prueba(1/10/100): 18.97 42.67 63.79, RRM: 27.45, media: 20.00, varianza: 3128.94 Sum
#8:  Precision_prueba(1/10/100): 20.69 43.97 69.83, RRM: 27.99, media: 16.50, varianza: 3307.06 Sum
#7:  Precision_prueba(1/10/100): 20.69 41.38 66.38, RRM: 28.02, media: 18.50, varianza: 3332.68 Sum
#6:  Precision_prueba(1/10/100): 21.55 40.95 66.81, RRM: 28.46, media: 17.00, varianza: 3234.35 Sum

#0.005: osmarloeza88suaste
#15: Precision_prueba(1/10/100): 21.12 38.79 63.36, RRM: 26.65, media: 41.00, varianza: 2776.64 Sum
#8:  Precision_prueba(1/10/100): 21.98 37.50 64.22, RRM: 27.56, media: 35.50, varianza: 2582.61 Sum
#7:  Precision_prueba(1/10/100): 17.24 38.79 66.38, RRM: 24.85, media: 25.00, varianza: 2821.22 Sum
#6:  Precision_prueba(1/10/100): 20.26 39.22 64.66, RRM: 27.23, media: 23.50, varianza: 2796.38 Sum

#0.004: a21216301
#15: Precision_prueba(1/10/100): 21.12 36.21 58.62, RRM: 25.83, media: 48.50, varianza: 2882.41 Sum
#8:  Precision_prueba(1/10/100): 19.83 40.09 65.52, RRM: 25.29, media: 32.50, varianza: 3327.30 Sum
#7:  Precision_prueba(1/10/100): 20.26 40.52 61.64, RRM: 27.00, media: 31.50, varianza: 2666.81 Sum
#6:  Precision_prueba(1/10/100): 21.98 39.66 64.22, RRM: 27.64, media: 29.50, varianza: 2237.43 Sum

#Prueba 43: 0.63 - 0.66
#15: Precision_prueba(1/10/100): 20.69 42.24 62.93, RRM: 27.75, media: 27.00, varianza: 2702.67 Sum
#8:  Precision_prueba(1/10/100): 18.97 43.53 63.79, RRM: 26.54, media: 23.50, varianza: 3232.25 Sum
#7:  Precision_prueba(1/10/100): 21.12 39.66 63.79, RRM: 27.42, media: 24.00, varianza: 2637.76 Sum
#6:  Precision_prueba(1/10/100): 18.53 38.36 65.09, RRM: 25.23, media: 33.50, varianza: 2900.26 Sum

#Prueba 44: 0.67 - 0.70
#15: Precision_prueba(1/10/100): 17.60 40.34 64.81, RRM: 25.27, media: 23.00, varianza: 2921.34 Sum
#10: Precision_prueba(1/10/100): 20.60 42.92 61.80, RRM: 28.03, media: 20.00, varianza: 2921.31 Sum
#7:  Precision_prueba(1/10/100): 21.89 46.78 66.52, RRM: 29.65, media: 16.00, varianza: 2984.43 Sum
#4:  Precision_prueba(1/10/100): 24.03 46.35 68.67, RRM: 31.44, media: 14.00, varianza: 2844.37 Sum

#0.003: osmarloeza88suaste
#15: Precision_prueba(1/10/100): 20.17 43.78 64.38, RRM: 27.79, media: 19.00, varianza: 3411.07 Sum
#10: Precision_prueba(1/10/100): 18.45 42.49 66.95, RRM: 26.06, media: 23.00, varianza: 2686.24 Sum
#7:  Precision_prueba(1/10/100): 21.03 38.20 64.81, RRM: 26.68, media: 26.00, varianza: 2729.85 Sum
#4:  Precision_prueba(1/10/100): 17.17 40.77 66.09, RRM: 25.33, media: 24.00, varianza: 2774.85 Sum

#osmarsanchez2002loeza: El mejor dataset (Prueba 34) cayo
#15: Precision_prueba(1/10/100): 19.40 43.53 67.24, RRM: 27.25, media: 16.00, varianza: 3480.04 Sum
#10: Precision_prueba(1/10/100): 19.40 44.83 68.10, RRM: 27.60, media: 17.50, varianza: 4088.10 Sum
#7:  Precision_prueba(1/10/100): 18.10 40.95 68.53, RRM: 26.03, media: 25.00, varianza: 3659.97 Sum
#4:  Precision_prueba(1/10/100): 18.97 40.95 68.97, RRM: 27.79, media: 20.00, varianza: 4207.20 Sum

#0.002: osmarsanchez2002loeza
#15: Precision_prueba(1/10/100): 15.88 38.20 66.09, RRM: 23.81, media: 23.00, varianza: 3436.02 Sum
#10: Precision_prueba(1/10/100): 15.88 38.20 66.09, RRM: 22.81, media: 23.00, varianza: 3436.02 Sum
#7:  Precision_prueba(1/10/100): 15.88 36.48 60.52, RRM: 22.83, media: 32.00, varianza: 2764.67 Ato
#4:  Precision_prueba(1/10/100): 17.17 39.91 65.24, RRM: 24.20, media: 21.00, varianza: 2252.72 Sum

#a21216301: Prueba 34 con 510DD (Bien, casi por igual que la prueba 44)
#15: Precision_prueba(1/10/100): 22.84 42.67 65.52, RRM: 28.95, media: 21.50, varianza: 2453.85 Sum
#10: Precision_prueba(1/10/100): 22.84 42.24 65.52, RRM: 29.47, media: 16.00, varianza: 2240.06 Sum
#7:  Precision_prueba(1/10/100): 23.28 44.40 65.52, RRM: 30.94, media: 16.50, varianza: 2207.27 Sum
#4:  Precision_prueba(1/10/100): 22.84 42.24 63.36, RRM: 29.72, media: 20.00, varianza: 2588.08 Sum

#Prueba 45: 0.7
#14: Precision_prueba(1/10/100): 16.74 42.06 65.67, RRM: 25.39, media: 22.00, varianza: 2023.45 Sum
#10: Precision_prueba(1/10/100): 17.60 41.63 64.38, RRM: 25.81, media: 20.00, varianza: 2484.93 Sum
#7:  Precision_prueba(1/10/100): 19.31 46.78 67.38, RRM: 28.41, media: 13.00, varianza: 2320.71 Sum
#4:  Precision_prueba(1/10/100): 19.74 44.21 65.67, RRM: 27.96, media: 17.00, varianza: 2325.04 Sum

#0.0009: osmarsanchez2002loeza
#15: Precision_prueba(1/10/100): 19.74 39.06 63.09, RRM: 26.81, media: 26.00, varianza: 2035.41 Sum
#10: Precision_prueba(1/10/100): 19.31 40.77 63.95, RRM: 26.27, media: 22.00, varianza: 2499.52 Sum
#7:  Precision_prueba(1/10/100): 20.17 37.77 62.66, RRM: 25.53, media: 27.00, varianza: 2321.58 Sum
#4:  Precision_prueba(1/10/100): 18.45 36.91 62.66, RRM: 24.30, media: 27.00, varianza: 2156.52 Sum

#0.004 -> 0.001 y * 0.7: a21216301
#15: Precision_prueba(1/10/100): 15.02 34.33 60.52, RRM: 21.85, media: 32.00, varianza: 2396.68 Sum
#10: Precision_prueba(1/10/100): 18.88 38.63 62.66, RRM: 25.80, media: 38.00, varianza: 2894.55 Sum
#7:  Precision_prueba(1/10/100): 15.45 37.77 60.52, RRM: 22.04, media: 35.00, varianza: 2595.68 Sum
#4:  Precision_prueba(1/10/100): 18.88 38.20 60.52, RRM: 26.01, media: 28.00, varianza: 2549.90 Sum

#Prueba 46: 0.001, 0.7, 510DD
#13: Precision_prueba(1/10/100): 23.71 39.22 62.93, RRM: 29.23, media: 25.50, varianza: 2194.96 Sum
#10: Precision_prueba(1/10/100): 19.40 46.98 66.38, RRM: 28.21, media: 17.00, varianza: 2827.88 Sum
#7:  Precision_prueba(1/10/100): 18.53 41.81 63.36, RRM: 26.51, media: 22.00, varianza: 2716.64 Sum
#4:  Precision_prueba(1/10/100): 23.28 42.24 63.36, RRM: 29.67, media: 21.00, varianza: 2195.49 Sum

#0.003 -> 0.001 y * 0.71: a21216301
#13: Precision_prueba(1/10/100): 19.83 43.10 65.09, RRM: 27.32, media: 23.50, varianza: 2674.78 Sum
#10: Precision_prueba(1/10/100): 18.97 37.50 64.22, RRM: 25.05, media: 30.50, varianza: 2369.59 Sum
#7:  Precision_prueba(1/10/100): 20.69 41.38 63.36, RRM: 27.69, media: 24.00, varianza: 2639.41 Sum
#4:  Precision_prueba(1/10/100): 16.38 37.93 62.50, RRM: 23.96, media: 24.50, varianza: 2360.89 Sum

#0.0008 -> 0.001 y * 0.71: osmarsanchez2002loeza
#13: Precision_prueba(1/10/100): 20.69 41.81 63.79, RRM: 27.60, media: 22.00, varianza: 2766.16 Sum
#10: Precision_prueba(1/10/100): 21.12 45.26 68.10, RRM: 29.14, media: 15.00, varianza: 2211.48 Sum
#7:  Precision_prueba(1/10/100): 21.55 43.10 65.52, RRM: 28.68, media: 16.50, varianza: 2526.95 Sum
#4:  Precision_prueba(1/10/100): 22.84 42.24 62.93, RRM: 29.33, media: 25.00, varianza: 2366.83 Sum

#Prueba 47: 0.001, 0.71, 510DD 0.1Dropout
#13: Precision_prueba(1/10/100): 15.95 41.38 62.07, RRM: 24.37, media: 35.00, varianza: 3304.57 Sum
#10: Precision_prueba(1/10/100): 20.26 38.36 59.48, RRM: 26.12, media: 31.50, varianza: 3884.10 Sum
#6:  Precision_prueba(1/10/100): 15.52 38.79 56.90, RRM: 22.66, media: 46.00, varianza: 3361.97 Sum
#4:  Precision_prueba(1/10/100): 17.24 39.66 63.36, RRM: 24.86, media: 22.50, varianza: 4128.46 Sum

#0.001, 0.71, 510DD 0.2Dropout FastText: osmarsanchez2002loeza
#13: Precision_prueba(1/10/100): 22.41 40.09 63.79, RRM: 28.47, media: 22.50, varianza: 3940.77 Sum
#10: Precision_prueba(1/10/100): 23.28 43.97 62.93, RRM: 30.12, media: 19.50, varianza: 3571.34 Sum
#6:  Precision_prueba(1/10/100): 22.41 42.67 65.09, RRM: 29.37, media: 17.50, varianza: 3224.15 Sum
#4:  Precision_prueba(1/10/100): 18.10 34.91 61.64, RRM: 23.74, media: 31.00, varianza: 3551.02 Sum

#Prueba 48: 0.001, 0.72, 510DD, 0.2Dropout, Word2Vec
#12: Precision_prueba(1/10/100): 21.46 40.34 63.09, RRM: 28.70, media: 22.00, varianza: 3029.31 Sum
#10: Precision_prueba(1/10/100): 23.61 45.06 66.95, RRM: 31.04, media: 16.00, varianza: 2231.03 Sum
#6:  Precision_prueba(1/10/100): 21.03 42.92 66.52, RRM: 27.96, media: 16.00, varianza: 2402.50 Sum
#4:  Precision_prueba(1/10/100): 21.46 42.49 63.52, RRM: 28.99, media: 20.00, varianza: 1890.20 Sum

#0.0008 -> 0.001, 0.72, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#12: Precision_prueba(1/10/100): 18.88 44.64 71.24, RRM: 27.09, media: 16.00, varianza: 1224.71 Ato
#10: Precision_prueba(1/10/100): 15.45 43.78 69.96, RRM: 25.14, media: 15.00, varianza: 1563.44 Ato
#6:  Precision_prueba(1/10/100): 21.46 49.36 73.39, RRM: 31.00, media: 13.00, varianza: 1422.22 Sum
#4:  Precision_prueba(1/10/100): 19.74 42.49 70.39, RRM: 27.51, media: 20.00, varianza: 1585.67 Sum

#0.001, 0.72, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#12: Precision_prueba(1/10/100): 17.60 45.06 67.38, RRM: 26.22, media: 21.00, varianza: 1152.53 At
#10: Precision_prueba(1/10/100): 19.31 45.06 71.24, RRM: 27.27, media: 17.00, varianza: 1548.23 Ato
#6:  Precision_prueba(1/10/100): 20.17 48.07 75.97, RRM: 29.17, media: 14.00, varianza: 1500.34 Sum
#4:  Precision_prueba(1/10/100): 16.31 41.20 70.82, RRM: 24.84, media: 19.00, varianza: 1361.16 Ato

#Prueba 49: 0.001, 0.73, 510DD, 0.2Dropout, Word2Vec
#11: Precision_prueba(1/10/100): 20.51 45.30 67.95, RRM: 28.40, media: 16.50, varianza: 2688.34 Sum
#10: Precision_prueba(1/10/100): 22.65 43.59 65.38, RRM: 29.94, media: 19.00, varianza: 2536.52 Sum
#6:  Precision_prueba(1/10/100): 21.79 42.74 67.09, RRM: 28.58, media: 20.50, varianza: 2640.87 Sum
#4:  Precision_prueba(1/10/100): 21.37 43.59 63.25, RRM: 28.19, media: 18.00, varianza: 3334.76 Sum

#0.0007 -> 0.001, 0.73, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#11: Precision_prueba(1/10/100): 18.80 45.73 71.37, RRM: 27.76, media: 17.50, varianza: 1309.89 Ato
#10: Precision_prueba(1/10/100): 23.93 42.74 68.80, RRM: 30.33, media: 15.50, varianza: 1307.18 Sum
#6:  Precision_prueba(1/10/100): 19.66 41.88 70.09, RRM: 27.41, media: 17.50, varianza: 1152.65 Ato
#4:  Precision_prueba(1/10/100): 17.95 40.17 70.09, RRM: 25.20, media: 20.50, varianza: 1629.87 Ato

#0.001, 0.73, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#11: Precision_prueba(1/10/100): 20.09 45.30 73.08, RRM: 28.45, media: 12.50, varianza: 1327.00 Sum
#10: Precision_prueba(1/10/100): 18.38 43.59 70.51, RRM: 26.47, media: 16.00, varianza: 1173.55 Ato
#6:  Precision_prueba(1/10/100): 17.09 41.03 69.23, RRM: 26.22, media: 16.00, varianza: 1962.74 Sum
#4:  Precision_prueba(1/10/100): 16.67 43.16 71.37, RRM: 25.42, media: 14.00, varianza: 1531.91 Ato

#0.0006 -> 0.001, 0.8, 510DD, 0.2Dropout, FastText: chpalomoo
#11: Precision_prueba(1/10/100): 15.88 41.20 72.96, RRM: 24.64, media: 18.00, varianza: 1482.73 Sum
#10: Precision_prueba(1/10/100): 15.02 44.64 71.24, RRM: 24.12, media: 15.00, varianza: 1650.82 Ato
#6:  Precision_prueba(1/10/100): 15.88 42.92 69.96, RRM: 24.88, media: 18.00, varianza: 1516.87 Sum
#3:  Precision_prueba(1/10/100): 16.74 42.92 74.25, RRM: 25.19, media: 17.00, varianza: 1116.18 Sum

#0.001, 0.8, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#11: Precision_prueba(1/10/100): 15.88 43.78 72.53, RRM: 25.12, media: 15.00, varianza: 1149.51 Ato
#10: Precision_prueba(1/10/100): 17.60 43.78 71.67, RRM: 26.72, media: 15.00, varianza: 1404.45 Ato
#6:  Precision_prueba(1/10/100): 14.16 41.63 72.96, RRM: 22.57, media: 20.00, varianza: 1953.53 Ato
#3:  Precision_prueba(1/10/100): 21.03 42.92 71.67, RRM: 28.37, media: 17.00, varianza: 1781.84 Sum

#Prueba 50: 0.001, 0.74, 510DD, 0.2Dropout, Word2Vec
#11: Precision_prueba(1/10/100): 20.17 39.91 61.37, RRM: 26.40, media: 26.00, varianza: 3446.61 Sum
#10: Precision_prueba(1/10/100): 21.03 45.92 63.52, RRM: 29.08, media: 15.00, varianza: 2590.93 Sum
#6:  Precision_prueba(1/10/100): 20.60 44.64 66.52, RRM: 28.38, media: 18.00, varianza: 2407.34 Sum
#3:  Precision_prueba(1/10/100): 20.60 44.21 67.38, RRM: 28.51, media: 19.00, varianza: 2937.45 Sum

#0.0006 -> 0.001, 0.9, 510DD, 0.2Dropout, FastText: chpalomoo
#11: Precision_prueba(1/10/100): 14.59 40.77 69.96, RRM: 23.07, media: 21.00, varianza: 1648.38 Ato
#10: Precision_prueba(1/10/100): 17.17 38.63 68.67, RRM: 24.85, media: 22.00, varianza: 1126.25 Sum
#6:  Precision_prueba(1/10/100): 18.45 43.35 72.10, RRM: 26.92, media: 14.00, varianza: 1860.53 Sum
#3:  Precision_prueba(1/10/100): 17.60 42.06 69.96, RRM: 25.24, media: 17.00, varianza: 1512.39 Ato

#0.001, 0.9, 510DD, 0.2Dropout, FastText: gonzalezaldar4o
#11: Precision_prueba(1/10/100): 18.03 42.49 69.53, RRM: 26.52, media: 16.00, varianza: 1410.21 Ato
#10: Precision_prueba(1/10/100): 17.60 40.77 72.53, RRM: 25.78, media: 19.00, varianza: 1506.03 Ato
#6:  Precision_prueba(1/10/100): 15.88 39.91 72.10, RRM: 23.78, media: 21.00, varianza: 1408.99 Ato
#3:  Precision_prueba(1/10/100): 18.45 40.34 71.67, RRM: 26.09, media: 18.00, varianza: 2063.07 Ato

#Prueba 51: 0.001, 0.74, 510DD, 0.2Dropout, Word2Vec
#10: Precision_prueba(1/10/100): 18.30 37.87 63.83, RRM: 25.27, media: 30.00, varianza: 2670.93 Sum
#6:  Precision_prueba(1/10/100): 17.45 36.60 64.68, RRM: 25.31, media: 29.00, varianza: 3288.10 Sum
#3:  Precision_prueba(1/10/100): 18.30 39.15 61.28, RRM: 25.70, media: 26.00, varianza: 2438.33 Sum

#0.0007 -> 0.001, 0.71, 510DD, 0.2Dropout, FastText: chpalomoo
#10: Precision_prueba(1/10/100): 14.89 40.43 68.94, RRM: 23.18, media: 23.00, varianza: 1774.49 Sum
#6:  Precision_prueba(1/10/100): 18.72 45.53 75.32, RRM: 26.93, media: 15.00, varianza: 1539.94 Ato
#3:  Precision_prueba(1/10/100): 11.06 41.28 68.51, RRM: 21.22, media: 20.00, varianza: 1835.72 Ato

#0.001, 0.71, 510DD, 0.2Dropout, FastText: rubencoolog
#10: Precision_prueba(1/10/100): 18.30 44.68 75.32, RRM: 27.21, media: 17.00, varianza: 2108.75 Ato
#6:  Precision_prueba(1/10/100): 14.04 41.70 68.94, RRM: 22.80, media: 19.00, varianza: 1794.07 Sum
#3:  Precision_prueba(1/10/100): 19.57 43.83 72.77, RRM: 28.37, media: 17.00, varianza: 1967.25 Ato

#0.0008 -> 0.001, 0.72, 510DD, 0.2Dropout, semilla: 541859516, patience=0 FastText: chpalomoo #52
#15: Precision_prueba(1/10/100): 19.66 50.00 72.22, RRM: 29.92, media: 11.00, varianza: 1188.64 Sum
#10: Precision_prueba(1/10/100): 19.23 46.58 72.65, RRM: 27.93, media: 14.00, varianza: 1431.63 Sum
#6:  Precision_prueba(1/10/100): 16.24 46.15 67.95, RRM: 25.49, media: 14.00, varianza: 1754.68 Ato
#3:  Precision_prueba(1/10/100): 18.38 41.03 70.09, RRM: 26.65, media: 20.50, varianza: 1705.46 Ato

#0.001, 0.72, 510DD, 0.2Dropout, FastText: rubencoolog #52
#10: Precision_prueba(1/10/100): 17.95 44.44 68.80, RRM: 26.81, media: 21.50, varianza: 1648.16 Sum
#6:  Precision_prueba(1/10/100): 17.09 44.44 68.38, RRM: 25.19, media: 18.50, varianza: 1511.21 Ato
#3:  Precision_prueba(1/10/100): 18.80 45.30 70.51, RRM: 28.04, media: 18.00, varianza: 1273.05 Sum
#2:  Precision_prueba(1/10/100): 17.09 44.44 68.38, RRM: 26.19, media: 18.50, varianza: 1511.21 Ato

#Prueba 52: 0.001, 0.72, 510DD, 0.2Dropout, Word2Vec
#10: Precision_prueba(1/10/100): 20.94 43.16 65.81, RRM: 28.66, media: 18.00, varianza: 2966.64 Sum
#6:  Precision_prueba(1/10/100): 20.09 44.44 65.38, RRM: 28.13, media: 14.50, varianza: 3222.62 Sum
#3:  Precision_prueba(1/10/100): 19.23 37.61 60.68, RRM: 25.84, media: 32.50, varianza: 3111.15 Sum

#0.0008 -> 0.001, 0.72, 510DD, 0.2Dropout, patience=1 FastText: chpalomoo #52
#20: Precision_prueba(1/10/100): 17.52 46.15 71.37, RRM: 26.47, media: 13.00, varianza: 1199.06 Sum
#15: Precision_prueba(1/10/100): 21.37 44.44 74.36, RRM: 29.89, media: 18.00, varianza: 1160.77 Sum
#10: Precision_prueba(1/10/100): 22.65 45.73 74.79, RRM: 31.40, media: 15.00, varianza: 1408.75 Sum

#0.001, 0.72, 510DD, 0.2Dropout, patience=1, FastText: rubencoolog #52
#6:  Precision_prueba(1/10/100): 16.67 40.17 67.09, RRM: 24.90, media: 20.50, varianza: 1706.10 Sum
#3:  Precision_prueba(1/10/100): 17.09 40.60 68.80, RRM: 25.49, media: 19.50, varianza: 870.78 Sum
#2:  Precision_prueba(1/10/100): 18.80 41.88 67.95, RRM: 26.17, media: 21.50, varianza: 1414.65 Ato

#Prueba 53: 0.001, 0.73, 510DD, 0.2Dropout, Word2Vec
#10: Precision_prueba(1/10/100): 20.09 39.74 63.68, RRM: 25.98, media: 19.00, varianza: 3205.91 Sum
#6:  Precision_prueba(1/10/100): 21.37 44.44 66.24, RRM: 28.78, media: 20.00, varianza: 3479.93 Sum
#3:  Precision_prueba(1/10/100): 18.80 38.46 63.68, RRM: 25.26, media: 29.00, varianza: 3404.26 Sum

#0.0008 -> 0.001, 0.72, 510DD, 0.2Dropout, patience=1 FastText: chpalomoo #53
#20: Precision_prueba(1/10/100): 26.50 46.58 72.22, RRM: 32.42, media: 14.00, varianza: 1633.94 Sum
#15: Precision_prueba(1/10/100): 24.79 47.86 71.79, RRM: 32.13, media: 13.00, varianza: 1635.02 Sum
#10: Precision_prueba(1/10/100): 24.79 49.15 74.36, RRM: 33.51, media: 12.00, varianza: 2150.47 Sum

#0.001, 0.72, 510DD, 0.2Dropout, patience=1, FastText: rubencoolog #53
#6:  Precision_prueba(1/10/100): 25.64 45.30 76.07, RRM: 32.46, media: 14.00, varianza: 1877.72 Sum
#3:  Precision_prueba(1/10/100): 24.79 47.44 74.36, RRM: 31.71, media: 11.00, varianza: 1974.60 Sum
#2:  Precision_prueba(1/10/100): 26.07 46.15 75.64, RRM: 33.23, media: 16.50, varianza: 1585.09 Sum

#Prueba 54: 0.001, 0.73, 510DD, 0.2Dropout, Word2Vec
#10: Precision_prueba(1/10/100): 27.66 44.26 64.26, RRM: 32.94, media: 16.00, varianza: 4073.93 Sum
#6:  Precision_prueba(1/10/100): 22.98 39.57 58.30, RRM: 28.55, media: 26.00, varianza: 3665.67 Sum
#3:  Precision_prueba(1/10/100): 24.68 43.83 65.53, RRM: 30.95, media: 18.00, varianza: 3515.51 Sum

#0.0008 -> 0.001, 0.73, 510DD, 0.2Dropout, patience=0 FastText: chpalomoo #54
#20: Precision_prueba(1/10/100): 23.40 45.11 72.77, RRM: 30.34, media: 16.00, varianza: 2399.11 Ato
#15: Precision_prueba(1/10/100): 24.68 46.38 72.34, RRM: 31.69, media: 14.00, varianza: 2077.03 Ato
#10: Precision_prueba(1/10/100): 24.68 45.53 74.89, RRM: 31.22, media: 12.00, varianza: 2675.56 Sum

#0.001, 0.73, 510DD, 0.2Dropout, patience=0, FastText: rubencoolog #54
#6:  Precision_prueba(1/10/100): 24.68 44.26 73.62, RRM: 31.24, media: 15.00, varianza: 2213.69 Ato
#3:  Precision_prueba(1/10/100): 27.23 45.11 71.91, RRM: 32.96, media: 16.00, varianza: 2296.51 Sum
#2:  Precision_prueba(1/10/100): 25.11 45.11 72.77, RRM: 31.02, media: 17.00, varianza: 2392.48 Ato

#Prueba 55: 0.001, 0.73, 500DD, 0.2Dropout, patience=0, FastText
#10: Precision_prueba(1/10/100): 25.11 48.94 72.34, RRM: 33.23, media: 12.00, varianza: 1340.54 Sum
#6:  Precision_prueba(1/10/100): 25.96 48.51 71.49, RRM: 33.14, media: 12.00, varianza: 1335.26 Sum
#3:  Precision_prueba(1/10/100): 24.68 48.51 71.49, RRM: 33.17, media: 12.00, varianza: 1658.18 Sum

#Prueba 56: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText
#10: Precision_prueba(1/10/100): 26.50 47.44 69.23, RRM: 33.87, media: 13.00, varianza: 2001.91 Sum
#6:  Precision_prueba(1/10/100): 28.21 48.72 71.79, RRM: 33.61, media: 12.50, varianza: 2454.40 Sum
#3:  Precision_prueba(1/10/100): 28.63 50.00 71.79, RRM: 35.63, media: 10.50, varianza: 2002.76 Sum

#0.0008 -> 0.001, 0.73, 510DD, 0.2Dropout, patience=1 FastText: jatziryocao #56
#20: Precision_prueba(1/10/100): 23.50 47.44 68.80, RRM: 32.35, media: 13.00, varianza: 1869.70 Sum
#15: Precision_prueba(1/10/100): 26.92 47.01 69.66, RRM: 33.40, media: 14.50, varianza: 1710.97 Ato
#10: Precision_prueba(1/10/100): 27.78 49.57 72.65, RRM: 35.11, media: 11.50, varianza: 1545.70 Sum

#0.001, 0.73, 510DD, 0.2Dropout, patience=1, FastText: rubencoolog #56
#7:  Precision_prueba(1/10/100): 26.50 47.86 69.66, RRM: 33.76, media: 14.00, varianza: 2583.89 Sum
#3:  Precision_prueba(1/10/100): 26.50 49.15 72.22, RRM: 33.96, media: 14.00, varianza: 1827.67 Sum
#2:  Precision_prueba(1/10/100): 26.07 46.15 70.09, RRM: 32.96, media: 17.00, varianza: 1882.37 Sum

#Prueba 57: 0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText
#10: Precision_prueba(1/10/100): 29.36 44.26 70.21, RRM: 35.20, media: 17.00, varianza: 2025.73 Sum
#6:  Precision_prueba(1/10/100): 30.21 54.04 73.62, RRM: 36.88, media: 9.00, varianza: 1231.25 Sum
#3:  Precision_prueba(1/10/100): 30.64 46.81 73.62, RRM: 36.39, media: 14.00, varianza: 1976.45 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=1 FastText: jatziryocao #57
#20: Precision_prueba(1/10/100): 28.09 48.94 75.32, RRM: 35.23, media: 12.00, varianza: 1328.40 Sum
#15: Precision_prueba(1/10/100): 26.38 44.68 71.49, RRM: 32.42, media: 17.00, varianza: 1427.20 Sum
#10: Precision_prueba(1/10/100): 27.23 48.51 75.74, RRM: 34.80, media: 11.00, varianza: 1981.72 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText: rubencoolog #57
#7:  Precision_prueba(1/10/100): 26.81 48.51 75.74, RRM: 33.40, media: 12.00, varianza: 1828.57 Ato
#3:  Precision_prueba(1/10/100): 29.36 48.09 74.47, RRM: 34.98, media: 12.00, varianza: 1515.56 Sum
#2:  Precision_prueba(1/10/100): 27.23 46.81 74.47, RRM: 33.83, media: 14.00, varianza: 1611.70 Sum

#Prueba 58: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 28.09 50.21 71.91, RRM: 34.48, media: 10.00, varianza: 1703.90 Sum
#6:  Precision_prueba(1/10/100): 27.23 48.51 71.06, RRM: 34.02, media: 12.00, varianza: 1536.44 Sum
#3:  Precision_prueba(1/10/100): 26.81 48.94 69.36, RRM: 33.40, media: 11.00, varianza: 1656.02 Ato

#Prueba 59: 0.001, 0.73, 500DD, 0.2Dropout, patience=4, FastText
#10: Precision_prueba(1/10/100): 23.08 46.15 75.64, RRM: 31.45, media: 13.00, varianza: 1780.05 Sum
#6:  Precision_prueba(1/10/100): 26.07 48.72 72.22, RRM: 33.57, media: 13.00, varianza: 2016.51 Sum
#3:  Precision_prueba(1/10/100): 28.21 45.73 72.65, RRM: 34.27, media: 14.00, varianza: 1679.28 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #59
#20: Precision_prueba(1/10/100): 29.06 45.73 74.79, RRM: 34.62, media: 16.50, varianza: 2018.98 Sum
#15: Precision_prueba(1/10/100): 25.64 49.15 78.21, RRM: 33.26, media: 11.00, varianza: 1578.98 Sum
#10: Precision_prueba(1/10/100): 25.21 51.28 73.50, RRM: 32.99, media: 10.00, varianza: 1866.36 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: rubencoolog #59
#7:  Precision_prueba(1/10/100): 25.64 46.15 74.36, RRM: 31.99, media: 14.50, varianza: 2259.62 Sum
#3:  Precision_prueba(1/10/100): 22.22 45.30 74.79, RRM: 30.11, media: 15.00, varianza: 1794.20 Ato

#Prueba 60: 0.001, 0.73, 500DD, 0.2Dropout, patience=5, FastText
#10: Precision_prueba(1/10/100): 26.92 43.16 68.80, RRM: 32.02, media: 21.00, varianza: 1876.56 Sum
#6:  Precision_prueba(1/10/100): 26.50 46.58 67.52, RRM: 32.96, media: 15.00, varianza: 1303.14 Ato
#3:  Precision_prueba(1/10/100): 26.92 46.58 67.52, RRM: 32.72, media: 15.50, varianza: 1528.32 Ato

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #60
#20: Precision_prueba(1/10/100): 23.93 42.31 68.80, RRM: 30.91, media: 22.00, varianza: 2135.98 Sum
#15: Precision_prueba(1/10/100): 25.21 45.73 64.96, RRM: 32.30, media: 16.00, varianza: 1614.93 Sum
#10: Precision_prueba(1/10/100): 25.21 47.01 70.51, RRM: 32.36, media: 14.00, varianza: 2075.10 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: salvarogs #60
#7:  Precision_prueba(1/10/100): 24.79 43.59 72.22, RRM: 31.29, media: 17.00, varianza: 1906.44 Sum
#3:  Precision_prueba(1/10/100): 22.22 46.58 68.38, RRM: 30.19, media: 17.00, varianza: 1949.65 Ato
#2:  Precision_prueba(1/10/100): 26.07 43.16 71.37, RRM: 31.53, media: 21.00, varianza: 2192.55 Sum

#Prueba 61: 0.001, 0.73, 500DD, 0.2Dropout, patience=6, FastText
#10: Precision_prueba(1/10/100): 22.65 43.16 71.79, RRM: 29.64, media: 17.50, varianza: 1711.01 Sum
#6:  Precision_prueba(1/10/100): 25.21 50.00 75.21, RRM: 32.93, media: 10.50, varianza: 1702.53 Ato
#3:  Precision_prueba(1/10/100): 23.93 44.02 70.09, RRM: 31.05, media: 17.50, varianza: 1709.74 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=3 FastText: jatziryocao #61
#20: Precision_prueba(1/10/100): 22.22 46.15 73.50, RRM: 29.22, media: 16.50, varianza: 1962.43 Sum
#15: Precision_prueba(1/10/100): 22.65 43.59 70.51, RRM: 29.72, media: 16.00, varianza: 1868.86 At
#10: Precision_prueba(1/10/100): 23.08 46.58 69.23, RRM: 31.01, media: 13.50, varianza: 1780.36 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText: salvarogs #61
#7:  Precision_prueba(1/10/100): 24.36 47.01 75.64, RRM: 32.29, media: 13.50, varianza: 2041.99 Sum
#3:  Precision_prueba(1/10/100): 22.65 47.01 74.36, RRM: 30.28, media: 15.00, varianza: 2239.58 Ato
#2:  Precision_prueba(1/10/100): 23.93 50.43 77.78, RRM: 32.30, media: 10.00, varianza: 1551.38 Sum

#Prueba 62: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 25.32 47.21 76.39, RRM: 32.22, media: 15.00, varianza: 1257.85 Sum
#6:  Precision_prueba(1/10/100): 21.89 51.93 70.82, RRM: 31.49, media: 9.00, varianza: 1369.05 Sum
#3:  Precision_prueba(1/10/100): 24.46 46.78 71.67, RRM: 31.92, media: 13.00, varianza: 1134.47 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #62
#20: Precision_prueba(1/10/100): 26.18 47.21 73.82, RRM: 33.45, media: 14.00, varianza: 1540.83 Sum
#15: Precision_prueba(1/10/100): 27.04 50.21 73.39, RRM: 34.91, media: 10.00, varianza: 1380.31 Sum
#10: Precision_prueba(1/10/100): 27.90 49.79 75.11, RRM: 35.62, media: 11.00, varianza: 1138.75 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: salvarogs #62
#7:  Precision_prueba(1/10/100): 26.18 45.49 73.39, RRM: 32.61, media: 19.00, varianza: 1211.96 Sum
#3:  Precision_prueba(1/10/100): 25.75 45.92 70.82, RRM: 32.44, media: 14.00, varianza: 1293.24 Sum
#2:  Precision_prueba(1/10/100): 25.75 46.35 73.82, RRM: 33.66, media: 13.00, varianza: 1573.89 Ato

#Prueba 63: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 23.40 50.64 71.91, RRM: 32.47, media: 10.00, varianza: 1732.11 Sum
#6:  Precision_prueba(1/10/100): 28.09 48.51 75.32, RRM: 35.34, media: 12.00, varianza: 1576.27 Sum
#3:  Precision_prueba(1/10/100): 25.53 46.81 73.19, RRM: 33.39, media: 14.00, varianza: 1443.87 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #63
#20: Precision_prueba(1/10/100): 24.68 48.94 74.89, RRM: 32.61, media: 11.00, varianza: 1961.84 Sum
#15: Precision_prueba(1/10/100): 24.68 49.36 77.45, RRM: 32.84, media: 11.00, varianza: 2004.50 Sum
#10: Precision_prueba(1/10/100): 25.11 51.49 76.60, RRM: 33.94, media: 9.00, varianza: 1707.56 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: salvarogs #63
#7:  Precision_prueba(1/10/100): 28.09 48.09 73.62, RRM: 34.82, media: 11.00, varianza: 1601.21 Sum
#3:  Precision_prueba(1/10/100): 24.68 47.23 76.17, RRM: 32.58, media: 15.00, varianza: 1157.68 Sum
#2:  Precision_prueba(1/10/100): 24.68 50.64 77.02, RRM: 33.88, media: 10.00, varianza: 1449.34 Ato

#Prueba 64: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 21.28 43.40 71.06, RRM: 29.58, media: 19.00, varianza: 1622.33 Sum
#6:  Precision_prueba(1/10/100): 22.98 42.98 74.04, RRM: 29.06, media: 20.00, varianza: 1359.03 Ato

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #64
#20: Precision_prueba(1/10/100): 23.40 47.23 71.49, RRM: 31.08, media: 14.00, varianza: 1239.51 Sum
#15: Precision_prueba(1/10/100): 22.13 48.94 73.19, RRM: 30.04, media: 13.00, varianza: 1124.67 Sum
#10: Precision_prueba(1/10/100): 19.57 44.26 70.64, RRM: 27.38, media: 16.00, varianza: 1225.44 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: salvarogs #64
#7:  Precision_prueba(1/10/100): 21.28 47.23 72.77, RRM: 30.28, media: 13.00, varianza: 1200.64 Sum
#3:  Precision_prueba(1/10/100): 20.43 43.83 69.79, RRM: 27.97, media: 18.00, varianza: 1587.39 Sum
#2:  Precision_prueba(1/10/100): 21.28 48.51 73.62, RRM: 30.58, media: 12.00, varianza: 1577.12 Sum

#Prueba 65: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 24.58 49.58 72.46, RRM: 31.97, media: 11.00, varianza: 1483.24 Sum
#6:  Precision_prueba(1/10/100): 23.31 46.19 74.15, RRM: 30.84, media: 14.00, varianza: 1683.83 Sum
#4:  Precision_prueba(1/10/100): 25.00 44.07 74.15, RRM: 30.85, media: 14.50, varianza: 1771.79 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #65
#20: Precision_prueba(1/10/100): 24.15 47.03 71.61, RRM: 31.31, media: 16.00, varianza: 1630.88 Sum
#15: Precision_prueba(1/10/100): 23.73 43.22 73.73, RRM: 30.79, media: 18.00, varianza: 1676.75 Sum
#10: Precision_prueba(1/10/100): 23.31 46.19 73.73, RRM: 30.41, media: 12.50, varianza: 1422.02 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: salvarogs #65
#7:  Precision_prueba(1/10/100): 24.58 47.88 75.42, RRM: 32.13, media: 13.50, varianza: 1307.56 Sum
#3:  Precision_prueba(1/10/100): 25.00 47.03 73.31, RRM: 31.63, media: 13.00, varianza: 1425.26 Sum

#Prueba 66: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 26.38 50.21 76.60, RRM: 34.58, media: 10.00, varianza: 2026.68 Ato
#6:  Precision_prueba(1/10/100): 28.51 50.21 71.49, RRM: 36.10, media: 10.00, varianza: 1962.53 Sum
#4:  Precision_prueba(1/10/100): 25.96 48.94 71.06, RRM: 33.88, media: 13.00, varianza: 1927.03 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: jatziryocao #66
#20: Precision_prueba(1/10/100): 26.38 48.94 73.62, RRM: 34.43, media: 13.00, varianza: 1786.26 Ato
#15: Precision_prueba(1/10/100): 27.23 51.49 73.19, RRM: 35.51, media: 10.00, varianza: 2494.76 Sum
#10: Precision_prueba(1/10/100): 26.38 48.94 72.77, RRM: 34.04, media: 12.00, varianza: 1567.95 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #66
#7:  Precision_prueba(1/10/100): 25.11 50.64 73.19, RRM: 33.83, media: 9.00, varianza: 1914.14 Sum
#3:  Precision_prueba(1/10/100): 26.38 49.79 75.74, RRM: 33.99, media: 11.00, varianza: 1967.52 Sum
#2:  Precision_prueba(1/10/100): 28.09 51.91 73.62, RRM: 36.29, media: 9.00, varianza: 1865.55 Sum

#Prueba 67: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 26.60 47.60 69.80, RRM: 32.89, media: 14.00, varianza: 1493.01 Sum
#6:  Precision_prueba(1/10/100): 25.80 46.20 70.60, RRM: 32.30, media: 15.00, varianza: 1556.00 Sum
#4:  Precision_prueba(1/10/100): 26.60 46.60 70.60, RRM: 33.08, media: 17.00, varianza: 1647.81 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #67
#20: Precision_prueba(1/10/100): 27.00 47.00 71.40, RRM: 33.93, media: 15.00, varianza: 1182.19 Sum
#15: Precision_prueba(1/10/100): 25.40 47.00 71.40, RRM: 32.37, media: 15.00, varianza: 1606.63 Sum
#10: Precision_prueba(1/10/100): 27.20 48.80 73.20, RRM: 34.46, media: 11.00, varianza: 1535.37 Ato

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #67
#7: Precision_prueba(1/10/100): 24.40 46.20 72.80, RRM: 31.77, media: 14.50, varianza: 1250.83 Ato
#3: Precision_prueba(1/10/100): 24.40 46.60 71.20, RRM: 32.03, media: 14.00, varianza: 1466.66 Ato

#Prueba 68: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 24.60 47.00 71.00, RRM: 31.75, media: 13.00, varianza: 1671.44 Sum
#6:  Precision_prueba(1/10/100): 24.40 45.40 72.20, RRM: 31.70, media: 16.50, varianza: 1310.16 Sum
#4:  Precision_prueba(1/10/100): 24.80 45.40 70.20, RRM: 31.76, media: 17.00, varianza: 1413.84 Sum

#Prueba 69: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 26.80 48.60 74.80, RRM: 34.31, media: 11.00, varianza: 1902.09 Sum
#6:  Precision_prueba(1/10/100): 25.20 46.60 72.60, RRM: 31.93, media: 15.00, varianza: 2136.14 Sum
#4:  Precision_prueba(1/10/100): 25.20 46.60 70.60, RRM: 32.26, media: 13.50, varianza: 1979.37 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #69
#20: Precision_prueba(1/10/100): 26.00 46.80 71.20, RRM: 32.26, media: 14.50, varianza: 1985.22 Ato
#15: Precision_prueba(1/10/100): 24.80 46.80 70.60, RRM: 32.26, media: 13.50, varianza: 1394.60 Sum
#10: Precision_prueba(1/10/100): 24.60 47.20 73.20, RRM: 32.83, media: 15.00, varianza: 1838.77 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #69
#7: Precision_prueba(1/10/100): 24.20 47.60 71.60, RRM: 31.87, media: 12.00, varianza: 1825.05 Sum
#3: Precision_prueba(1/10/100): 27.00 47.00 72.60, RRM: 34.09, media: 13.00, varianza: 2085.72 Sum
#2: Precision_prueba(1/10/100): 24.00 46.60 71.60, RRM: 31.91, media: 15.50, varianza: 1820.09 Sum

#Prueba 70: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 24.40 45.40 71.20, RRM: 31.43, media: 15.50, varianza: 1731.44 Sum
#7:  Precision_prueba(1/10/100): 25.40 43.40 71.40, RRM: 31.77, media: 17.00, varianza: 1650.67 Sum
#4:  Precision_prueba(1/10/100): 24.20 47.40 71.60, RRM: 31.98, media: 13.00, varianza: 1823.40 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #70
#20: Precision_prueba(1/10/100): 24.20 45.40 75.20, RRM: 30.64, media: 15.00, varianza: 1566.64 Sum
#14: Precision_prueba(1/10/100): 26.20 46.00 72.40, RRM: 33.15, media: 15.00, varianza: 1276.55 Sum
#10: Precision_prueba(1/10/100): 24.20 47.40 72.80, RRM: 31.68, media: 13.00, varianza: 1667.47 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #70
#8:  Precision_prueba(1/10/100): 24.80 47.40 71.20, RRM: 32.25, media: 13.00, varianza: 1600.54 Sum
#3:  Precision_prueba(1/10/100): 23.40 47.80 72.40, RRM: 31.40, media: 12.00, varianza: 1647.82 Sum
#2:  Precision_prueba(1/10/100): 23.60 47.00 72.00, RRM: 30.96, media: 13.00, varianza: 1442.19 Sum

#Prueba 71: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 1.20 6.00 17.20, RRM: 2.90, media: 1475.50, varianza: 6125.98 Sum
#7:  Precision_prueba(1/10/100): 1.40 5.80 15.80, RRM: 2.84, media: 1251.00, varianza: 6060.78 Sum
#4:  Precision_prueba(1/10/100): 1.40 6.00 20.00, RRM: 3.03, media: 1375.00, varianza: 6372.62 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #71
#21: Precision_prueba(1/10/100): 1.00 6.20 18.40, RRM: 2.80, media: 1557.00, varianza: 6562.51 Loc
#14: Precision_prueba(1/10/100): 1.60 5.00 18.80, RRM: 3.00, media: 1347.50, varianza: 5948.22 Sum
#10: Precision_prueba(1/10/100): 1.80 4.80 14.80, RRM: 3.01, media: 2059.50, varianza: 6497.81 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #71
#8:  Precision_prueba(1/10/100): 1.20 3.60 10.80, RRM: 2.13, media: 3381.00, varianza: 7252.26 Sum
#3:  Precision_prueba(1/10/100): 2.00 5.60 16.80, RRM: 3.36, media: 1813.00, varianza: 6849.69 Sum
#2:  Precision_prueba(1/10/100): 1.60 5.60 18.60, RRM: 3.14, media: 1401.50, varianza: 5930.92 Sum

#Prueba 72: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText
#10: Precision_prueba(1/10/100): 2.68 9.87 27.80, RRM: 5.17, media: 633.00, varianza: 5130.28 Sum
#7:  Precision_prueba(1/10/100): 2.07 10.25 28.32, RRM: 4.87, media: 596.00, varianza: 5358.31 Sum
#4:  Precision_prueba(1/10/100): 2.35 10.29 30.45, RRM: 5.03, media: 526.00, varianza: 5264.80 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #72
#21: Precision_prueba(1/10/100): 2.90 9.90 28.06, RRM: 5.47, media: 650.00, varianza: 5721.01 Sum
#14: Precision_prueba(1/10/100): 2.29 9.16 28.36, RRM: 4.92, media: 762.00, varianza: 5769.94 Sum
#10: Precision_prueba(1/10/100): 1.70 8.18 24.81, RRM: 3.98, media: 968.00, varianza: 5752.80 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #72
#8:  Precision_prueba(1/10/100): 2.24 10.25 27.45, RRM: 4.94, media: 729.00, varianza: 5471.37 Sum
#3:  Precision_prueba(1/10/100): 2.68 9.64 28.28, RRM: 5.26, media: 744.00, varianza: 5967.06 Sum
#2:  Precision_prueba(1/10/100): 2.35 9.77 28.36, RRM: 5.15, media: 692.00, varianza: 6096.94 Sum

#Prueba 73: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 61.48%, 9
#10: Precision_prueba(1/10/100): 3.53 9.44 23.67, RRM: 5.68, media: 995.00, varianza: 5171.64 Sum
#7:  Precision_prueba(1/10/100): 2.90 10.33 26.49, RRM: 5.43, media: 747.00, varianza: 5014.45 Sum
#4:  Precision_prueba(1/10/100): 3.20 10.71 28.39, RRM: 5.90, media: 598.00, varianza: 4640.24 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #73
#21: Precision_prueba(1/10/100): 3.37 10.91 27.00, RRM: 6.00, media: 713.50, varianza: 4461.87 Sum
#14: Precision_prueba(1/10/100): 3.05 12.62 30.83, RRM: 6.36, media: 532.00, varianza: 4356.26 Sum
#10: Precision_prueba(1/10/100): 3.09 10.44 27.56, RRM: 5.78, media: 681.00, varianza: 4831.38 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #73
#8:  Precision_prueba(1/10/100): 2.95 11.90 31.21, RRM: 6.22, media: 488.50, varianza: 4218.43 Sum
#3:  Precision_prueba(1/10/100): 2.38 10.27 27.36, RRM: 5.13, media: 681.00, varianza: 4578.91 Sum
#2:  Precision_prueba(1/10/100): 2.83 9.50 23.68, RRM: 5.11, media: 1082.00, varianza: 5287.22 Sum

#Prueba 74: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 61.76%, 9
#10: Precision_prueba(1/10/100): 26.00 45.20 68.20, RRM: 32.35, media: 17.00, varianza: 1791.18 Sum
#7:  Precision_prueba(1/10/100): 24.00 45.40 66.80, RRM: 31.58, media: 16.00, varianza: 1888.18 Sum
#4:  Precision_prueba(1/10/100): 25.20 46.20 70.60, RRM: 32.40, media: 14.00, varianza: 2394.64 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #74
#21: Precision_prueba(1/10/100): 26.00 42.20 66.40, RRM: 31.77, media: 22.50, varianza: 2195.41 Sum
#14: Precision_prueba(1/10/100): 25.00 45.00 68.60, RRM: 31.69, media: 16.00, varianza: 2348.41 Sum
#10: Precision_prueba(1/10/100): 25.40 45.00 68.80, RRM: 31.96, media: 17.00, varianza: 2221.12 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #74
#8:  Precision_prueba(1/10/100): 25.00 45.20 68.80, RRM: 32.09, media: 17.50, varianza: 2256.85 Sum
#3:  Precision_prueba(1/10/100): 25.00 43.80 68.00, RRM: 31.59, media: 20.00, varianza: 2388.57 Sum
#2:  Precision_prueba(1/10/100): 24.60 44.00 67.80, RRM: 31.39, media: 17.00, varianza: 2138.96 Sum

#Prueba 75: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 62.53%, 10
#10: Precision_prueba(1/10/100): 3.03 11.07 29.04, RRM: 5.78, media: 657.00, varianza: 4602.71 Sum
#7:  Precision_prueba(1/10/100): 2.40 9.03 25.42, RRM: 4.76, media: 1029.00, varianza: 5146.62 Sum
#4:  Precision_prueba(1/10/100): 3.60 11.38 28.27, RRM: 6.44, media: 701.00, varianza: 4366.06 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #75
#21: Precision_prueba(1/10/100): 2.18 8.81 22.70, RRM: 4.48, media: 1103.00, varianza: 5333.21 Sum
#14: Precision_prueba(1/10/100): 2.40 10.05 28.45, RRM: 5.14, media: 624.00, varianza: 4431.04 Sum
#10: Precision_prueba(1/10/100): 2.66 11.14 28.52, RRM: 5.60, media: 647.00, varianza: 4668.31 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #75
#8:  Precision_prueba(1/10/100): 2.22 9.31 26.95, RRM: 4.76, media: 620.00, varianza: 4464.42 Sum
#3:  Precision_prueba(1/10/100): 2.40 11.45 28.36, RRM: 5.34, media: 715.00, varianza: 4771.53 Sum
#1:  Precision_prueba(1/10/100): 2.75 9.83 26.68, RRM: 5.29, media: 737.00, varianza: 4625.83 Sum

#Prueba 76: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 62.53%, 10
#10: Precision_prueba(1/10/100): 24.40 45.60 68.20, RRM: 31.31, media: 16.00, varianza: 2288.77 Sum
#7:  Precision_prueba(1/10/100): 22.20 44.60 67.20, RRM: 29.58, media: 16.50, varianza: 2149.20 Sum
#4:  Precision_prueba(1/10/100): 24.00 42.40 66.60, RRM: 30.05, media: 21.50, varianza: 2650.55 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #76
#21: Precision_prueba(1/10/100): 24.20 45.00 67.80, RRM: 30.60, media: 18.00, varianza: 2558.65 Sum
#14: Precision_prueba(1/10/100): 24.00 45.80 68.00, RRM: 31.14, media: 17.50, varianza: 2431.25 Sum
#10: Precision_prueba(1/10/100): 24.60 47.00 70.00, RRM: 31.59, media: 16.00, varianza: 2628.48 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #76
#8:  Precision_prueba(1/10/100): 23.60 42.60 68.80, RRM: 30.15, media: 20.50, varianza: 2500.66 Sum
#3:  Precision_prueba(1/10/100): 24.80 43.40 67.60, RRM: 30.87, media: 18.50, varianza: 2287.15 Sum
#1:  Precision_prueba(1/10/100): 23.20 42.20 66.00, RRM: 29.34, media: 18.50, varianza: 2514.10 Sum

#Prueba 77: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 62.94%, 11
#10: Precision_prueba(1/10/100): 2.77 11.14 28.52, RRM: 5.74, media: 646.00, varianza: 4254.11 Sum
#6:  Precision_prueba(1/10/100): 2.83 9.31 27.32, RRM: 5.22, media: 672.00, varianza: 4531.89 Sum
#4:  Precision_prueba(1/10/100): 2.42 9.44 27.77, RRM: 4.88, media: 680.00, varianza: 4434.80 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #77
#21: Precision_prueba(1/10/100): 1.94 10.16 27.64, RRM: 4.89, media: 718.00, varianza: 4355.58 Sum
#14: Precision_prueba(1/10/100): 2.53 9.83 29.82, RRM: 5.16, media: 567.00, varianza: 4318.41 Sum
#10: Precision_prueba(1/10/100): 2.62 9.74 27.08, RRM: 5.14, media: 731.00, varianza: 4540.94 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: a21216301 #77
#8:  Precision_prueba(1/10/100): 2.24 10.75 29.74, RRM: 5.14, media: 606.00, varianza: 4546.35 Sum
#4:  Precision_prueba(1/10/100): 2.24 10.75 29.74, RRM: 5.14, media: 606.00, varianza: 4546.35 Sum
#3:  Precision_prueba(1/10/100): 2.24 10.75 29.74, RRM: 5.14, media: 606.00, varianza: 4546.35 Sum

#Prueba 78: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 63.54%, 11
#10: Precision_prueba(1/10/100): 22.80 43.20 69.40, RRM: 29.68, media: 19.00, varianza: 1863.32 Sum
#6:  Precision_prueba(1/10/100): 24.00 43.80 70.40, RRM: 30.72, media: 17.00, varianza: 2414.59 Sum
#4:  Precision_prueba(1/10/100): 24.00 44.60 68.60, RRM: 30.69, media: 18.50, varianza: 1616.99 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarloeza77suaste #78
#21: Precision_prueba(1/10/100): 23.60 44.60 69.20, RRM: 30.31, media: 18.00, varianza: 2229.22 Sum
#14: Precision_prueba(1/10/100): 24.40 42.60 70.40, RRM: 30.41, media: 18.50, varianza: 1968.34 Sum
#10: Precision_prueba(1/10/100): 23.60 45.20 71.00, RRM: 30.74, media: 18.00, varianza: 1924.60 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #78
#8:  Precision_prueba(1/10/100): 24.80 43.80 68.40, RRM: 31.17, media: 16.50, varianza: 1907.08 Sum
#4:  Precision_prueba(1/10/100): 23.60 44.40 70.40, RRM: 30.39, media: 19.00, varianza: 2022.57 Sum
#3:  Precision_prueba(1/10/100): 22.60 42.40 70.80, RRM: 29.35, media: 19.00, varianza: 1826.95 Sum

#Prueba 79: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 63.85%, 12
#10: Precision_prueba(1/10/100): 3.25 10.97 26.09, RRM: 5.94, media: 875.00, varianza: 4515.50 Sum
#6:  Precision_prueba(1/10/100): 3.25 11.18 27.58, RRM: 6.02, media: 715.00, varianza: 4220.37 Sum
#4:  Precision_prueba(1/10/100): 2.24 9.37 27.67, RRM: 4.77, media: 710.00, varianza: 4263.34 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #79
#21: Precision_prueba(1/10/100): 3.75 13.78 31.89, RRM: 7.28, media: 538.00, varianza: 3885.29 Sum
#14: Precision_prueba(1/10/100): 3.45 8.87 21.85, RRM: 5.42, media: 1310.00, varianza: 4966.36 Sum
#10: Precision_prueba(1/10/100): 2.90 10.70 27.32, RRM: 5.53, media: 749.00, varianza: 4381.87 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #79
#8:  Precision_prueba(1/10/100): 3.34 11.53 26.51, RRM: 6.30, media: 769.00, varianza: 4372.52 Sum
#4:  Precision_prueba(1/10/100): 3.45 10.64 24.52, RRM: 5.91, media: 1064.00, varianza: 4781.89 Sum
#3:  Precision_prueba(1/10/100): 2.18 10.84 27.36, RRM: 5.14, media: 698.00, varianza: 4309.26 Sum

#Prueba 80: 0.001, 0.73, 500DD, 0.2Dropout, patience=3, FastText, 63.85%, 12
#10: Precision_prueba(1/10/100): 21.80 39.80 66.80, RRM: 28.33, media: 26.00, varianza: 2136.84 Sum
#6:  Precision_prueba(1/10/100): 21.60 42.80 66.20, RRM: 28.53, media: 21.00, varianza: 2408.20 Sum
#4:  Precision_prueba(1/10/100): 22.80 41.00 66.20, RRM: 29.07, media: 24.00, varianza: 2172.41 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #80
#21: Precision_prueba(1/10/100): 23.20 43.00 66.40, RRM: 29.67, media: 24.00, varianza: 2577.17 Sum
#14: Precision_prueba(1/10/100): 22.40 43.20 67.20, RRM: 29.60, media: 22.00, varianza: 2421.89 Sum
#10: Precision_prueba(1/10/100): 22.20 41.20 66.60, RRM: 28.81, media: 26.00, varianza: 2315.82 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #80
#8:  Precision_prueba(1/10/100): 21.80 41.20 67.40, RRM: 28.49, media: 24.00, varianza: 2158.52 Sum
#4:  Precision_prueba(1/10/100): 22.60 41.40 66.20, RRM: 28.67, media: 22.00, varianza: 2089.05 Sum
#3:  Precision_prueba(1/10/100): 24.60 44.00 65.40, RRM: 30.49, media: 20.50, varianza: 2329.64 Sum

#Prueba 81: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.45%, 13
#9:  Precision_prueba(1/10/100): 2.48 11.42 27.47, RRM: 5.58, media: 729.00, varianza: 4182.25 Sum
#6:  Precision_prueba(1/10/100): 2.07 9.53 27.80, RRM: 4.80, media: 656.00, varianza: 4391.20 Sum
#4:  Precision_prueba(1/10/100): 2.35 11.99 29.28, RRM: 5.32, media: 587.00, varianza: 4512.46 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #81
#21: Precision_prueba(1/10/100): 3.29 11.58 27.36, RRM: 6.20, media: 783.00, varianza: 4400.89 Sum
#14: Precision_prueba(1/10/100): 2.46 11.32 31.05, RRM: 5.47, media: 525.00, varianza: 4103.76 Sum
#10: Precision_prueba(1/10/100): 2.70 11.42 28.75, RRM: 5.69, media: 602.00, varianza: 4139.64 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #81
#8:  Precision_prueba(1/10/100): 2.38 10.27 30.41, RRM: 5.15, media: 525.00, varianza: 3961.04 Sum
#4:  Precision_prueba(1/10/100): 2.68 9.96 25.16, RRM: 5.22, media: 779.00, varianza: 4636.24 Sum
#3:  Precision_prueba(1/10/100): 2.77 10.92 28.03, RRM: 5.59, media: 654.00, varianza: 3801.24 Sum

#Prueba 82: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 60.75%, 13
#9:  Precision_prueba(1/10/100): 19.00 41.40 66.60, RRM: 26.59, media: 21.00, varianza: 1585.33 Sum
#6:  Precision_prueba(1/10/100): 21.00 42.00 69.20, RRM: 27.88, media: 19.50, varianza: 1365.44 Sum
#4:  Precision_prueba(1/10/100): 21.20 42.40 67.60, RRM: 28.24, media: 18.50, varianza: 1722.41 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #82
#21: Precision_prueba(1/10/100): 19.60 41.60 65.60, RRM: 27.06, media: 23.50, varianza: 1776.35 Sum
#14: Precision_prueba(1/10/100): 21.20 44.40 70.00, RRM: 29.05, media: 19.50, varianza: 1713.74 Sum
#10: Precision_prueba(1/10/100): 20.00 41.00 69.40, RRM: 27.13, media: 24.00, varianza: 1496.11 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #82
#8:  Precision_prueba(1/10/100): 22.00 40.40 65.80, RRM: 27.83, media: 24.50, varianza: 1594.08 Sum
#4:  Precision_prueba(1/10/100): 20.20 42.60 68.20, RRM: 27.62, media: 19.00, varianza: 1633.39 Sum
#3:  Precision_prueba(1/10/100): 20.80 42.60 66.80, RRM: 28.18, media: 19.00, varianza: 1543.14 Sum

#Prueba 83: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 62.71%, 14
#11: Precision_prueba(1/10/100): 20.80 40.20 67.40, RRM: 27.01, media: 23.50, varianza: 2358.66 Sum
#6:  Precision_prueba(1/10/100): 21.00 41.40 66.60, RRM: 27.68, media: 22.00, varianza: 2046.58 Sum
#4:  Precision_prueba(1/10/100): 20.40 39.20 67.80, RRM: 26.88, media: 27.00, varianza: 1986.90 Sum

#Prueba 84: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 63.32%, 15
#11: Precision_prueba(1/10/100): 18.80 40.40 65.40, RRM: 25.75, media: 28.00, varianza: 1549.07 Sum
#6:  Precision_prueba(1/10/100): 20.20 40.60 66.40, RRM: 26.91, media: 24.00, varianza: 1647.62 Sum
#4:  Precision_prueba(1/10/100): 19.00 40.40 67.00, RRM: 25.42, media: 28.00, varianza: 1525.19 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #84
#21: Precision_prueba(1/10/100): 19.40 42.20 67.80, RRM: 26.68, media: 22.00, varianza: 1505.22 Sum
#14: Precision_prueba(1/10/100): 18.80 40.00 67.00, RRM: 25.70, media: 27.00, varianza: 1523.54 Sum
#10: Precision_prueba(1/10/100): 20.20 41.00 67.60, RRM: 26.50, media: 27.00, varianza: 1670.83 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #84
#8:  Precision_prueba(1/10/100): 19.60 38.20 69.40, RRM: 26.00, media: 24.00, varianza: 1615.20 Sum
#4:  Precision_prueba(1/10/100): 18.40 38.00 66.00, RRM: 24.53, media: 25.00, varianza: 1727.50 Sum
#3:  Precision_prueba(1/10/100): 21.00 39.60 69.00, RRM: 27.06, media: 22.50, varianza: 1528.50 Sum

#Prueba 85: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 63.53%, 16
#11: Precision_prueba(1/10/100): 24.40 43.60 68.80, RRM: 30.84, media: 19.50, varianza: 1711.00 Sum
#6:  Precision_prueba(1/10/100): 24.40 45.20 71.80, RRM: 31.19, media: 17.50, varianza: 1789.28 Sum
#4:  Precision_prueba(1/10/100): 25.80 44.80 69.40, RRM: 31.77, media: 17.50, varianza: 1735.16 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #85
#21: Precision_prueba(1/10/100): 25.20 44.60 70.60, RRM: 31.80, media: 18.00, varianza: 1774.01 Sum
#14: Precision_prueba(1/10/100): 23.40 44.20 71.00, RRM: 30.40, media: 17.50, varianza: 1667.58 Sum
#10: Precision_prueba(1/10/100): 25.00 46.60 69.60, RRM: 32.12, media: 14.50, varianza: 1671.12 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #85
#14: Precision_prueba(1/10/100): 24.40 44.60 70.00, RRM: 31.01, media: 16.00, varianza: 1710.10 Sum
#8:  Precision_prueba(1/10/100): 25.00 44.80 68.60, RRM: 31.49, media: 17.00, varianza: 2039.83 Sum
#3:  Precision_prueba(1/10/100): 25.00 48.60 71.00, RRM: 32.23, media: 13.00, varianza: 1713.47 Sum

#Prueba 86: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 63.98%, 17
#11: Precision_prueba(1/10/100): 22.20 42.00 69.00, RRM: 28.70, media: 23.00, varianza: 2172.76 Sum
#6:  Precision_prueba(1/10/100): 20.80 41.80 69.40, RRM: 27.73, media: 20.00, varianza: 1775.60 Sum
#4:  Precision_prueba(1/10/100): 21.60 42.60 67.80, RRM: 28.31, media: 20.00, varianza: 1603.96 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #86
#21: Precision_prueba(1/10/100): 22.40 42.40 70.00, RRM: 28.79, media: 21.00, varianza: 1786.04 Sum
#13: Precision_prueba(1/10/100): 20.00 40.60 66.60, RRM: 27.03, media: 24.00, varianza: 1706.71 Sum
#10: Precision_prueba(1/10/100): 19.40 41.00 68.60, RRM: 26.58, media: 25.00, varianza: 1500.46 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: osmarloeza88suaste #86
#9:  Precision_prueba(1/10/100): 22.40 39.80 68.00, RRM: 27.89, media: 19.50, varianza: 1743.90 Sum
#8:  Precision_prueba(1/10/100): 22.00 43.60 70.00, RRM: 28.91, media: 20.00, varianza: 1912.56 Sum
#3:  Precision_prueba(1/10/100): 22.60 45.40 70.00, RRM: 29.61, media: 17.00, varianza: 1655.82 Sum

#Prueba 87: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.48%, 18
#11: Precision_prueba(1/10/100): 22.20 42.40 69.20, RRM: 29.15, media: 19.50, varianza: 1719.71 Sum
#6:  Precision_prueba(1/10/100): 21.20 42.00 70.20, RRM: 28.43, media: 20.00, varianza: 1518.76 Sum
#4:  Precision_prueba(1/10/100): 20.60 40.00 73.20, RRM: 27.17, media: 19.00, varianza: 1406.91 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: osmarsanchez2002loeza #87
#21: Precision_prueba(1/10/100): 22.20 45.40 70.40, RRM: 29.37, media: 17.00, varianza: 1664.34 Sum
#13: Precision_prueba(1/10/100): 23.00 44.80 70.80, RRM: 30.83, media: 14.00, varianza: 1505.64 Sum
#10: Precision_prueba(1/10/100): 22.40 42.40 71.60, RRM: 29.22, media: 20.00, varianza: 1943.53 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: gonzalezaldar4o #87
#19: Precision_prueba(1/10/100): 22.60 42.40 69.80, RRM: 29.37, media: 19.50, varianza: 1610.27 Sum
#8:  Precision_prueba(1/10/100): 22.40 43.40 70.40, RRM: 28.65, media: 19.50, varianza: 1455.01 Sum

#Prueba 88: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.88%, 19
#11: Precision_prueba(1/10/100): 19.00 38.60 71.80, RRM: 24.94, media: 21.00, varianza: 1650.50 Sum
#6:  Precision_prueba(1/10/100): 18.40 41.80 69.20, RRM: 25.43, media: 21.00, varianza: 1526.03 Sum
#4:  Precision_prueba(1/10/100): 19.00 37.80 67.40, RRM: 25.62, media: 24.00, varianza: 1502.85 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: chpalomoo #88
#21: Precision_prueba(1/10/100): 19.20 39.60 68.40, RRM: 26.01, media: 23.00, varianza: 1506.55 Sum
#13: Precision_prueba(1/10/100): 17.40 39.20 69.40, RRM: 25.45, media: 20.00, varianza: 1768.49 Sum
#10: Precision_prueba(1/10/100): 18.00 39.20 70.80, RRM: 24.96, media: 22.50, varianza: 1561.19 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: gonzalezaldar4o #88
#19: Precision_prueba(1/10/100): 18.00 40.80 68.00, RRM: 25.66, media: 21.50, varianza: 1452.21 Sum
#8:  Precision_prueba(1/10/100): 18.00 37.60 68.00, RRM: 24.65, media: 26.00, varianza: 1609.64 Sum
#3:  Precision_prueba(1/10/100): 20.40 40.40 70.00, RRM: 26.64, media: 23.00, varianza: 1559.54 Sum

#Prueba 89: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.17%, min_count=20, grupos=13
#11: Precision_prueba(1/10/100): 20.80 40.20 68.80, RRM: 27.32, media: 25.00, varianza: 1371.83 Sum
#6:  Precision_prueba(1/10/100): 19.40 40.00 70.40, RRM: 26.05, media: 23.00, varianza: 1776.92 Sum
#4:  Precision_prueba(1/10/100): 19.60 39.60 69.00, RRM: 26.76, media: 22.00, varianza: 1274.75 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: chpalomoo #89
#21: Precision_prueba(1/10/100): 21.20 41.40 71.00, RRM: 28.00, media: 25.00, varianza: 1322.34 Sum
#13: Precision_prueba(1/10/100): 20.20 40.80 70.40, RRM: 27.06, media: 24.00, varianza: 1332.93 Sum
#11: Precision_prueba(1/10/100): 18.80 41.20 69.60, RRM: 26.19, media: 21.00, varianza: 1553.85 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: gonzalezaldar4o #89
#19: Precision_prueba(1/10/100): 19.60 39.40 69.40, RRM: 26.36, media: 23.50, varianza: 1427.46 Sum
#9:  Precision_prueba(1/10/100): 22.00 40.80 69.80, RRM: 28.06, media: 27.00, varianza: 1545.75 Sum
#3:  Precision_prueba(1/10/100): 21.40 43.60 69.40, RRM: 28.68, media: 15.00, varianza: 1665.62 Sum

#Prueba 90: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.51%, min_count=21, grupos=26
#11: Precision_prueba(1/10/100): 20.60 41.40 69.40, RRM: 26.88, media: 23.50, varianza: 1549.17 Sum
#6:  Precision_prueba(1/10/100): 18.80 42.40 70.80, RRM: 25.87, media: 18.00, varianza: 1333.43 Sum
#4:  Precision_prueba(1/10/100): 20.20 43.00 70.40, RRM: 27.37, media: 18.50, varianza: 1523.21 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: chpalomoo #90
#30: Precision_prueba(1/10/100): 19.80 43.80 70.00, RRM: 27.15, media: 20.00, varianza: 1664.47 Sum
#21: Precision_prueba(1/10/100): 19.00 42.40 69.80, RRM: 26.45, media: 19.00, varianza: 1663.69 Sum
#13: Precision_prueba(1/10/100): 20.00 43.80 70.00, RRM: 27.50, media: 18.50, varianza: 1639.77 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: gonzalezaldar4o #90
#19: Precision_prueba(1/10/100): 22.00 41.00 71.20, RRM: 28.33, media: 20.50, varianza: 1844.35 Sum
#9:  Precision_prueba(1/10/100): 18.80 41.40 68.80, RRM: 26.01, media: 19.00, varianza: 1406.06 Sum
#3:  Precision_prueba(1/10/100): 19.80 44.00 70.00, RRM: 27.05, media: 19.00, varianza: 1590.61 Sum

#Prueba 91: 0.001, 0.73, 500DD, 0.2Dropout, patience=1, FastText, 64.84%, min_count=22, grupos=39
#11: Precision_prueba(1/10/100): 18.20 41.20 69.80, RRM: 26.26, media: 19.00, varianza: 1251.53 Sum
#4:  Precision_prueba(1/10/100): 19.00 42.40 69.40, RRM: 26.55, media: 23.00, varianza: 1190.82 Sum
#2:  Precision_prueba(1/10/100): 20.40 40.40 69.60, RRM: 27.16, media: 20.50, varianza: 1249.64 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Dropout, patience=2 FastText: chpalomoo #91
#30: Precision_prueba(1/10/100): 19.80 40.00 67.80, RRM: 27.16, media: 25.50, varianza: 1247.22 Sum
#21: Precision_prueba(1/10/100): 20.00 40.40 73.00, RRM: 26.91, media: 20.00, varianza: 1001.71 Sum
#13: Precision_prueba(1/10/100): 19.60 40.80 70.60, RRM: 27.24, media: 21.00, varianza: 1235.25 Sum

#0.001, 0.73, 500DD, 0.2Dropout, patience=2, FastText: gonzalezaldar4o #91
#19: Precision_prueba(1/10/100): 18.40 42.40 70.40, RRM: 26.18, media: 18.00, varianza: 1472.40 Sum
#9:  Precision_prueba(1/10/100): 19.80 40.00 67.80, RRM: 27.16, media: 25.50, varianza: 1247.22 Sum
#3:  Precision_prueba(1/10/100): 19.80 42.00 68.80, RRM: 27.14, media: 20.50, varianza: 1030.50 Sum

#Prueba 92: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 65.27%, min_count=23, grupos=56, 6%
#11: Precision_prueba(1/10/100): 16.20 38.40 66.00, RRM: 23.18, media: 23.00, varianza: 1519.62 Sum
#4:  Precision_prueba(1/10/100): 16.80 38.60 67.40, RRM: 23.93, media: 22.50, varianza: 1547.39 Sum
#2:  Precision_prueba(1/10/100): 17.00 39.80 70.00, RRM: 24.89, media: 21.50, varianza: 1423.32 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: chpalomoo #92
#30: Precision_prueba(1/10/100): 16.80 40.00 68.60, RRM: 24.40, media: 23.00, varianza: 1342.40 Sum
#20: Precision_prueba(1/10/100): 17.40 35.20 69.20, RRM: 23.69, media: 25.50, varianza: 1615.72 Sum
#13: Precision_prueba(1/10/100): 15.20 38.80 67.60, RRM: 23.18, media: 24.00, varianza: 1589.81 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: gonzalezaldar4o #92
#19: Precision_prueba(1/10/100): 17.00 41.20 68.40, RRM: 24.52, media: 22.00, varianza: 1564.72 Sum
#9:  Precision_prueba(1/10/100): 16.60 39.80 69.80, RRM: 24.28, media: 22.50, varianza: 1505.56 Sum
#3:  Precision_prueba(1/10/100): 16.40 37.60 69.40, RRM: 23.45, media: 28.00, varianza: 1483.60 Sum

#Prueba 93: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 65.27%, min_count=24, grupos=70, 6%
#10: Precision_prueba(1/10/100): 17.20 38.80 67.60, RRM: 24.67, media: 25.00, varianza: 1460.84 Sum
#4:  Precision_prueba(1/10/100): 15.40 40.20 68.80, RRM: 23.66, media: 23.00, varianza: 1266.98 Sum
#2:  Precision_prueba(1/10/100): 18.00 41.00 70.60, RRM: 25.38, media: 21.00, varianza: 1325.39 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: chpalomoo #93
#30: Precision_prueba(1/10/100): 18.40 41.00 70.40, RRM: 25.31, media: 24.50, varianza: 1462.46 Sum
#20: Precision_prueba(1/10/100): 17.60 41.80 67.60, RRM: 25.43, media: 18.00, varianza: 1533.59 Sum
#13: Precision_prueba(1/10/100): 16.40 39.20 70.00, RRM: 23.91, media: 23.00, varianza: 1496.23 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: gonzalezaldar4o #93
#19: Precision_prueba(1/10/100): 17.80 40.20 70.20, RRM: 24.76, media: 21.00, varianza: 1420.78 Sum
#9:  Precision_prueba(1/10/100): 16.40 39.00 70.80, RRM: 24.52, media: 23.50, varianza: 1624.28 Sum
#3:  Precision_prueba(1/10/100): 18.20 40.00 69.20, RRM: 25.19, media: 21.00, varianza: 1306.59 Sum

#Prueba 94: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 66.58%, min_count=25, grupos=84, 6%
#10: Precision_prueba(1/10/100): 15.60 40.20 69.40, RRM: 23.72, media: 24.00, varianza: 1428.98 Sum
#4:  Precision_prueba(1/10/100): 16.40 39.20 69.80, RRM: 23.72, media: 23.00, varianza: 1313.91 Sum
#2:  Precision_prueba(1/10/100): 16.40 39.00 69.80, RRM: 24.30, media: 21.00, varianza: 1345.61 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: chpalomoo #94
#30: Precision_prueba(1/10/100): 17.20 40.00 68.80, RRM: 24.44, media: 22.50, varianza: 1492.28 Sum
#20: Precision_prueba(1/10/100): 15.60 38.60 71.00, RRM: 23.18, media: 24.00, varianza: 1406.51 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: gonzalezaldar4o #94
#19: Precision_prueba(1/10/100): 15.60 40.80 72.20, RRM: 23.95, media: 20.00, varianza: 1415.10 Sum
#9:  Precision_prueba(1/10/100): 15.20 39.20 70.00, RRM: 23.55, media: 22.50, varianza: 1509.25 Sum

#Prueba 95: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 66.35%, min_count=25, grupos=98, 3%
#10: Precision_prueba(1/10/100): 11.40 40.80 69.00, RRM: 21.14, media: 19.50, varianza: 1508.30 Sum
#4:  Precision_prueba(1/10/100): 14.20 36.60 66.40, RRM: 21.60, media: 26.00, varianza: 1314.63 Sum
#2:  Precision_prueba(1/10/100): 16.00 38.40 67.60, RRM: 22.70, media: 26.00, varianza: 1467.26 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #95
#30: Precision_prueba(1/10/100): 13.60 37.40 68.40, RRM: 21.69, media: 25.00, varianza: 1395.86 Sum
#20: Precision_prueba(1/10/100): 15.20 38.00 66.60, RRM: 22.30, media: 26.00, varianza: 1639.06 Sum
#14: Precision_prueba(1/10/100): 14.00 36.40 68.60, RRM: 20.81, media: 29.00, varianza: 1576.72 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #95
#19: Precision_prueba(1/10/100): 14.00 38.80 67.40, RRM: 22.25, media: 24.50, varianza: 1376.62 Sum
#9:  Precision_prueba(1/10/100): 14.20 39.20 70.20, RRM: 21.94, media: 24.00, varianza: 1458.31 Sum
#3:  Precision_prueba(1/10/100): 13.40 40.40 67.40, RRM: 22.21, media: 21.00, varianza: 1290.01 Sum

#Prueba 96: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 64.70%, min_count=25, grupos=112, 3%
#10: Precision_prueba(1/10/100): 17.80 38.00 73.40, RRM: 24.64, media: 20.00, varianza: 1357.23 Sum
#4:  Precision_prueba(1/10/100): 15.60 42.80 71.60, RRM: 24.86, media: 18.00, varianza: 1212.64 Sum
#2:  Precision_prueba(1/10/100): 15.60 42.80 71.60, RRM: 24.86, media: 18.00, varianza: 1212.64 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #96
#30: Precision_prueba(1/10/100): 16.20 41.00 72.80, RRM: 24.87, media: 18.00, varianza: 1049.16 Sum
#20: Precision_prueba(1/10/100): 15.80 41.20 72.20, RRM: 24.14, media: 19.00, varianza: 1126.85 Sum
#15: Precision_prueba(1/10/100): 16.80 42.40 73.20, RRM: 25.72, media: 18.50, varianza: 1526.00 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #96
#19: Precision_prueba(1/10/100): 18.00 41.40 69.80, RRM: 25.74, media: 17.50, varianza: 1359.90 Sum
#8:  Precision_prueba(1/10/100): 16.80 41.40 70.60, RRM: 24.80, media: 19.00, varianza: 1452.11 Sum
#3:  Precision_prueba(1/10/100): 18.00 40.60 71.00, RRM: 25.27, media: 19.00, varianza: 1385.02 Sum

#Prueba 97: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 62.91%, min_count=25, grupos=126, 3%
#9:  Precision_prueba(1/10/100): 14.80 40.20 70.60, RRM: 23.22, media: 20.50, varianza: 1288.43 Sum
#4:  Precision_prueba(1/10/100): 15.20 40.20 70.20, RRM: 23.58, media: 23.50, varianza: 1162.05 Sum
#2:  Precision_prueba(1/10/100): 16.00 38.20 68.60, RRM: 24.13, media: 23.00, varianza: 1412.39 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #97
#30: Precision_prueba(1/10/100): 16.00 38.40 72.20, RRM: 23.58, media: 22.50, varianza: 1161.34 Sum
#20: Precision_prueba(1/10/100): 15.80 41.40 69.80, RRM: 24.18, media: 19.00, varianza: 1390.44 Sum
#15: Precision_prueba(1/10/100): 14.20 40.60 70.00, RRM: 23.08, media: 22.50, varianza: 1330.95 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #97
#19: Precision_prueba(1/10/100): 16.00 39.00 70.80, RRM: 23.82, media: 24.00, varianza: 1123.27 Sum
#10: Precision_prueba(1/10/100): 14.60 38.20 70.20, RRM: 22.44, media: 27.00, varianza: 1260.54 Sum
#3:  Precision_prueba(1/10/100): 15.40 40.00 69.00, RRM: 23.63, media: 19.00, varianza: 1302.55 Sum

#Prueba 98: 0.001, 0.73, 500DD, 0.2Drop, patience=1, FastText, 67.93%, min_count=29, grupos=140, 1%
#11: Precision_prueba(1/10/100): 9.60 29.80 61.00, RRM: 15.88, media: 52.00, varianza: 1463.67 Sum
#4:  Precision_prueba(1/10/100): 10.00 29.00 57.60, RRM: 16.47, media: 56.00, varianza: 1982.64 Sum
#2:  Precision_prueba(1/10/100): 11.20 28.60 54.80, RRM: 17.70, media: 67.50, varianza: 1978.76 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #98
#30: Precision_prueba(1/10/100): 15.00 41.80 71.40, RRM: 23.48, media: 17.50, varianza: 1246.45 Sum
#20: Precision_prueba(1/10/100): 14.00 36.80 68.80, RRM: 22.12, media: 21.00, varianza: 1133.36 Sum
#15: Precision_prueba(1/10/100): 14.60 38.20 67.60, RRM: 22.72, media: 25.50, varianza: 1175.69 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #98
#19: Precision_prueba(1/10/100): 15.00 39.20 70.80, RRM: 22.83, media: 23.00, varianza: 1420.71 Sum
#18: Precision_prueba(1/10/100): 15.00 40.20 68.60, RRM: 23.39, media: 25.00, varianza: 1246.88 Sum
#3:  Precision_prueba(1/10/100): 16.40 40.00 68.20, RRM: 24.17, media: 20.00, varianza: 1399.01 Sum

#Prueba 99: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 67.16%, min_count=27, grupos=154, 1%
#14: Precision_prueba(1/10/100): 10.40 27.40 55.00, RRM: 16.12, media: 70.00, varianza: 1726.22 Sum
#4:  Precision_prueba(1/10/100): 9.40 27.20 55.80, RRM: 15.78, media: 60.00, varianza: 1762.42 Sum
#2:  Precision_prueba(1/10/100): 10.00 27.60 52.80, RRM: 15.70, media: 82.00, varianza: 2123.89 Sum

#Prueba 100: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 67.36%, min_count=25, grupos=154, 0%
#14: Precision_prueba(1/10/100): 11.20 29.00 56.00, RRM: 17.64, media: 63.50, varianza: 1856.50 Sum
#4:  Precision_prueba(1/10/100): 10.20 30.20 56.40, RRM: 16.71, media: 65.50, varianza: 1579.46 Sum
#2:  Precision_prueba(1/10/100): 11.40 29.60 57.20, RRM: 17.35, media: 61.00, varianza: 1869.41 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #100
#30: Precision_prueba(1/10/100): 10.80 28.80 55.60, RRM: 17.13, media: 66.00, varianza: 1626.03 Sum
#20: Precision_prueba(1/10/100): 10.00 28.20 56.00, RRM: 16.31, media: 61.50, varianza: 1874.77 Sum
#15: Precision_prueba(1/10/100): 10.00 28.20 56.00, RRM: 16.31, media: 61.50, varianza: 1874.77 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #100
#19: Precision_prueba(1/10/100): 10.40 28.60 59.60, RRM: 16.38, media: 54.00, varianza: 1449.89 Sum
#18: Precision_prueba(1/10/100): 11.20 27.60 57.00, RRM: 16.96, media: 61.00, varianza: 1812.07 Sum
#3:  Precision_prueba(1/10/100): 10.60 28.60 57.00, RRM: 16.85, media: 65.50, varianza: 1500.72 Sum

#Prueba 101: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 66.46%, min_count=23, grupos=168, 0%
#14: Precision_prueba(1/10/100): 10.20 32.60 62.20, RRM: 17.69, media: 42.00, varianza: 1715.93 Sum
#4:  Precision_prueba(1/10/100): 10.60 32.20 64.00, RRM: 18.75, media: 39.00, varianza: 1690.38 Sum
#2:  Precision_prueba(1/10/100): 10.00 32.40 57.20, RRM: 17.54, media: 50.00, varianza: 1775.45 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #101
#30: Precision_prueba(1/10/100): 12.20 31.40 61.60, RRM: 18.96, media: 43.00, varianza: 1776.03 Sum
#20: Precision_prueba(1/10/100): 10.40 30.40 58.60, RRM: 17.54, media: 47.00, varianza: 1962.96 Sum
#15: Precision_prueba(1/10/100): 12.00 31.60 61.00, RRM: 18.21, media: 47.50, varianza: 1751.54 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #101
#18: Precision_prueba(1/10/100): 11.40 30.80 60.80, RRM: 18.45, media: 40.50, varianza: 1582.16 Sum
#14: Precision_prueba(1/10/100): 10.60 34.40 61.80, RRM: 18.15, media: 39.00, varianza: 1677.69 Sum
#3:  Precision_prueba(1/10/100): 9.20 33.60 62.80, RRM: 17.41, media: 42.50, varianza: 1547.88 Sum

#Prueba 102: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 66.84%, min_count=24, grupos=182, 0%
#14: Precision_prueba(1/10/100): 10.60 27.00 58.80, RRM: 16.25, media: 53.00, varianza: 1542.75 Sum
#4:  Precision_prueba(1/10/100): 10.20 29.40 61.60, RRM: 16.84, media: 45.00, varianza: 1466.94 Sum
#2:  Precision_prueba(1/10/100): 11.60 31.60 57.40, RRM: 18.44, media: 58.00, varianza: 1414.60 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #102
#30: Precision_prueba(1/10/100): 11.00 30.80 62.80, RRM: 17.27, media: 42.50, varianza: 1367.24 Sum
#25: Precision_prueba(1/10/100): 10.20 27.80 58.40, RRM: 16.62, media: 51.00, varianza: 1388.05 Sum
#15: Precision_prueba(1/10/100): 10.60 29.40 61.60, RRM: 16.71, media: 50.00, varianza: 1352.60 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: salvarogs #102
#18: Precision_prueba(1/10/100): 10.00 30.40 60.40, RRM: 17.07, media: 52.00, varianza: 1358.87 Sum
#14: Precision_prueba(1/10/100): 10.60 30.80 61.40, RRM: 17.52, media: 51.50, varianza: 1389.99 Sum
#3:  Precision_prueba(1/10/100): 10.20 28.40 59.00, RRM: 16.96, media: 53.00, varianza: 1351.35 Sum

#Prueba 103: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 65.98%, min_count=23, grupos=196, 0%
#14: Precision_prueba(1/10/100): 11.00 29.40 57.40, RRM: 17.35, media: 60.50, varianza: 1663.10 Sum
#4:  Precision_prueba(1/10/100): 11.60 27.80 55.80, RRM: 16.86, media: 70.00, varianza: 1656.79 Sum
#2:  Precision_prueba(1/10/100): 11.20 26.00 55.00, RRM: 16.47, media: 67.00, varianza: 1734.36 Sum

#Prueba 104: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 65.35%, min_count=24, grupos=196, 0%
#14: Precision_prueba(1/10/100): 12.80 38.60 67.20, RRM: 20.59, media: 25.00, varianza: 1418.78 Sum
#4:  Precision_prueba(1/10/100): 13.20 35.60 67.60, RRM: 20.73, media: 27.00, varianza: 1374.52 Sum
#2:  Precision_prueba(1/10/100): 11.80 35.40 67.00, RRM: 19.48, media: 29.00, varianza: 1243.89 Sum

#0.0008 -> 0.001, 0.73, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #104
#30: Precision_prueba(1/10/100): 13.40 36.60 65.40, RRM: 20.39, media: 29.50, varianza: 1397.61 Sum
#15: Precision_prueba(1/10/100): 13.40 32.20 63.20, RRM: 20.09, media: 30.00, varianza: 1359.07 Sum
#5:  Precision_prueba(1/10/100): 13.60 35.60 67.20, RRM: 20.95, media: 25.50, varianza: 1270.00 Sum

#0.001, 0.73, 500DD, 0.2Drop, patience=2, FastText: osmarloeza88suaste #104
#18: Precision_prueba(1/10/100): 12.80 36.60 65.20, RRM: 20.35, media: 27.50, varianza: 1317.64 Sum
#14: Precision_prueba(1/10/100): 13.20 36.00 67.00, RRM: 20.37, media: 26.00, varianza: 1314.12 Sum
#4:  Precision_prueba(1/10/100): 13.00 35.60 63.20, RRM: 19.97, media: 31.50, varianza: 1542.55 Sum

#Prueba 105: 0.001, 0.7, 500DD, 0.2Drop, patience=3, FastText, 67.37%, min_count=25, grupos=210, 0%
#14: Precision_prueba(1/10/100): 10.60 33.40 68.80, RRM: 18.38, media: 28.00, varianza: 1059.34 Sum
#4:  Precision_prueba(1/10/100): 11.60 36.00 62.80, RRM: 18.88, media: 32.00, varianza: 1190.20 Sum
#3:  Precision_prueba(1/10/100): 12.20 35.20 65.00, RRM: 19.91, media: 32.00, varianza: 1072.08 Sum

#0.0007 -> 0.001, 0.75, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #105
#30: Precision_prueba(1/10/100): 9.60 31.40 66.00, RRM: 17.50, media: 36.50, varianza: 1134.89 Sum
#15: Precision_prueba(1/10/100): 10.00 34.80 66.40, RRM: 18.43, media: 27.50, varianza: 1016.58 Sum
#5:  Precision_prueba(1/10/100): 9.80 38.00 71.40, RRM: 18.67, media: 24.50, varianza: 997.26 Sum

#0.001, 0.75, 500DD, 0.2Drop, patience=2, FastText: osmarloeza88suaste #105
#18: Precision_prueba(1/10/100): 11.60 36.40 69.20, RRM: 19.74, media: 26.00, varianza: 1180.59 Sum
#14: Precision_prueba(1/10/100): 10.20 33.60 70.40, RRM: 18.31, media: 24.50, varianza: 984.46 Sum
#8:  Precision_prueba(1/10/100): 9.80 35.40 68.60, RRM: 17.61, media: 25.50, varianza: 943.68 Sum

#Prueba 106: 0.001, 0.7, 500DD, 0.3Drop, patience=3, FastText, 65.59%, min_count=25, grupos=240, 0%
#14: Precision_prueba(1/10/100): 12.00 38.40 70.80, RRM: 20.84, media: 20.00, varianza: 804.40 Sum
#4:  Precision_prueba(1/10/100): 13.20 37.20 67.60, RRM: 21.38, media: 24.00, varianza: 1198.11 Sum
#3:  Precision_prueba(1/10/100): 11.00 36.40 67.80, RRM: 19.48, media: 24.00, varianza: 1034.49 Sum

#Prueba 107: 0.001, 0.7, 500DD, 0.3Drop, patience=3, FastText, 65.84%, min_count=26, grupos=255, 0%
#14: Precision_prueba(1/10/100): 13.60 37.40 71.00, RRM: 21.50, media: 24.50, varianza: 857.34 Sum
#4:  Precision_prueba(1/10/100): 12.00 39.60 72.20, RRM: 21.37, media: 22.00, varianza: 847.33 Sum
#3:  Precision_prueba(1/10/100): 13.60 38.20 73.60, RRM: 22.64, media: 20.00, varianza: 999.09 Sum

#0.00073 -> 0.001, 0.75, 500DD, 0.2Drop, patience=2 FastText: jatziryocao #107
#30: Precision_prueba(1/10/100): 12.80 38.00 68.60, RRM: 20.39, media: 23.50, varianza: 1056.54 Sum
#15: Precision_prueba(1/10/100): 13.00 37.40 74.00, RRM: 21.56, media: 20.50, varianza: 741.08 Sum
#5:  Precision_prueba(1/10/100): 13.60 36.40 69.00, RRM: 21.34, media: 27.00, varianza: 1126.97 Sum

#0.001, 0.75, 500DD, 0.2Drop, patience=2, FastText: osmarloeza88suaste #107
#18: Precision_prueba(1/10/100): 12.00 37.80 70.00, RRM: 20.46, media: 24.00, varianza: 1067.81 Sum
#14: Precision_prueba(1/10/100): 13.80 36.60 72.20, RRM: 21.92, media: 23.50, varianza: 909.74 Sum
#2:  Precision_prueba(1/10/100): 14.20 37.80 71.40, RRM: 22.10, media: 27.50, varianza: 1001.80 Sum

#Prueba 108: 0.001, 0.7, 500DD, 0.3Drop, patience=3, FastText, 66.32%, min_count=27, grupos=270, 0%
#14: Precision_prueba(1/10/100): 14.80 38.40 73.20, RRM: 23.22, media: 19.00, varianza: 961.99 Sum
#4:  Precision_prueba(1/10/100): 13.80 38.60 74.60, RRM: 21.89, media: 22.00, varianza: 961.49 Sum
#3:  Precision_prueba(1/10/100): 13.40 40.40 73.40, RRM: 21.97, media: 19.50, varianza: 824.92 Sum

#0.00076 -> 0.001, 0.75, 500DD, 0.3Drop, patience=2 FastText: jatziryocao #108
#29: Precision_prueba(1/10/100): 14.40 38.40 73.60, RRM: 22.23, media: 25.00, varianza: 811.78 Sum
#15: Precision_prueba(1/10/100): 14.00 38.00 70.80, RRM: 22.12, media: 23.00, varianza: 982.63 Sum
#5:  Precision_prueba(1/10/100): 14.20 41.00 76.80, RRM: 23.14, media: 19.00, varianza: 772.02 Sum

#0.001, 0.75, 500DD, 0.3Drop, patience=2, FastText: osmarloeza88suaste #108
#18: Precision_prueba(1/10/100): 14.80 39.60 72.00, RRM: 22.85, media: 21.00, varianza: 883.88 Sum
#14: Precision_prueba(1/10/100): 14.80 39.20 70.40, RRM: 22.29, media: 24.00, varianza: 895.27 Sum
#2:  Precision_prueba(1/10/100): 15.80 36.20 72.20, RRM: 22.88, media: 22.00, varianza: 935.22 Sum

#Prueba 109: 0.001, 0.7, 500DD, 0.3Drop, patience=3, FastText, 66.81%, min_count=28, grupos=285, 0%
#14: Precision_prueba(1/10/100): 12.20 36.80 74.40, RRM: 20.93, media: 26.50, varianza: 669.50 Sum
#9:  Precision_prueba(1/10/100): 14.40 40.20 72.80, RRM: 22.45, media: 22.00, varianza: 702.55 Sum
#3:  Precision_prueba(1/10/100): 12.60 37.20 75.00, RRM: 20.59, media: 23.50, varianza: 763.29 Sum

#0.00076 -> 0.001, 0.75, 500DD, 0.3Drop, patience=2 FastText: jatziryocao #109
#29: Precision_prueba(1/10/100): 12.80 38.80 72.20, RRM: 21.12, media: 23.00, varianza: 743.16 Sum
#15: Precision_prueba(1/10/100): 12.20 40.20 74.20, RRM: 21.18, media: 20.50, varianza: 732.27 Sum
#5:  Precision_prueba(1/10/100): 12.60 40.80 76.60, RRM: 21.81, media: 19.00, varianza: 543.83 Sum

#0.001, 0.75, 500DD, 0.3Drop, patience=2, FastText: osmarloeza88suaste #109
#18: Precision_prueba(1/10/100): 13.20 38.00 72.20, RRM: 21.12, media: 21.50, varianza: 533.38 Sum
#14: Precision_prueba(1/10/100): 13.80 39.00 74.40, RRM: 22.30, media: 22.00, varianza: 720.18 Sum
#2:  Precision_prueba(1/10/100): 12.00 36.40 70.00, RRM: 19.89, media: 22.50, varianza: 670.27 Sum

#Prueba 110: 0.001, 0.7, 500DD, 0.3Drop, pat=3, FT, 69.11%, min_count=27, grupos=300, 0%, 0.00001
#14: Precision_prueba(1/10/100): 13.40 41.40 74.80, RRM: 22.62, media: 18.00, varianza: 781.73 Sum
#9:  Precision_prueba(1/10/100): 15.00 43.20 76.00, RRM: 23.43, media: 15.00, varianza: 584.53 Sum
#3:  Precision_prueba(1/10/100): 15.00 41.40 71.00, RRM: 23.05, media: 22.00, varianza: 918.86 Sum

#0.00076 -> 0.001, 0.75, 500DD, 0.3Drop, pat=2 FT 0.000001: jatziryocao #110
#29: Precision_prueba(1/10/100): 13.80 39.80 73.80, RRM: 22.86, media: 19.50, varianza: 862.12 Sum
#15: Precision_prueba(1/10/100): 14.80 40.20 73.20, RRM: 22.99, media: 21.00, varianza: 704.20 Sum
#5:  Precision_prueba(1/10/100): 14.60 40.60 76.20, RRM: 22.88, media: 18.00, varianza: 710.53 Sum

#0.001, 0.75, 500DD, 0.3Drop, pat=2, FT 0.000001: osmarloeza88suaste #110
#18: Precision_prueba(1/10/100): 15.40 40.20 75.80, RRM: 23.64, media: 23.00, varianza: 632.62 Sum
#14: Precision_prueba(1/10/100): 14.00 41.40 75.60, RRM: 22.80, media: 18.00, varianza: 713.84 Sum
#2:  Precision_prueba(1/10/100): 15.00 42.20 74.80, RRM: 23.50, media: 16.00, varianza: 713.61 Sum

#Prueba 111: 0.001, 0.7, 500DD, 0.3Drop, pat=3, FT, 69.10%, min_count=27, grupos=300, 0%, 0.00001
#14: Precision_prueba(1/10/100): 12.00 39.80 73.80, RRM: 21.50, media: 21.00, varianza: 832.26 Sum
#9:  Precision_prueba: 14.40 41.80 79.00 96.00, RRM: 23.34, media: 18.00, varianza: 840.18 Sum
#3:  Precision_prueba: 12.80 41.00 71.00 96.00, RRM: 21.69, media: 20.00, varianza: 923.12 Su

#Prueba 112: 0.001, 0.71, 500D, 0.4Drop0.03, pat=3, 69.44%, min_count=28, grupos=300, 0%, 0.0001
#15: Precision_prueba(1/10/100/1000): 15.19 41.35 74.23 95.38, RRM: 23.29, media: 18.50, varianza: 1085.48 Sum
#9:  Precision_prueba(1/10/100/1000): 12.50 42.50 75.96 95.38, RRM: 22.34, media: 15.00, varianza: 972.20 Sum
#3:  Precision_prueba(1/10/100/1000): 13.27 38.65 74.81 94.42, RRM: 21.76, media: 21.50, varianza: 1113.35 Sum

#Prueba 113: 0.001, 0.72, 500D, 0.5Drop0.06, pat=3, 69.42%, min_count=28, grupos=300, 0%, 0.0005
#15: Precision_prueba(1/10/100/1000): 13.77 43.77 75.85 94.91, RRM: 23.39, media: 15.00, varianza: 909.91 Sum
#9:  Precision_prueba(1/10/100/1000): 14.53 41.89 77.74 95.09, RRM: 23.48, media: 16.00, varianza: 928.09 Sum
#3:  Precision_prueba(1/10/100/1000): 14.34 43.02 78.30 95.09, RRM: 23.99, media: 14.00, varianza: 958.95 Sum

#Prueba 114: 0.001, 0.73, 500D, 0.5Drop0.10, pat=3, 70.31%, min_count=29, grupos=300, 0%, 0.001
#15: Precision_prueba(1/10/100/1000): 16.11 42.04 77.59 95.93, RRM: 25.18, media: 19.00, varianza: 756.74 Sum
#9:  Precision_prueba(1/10/100/1000): 15.00 42.22 77.96 95.93, RRM: 24.46, media: 15.50, varianza: 886.04 Sum
#3:  Precision_prueba(1/10/100/1000): 15.00 42.04 76.11 96.48, RRM: 24.39, media: 17.00, varianza: 731.57 Sum

#Prueba 115: 0.001,0.74,500D, 0.5Drop0.15, pat=2, 70.27%, min_count=28, grupos=300, 0%, 0.0005, 0.6
#15: Precision_prueba(1/10/100/1000): 14.38 42.81 75.31 95.16, RRM: 23.59, media: 16.50, varianza: 741.11 Sum
#9:  Precision_prueba(1/10/100/1000): 13.44 45.00 76.72 93.91, RRM: 23.54, media: 14.00, varianza: 900.83 Sum
#3:  Precision_prueba(1/10/100/1000): 14.53 42.81 73.91 94.53, RRM: 23.34, media: 17.00, varianza: 746.09 Sum

#Prueba 116: 0.001,0.75,500D, 0.5Drop0.21, pat=2, 70.29%, min_count=28, grupos=300, 0%, 0.0005, 0.5
#15: Precision_prueba(1/10/100/1000): 12.57 40.68 74.05 94.59, RRM: 21.57, media: 19.00, varianza: 695.44 Sum
#9:  Precision_prueba(1/10/100/1000): 11.89 40.14 75.14 94.59, RRM: 21.35, media: 20.00, varianza: 760.86 Sum
#2:  Precision_prueba(1/10/100/1000): 13.78 37.03 73.24 94.59, RRM: 21.68, media: 22.50, varianza: 846.79 Sum

#Prueba 117: 0.001,0.75,500D, 0.5Drop0.28, pat=2, 70.38%, min_count=28, grupos=120, 0%, 0.0005, 0.4
#15: Precision_prueba(1/10/100/1000): 10.12 36.19 72.14 95.00, RRM: 18.82, media: 22.00, varianza: 687.34 Sum
#9:  Precision_prueba(1/10/100/1000): 11.07 37.86 71.31 94.29, RRM: 19.59, media: 24.00, varianza: 699.22 Sum
#2:  Precision_prueba(1/10/100/1000): 9.88 35.83 70.24 93.69, RRM: 18.14, media: 26.00, varianza: 794.24 Sum

#Prueba 118: 0.001,0.75,500D,0.6Drop0.35,pat=2,70.20%,min_count=27,grupos=120,0%, 0.0005, 0.3, 0.01
#15: Precision_prueba(1/10/100/1000): 9.68 34.79 71.17 94.57, RRM: 17.73, media: 25.50, varianza: 783.59 Sum
#9:  Precision_prueba(1/10/100/1000): 9.15 34.79 72.02 94.79, RRM: 17.78, media: 26.00, varianza: 868.72 Sum
#2:  Precision_prueba(1/10/100/1000): 7.45 29.15 68.72 94.79, RRM: 14.84, media: 36.50, varianza: 652.44 Sum

#Prueba 119: 0.001,0.75,500D,0.6Drop0.36,pat=2,70.20%,min_count=27,grupos=120,0%, 0.0005, 0.3, 0.03
#15: Precision_prueba(1/10/100/1000): 8.85 32.69 68.08 94.33, RRM: 17.02, media: 28.00, varianza: 664.17 Sum
#9:  Precision_prueba(1/10/100/1000): 9.13 33.94 69.42 95.00, RRM: 17.46, media: 27.00, varianza: 740.61 Sum
#4:  Precision_prueba(1/10/100/1000): 8.56 32.98 68.56 94.04, RRM: 16.59, media: 29.00, varianza: 717.40 Sum

def limpiar_conjunto(path, titulos_finales, path2, equivalentes, igualaciones):
    no_permitidos = {'nelfinavir', 'síndrome de lacomme', 'ciron', 'saquinavir', 'complicaciones de la viruela loco', 'pralidoxima', 'vih 2', 'sulindaco', 'ritonavir', 'zona interior', 'creatinfosfoquinasa', 'metal', 'antimonio', 'órgano intracelular nacional de salud', 'necrólisis epidérmico', 'transducción de señales de sustancias peligrosas', 'sucralfato', 'supuración esquelético', 'octreotida', 'minerva', 'turpentina', 'mensaje neural', 'anexina', 'sindemia', 'proteína tau', 'loa', 'anillo estomacal', 'altura voluntaria', 'alto voluntaria', 'apatito', 'ortosis dinámico', 'clonorchis sinensis', 'dato censurado', 'prótesis autoexpansible', 'isofosfamida', 'transtorno bipolar', 'membrana germinativo', 'clasificación baltimore', 'cinesia estereotipado', 'aparato fusiforme', 'agencia mundial antidopaje', 'fosforilcolina', 'hormigueo en los dedos', 'próstesis autoexpansible', 'síndrome del asa ciego', 'nudo de cirujano', 'tensoactivo neumónico', 'enajenación mental transitorio', 'deferroxamina', 'síndrome neumático agudo grave', 'compensación de dosis génico', 'válvula connivente', 'dermatitis ocre', 'coronavirus dos del síndrome neumático agudo grave perlada del cabeza del pene', 'región celiaquía', 'banco de huesos', 'callo de ender', 'indice de katz', 'resultados de un psicoanálisis de sangre', 'tejido óseo incisivo', 'quiste hidatídico', 'vaso arterial rostral', 'disco intercalado', 'transducción de señales de substancia peligrosas', 'rastreo de contactos', 'etretinato', 'acrodermatitis enteropática', 'triantereno', 'desarrollo en capas', 'ano imperforado', 'escintilador', 'indice de rosner', 'vakog', 'penfigoide cicatricial', 'tricobezoar', 'elmex', 'metoxaleno', 'faja ortopeda', 'toser', 'pitiriasisrubra pilaris'}
    for nombre_archivo in os.listdir(path):
        if os.path.isfile(path + nombre_archivo) and nombre_archivo.endswith(".txt"):
            with open(path + nombre_archivo, 'r', encoding='utf-8') as file:
                content = file.read()
            titulos, content = limpiar_html_abreviaturas(content, nombre_archivo[:-4], equivalentes, igualaciones)
            #"""
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
            #"""
"""
ssh 148.209.67.23 -l catilen
CaTilen2024
source diccionario_inverso/bin/activate
nohup bash entrenamiento.sh > salida.log 2>&1 &
sudo chown -R catilen:catilen diccionario_inverso/ //no me acuerdo
ls -l diccionario_inverso //crear entorno
pkill -f entrenamiento.sh
kill PID

web_scrapiar:
nohup python -u web_scrapiar_dtme.py > salida.log 2>&1 &
disown -h <PID
tail -f salida.log
ps aux | grep web_scrapiar_dtme.py
kill -9 PID
"""
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
                    # if len(nombre_archivo[:-4]) > 0:
                    #     modificar_seguidores(nombre_archivo[:-4], __original, equivalentes)
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