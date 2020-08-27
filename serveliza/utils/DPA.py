
from urllib.error import HTTPError
import pandas as pd
import json

CIR_PRES_89_17_NAC_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_presidenciales_ce_1989_2017_Chile.xlsx'
CIR_PRES_89_17_EXT_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_presidenciales_ce_2017_Extranjero.xlsx'
CIR_SENA_89_17_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_senadores_ce_1989_2017.xlsx'
CIR_DIPU_89_17_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_diputados_ce_1989_2017.xlsx'
CIR_ALCA_04_16_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_alcaldes_ce_2004_2016.xlsx'
CIR_CONC_04_16_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_concejales_ce_2004_2016.xlsx'
CIR_ALCO_92_00_URL = 'https://www.servel.cl/wp-content/uploads/' \
    '2019/04/resultados_elecciones_concejales_ce_1992_al_2000.xlsx'

CIR_ALL_URLS = [
    CIR_PRES_89_17_NAC_URL,
    # CIR_PRES_89_17_EXT_URL, don't have a commune column
    CIR_SENA_89_17_URL,
    CIR_DIPU_89_17_URL,
    CIR_ALCA_04_16_URL,
    CIR_CONC_04_16_URL,
    CIR_ALCO_92_00_URL,
]

KEY_YEAR = 'Año de Elección'
KEY_REGION = 'Región'
KEY_PROVINCE = 'Nombre Provincia'
KEY_COMMUNE = 'Comuna'
KEY_CIR = 'Circunscripción Electoral'
KEY_CIR2 = 'Nombre Circunscripción Electoral'


def get_communes_circuns(url=None, verbose=False, export_json=False):
    '''
    Function to get from the Internet (servel.cl) a \
    dictionary object with comunne in key and list of \
    circunscriptions in value.

    If dont specify the url then take all urls in \
    CIR_ALL_URLS to get the data and consolidate \
    in unique result.

    If verbose is true then print the process in \
    console step by step.

    This function is used to create json fixtures \
    of communes and circuns with the export_json \
    param to true.
    '''
    def __url_to_dic(url):
        if verbose:
            print(f'''Waiting de XLS file from: {str(url)}''')
        try:
            doc = pd.read_excel(url)
        except HTTPError as e:
            print(f'''HTTP Error: {str(e.code)} -> {e.msg}''')
            print(f'''url: {url}''')
            return None
        if verbose:
            print('''xls file is downloaded''')
        if KEY_CIR2 in doc:
            key_cir = KEY_CIR2
        else:
            key_cir = KEY_CIR
        data = doc[[KEY_COMMUNE, key_cir]].drop_duplicates()
        data = data.to_dict('index').items()
        return [{item[KEY_COMMUNE]:item[key_cir]} for key, item in data]
    main_data = []
    if not url:
        if verbose:
            print('''Running in all urls availables''')
        for i, u in enumerate(CIR_ALL_URLS):
            if verbose:
                print(
                    'Getting the xls file '
                    f'{str(i+1)}/{str(len(CIR_ALL_URLS))}')
            dic = __url_to_dic(u)
            if not dic:
                if verbose:
                    print('''Not data found''')
                continue
            if verbose:
                print(f'Partial data founded {str(len(dic))} circunscriptions')
            main_data += dic
    else:
        if verbose:
            print(f'''Running in url: {str(url)}''')
        main_data += __url_to_dic(url)
    if not main_data:
        print('''Data from communes and circunscription are not availables''')
        return None
    if verbose:
        print(f'Data founded: {str(len(main_data))} circunscriptions')
    result = {}
    for item in main_data:
        for k, v in item.items():
            if k in result:
                if isinstance(v, float):
                    continue
                if v not in result[k]:
                    result[k].append(v)
            elif not isinstance(v, float):
                result[k] = [v]
    if verbose:
        print(f'Total communes: {str(len(result))}')
        print(
            'Total circunscriptions: '
            f'{sum([len(x) for x in result.values()])}')
    if export_json:
        return json.dumps(result)
    return result
