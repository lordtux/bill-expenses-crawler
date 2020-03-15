#!/usr/bin/env python3

# sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
# https://github.com/jalan/pdftotext


import pdftotext
import decimal
import re
import os
import sys
from PyPDF2 import PdfFileReader # used only to get pdf metadata

VERY_VERBOSE=False
VERBOSE=False
DETAILED_REPORT=False

TAX_DISCOUNT_REGEX_PATTERN = "^REDUC\. IVA LE.*"

DETAIL_LINE_REGEX_PATTERN = '\d\d \d\d \d\d*'
REFERENCE_LINE_REGEX_PATTERN = ".* PAGOS.*"
BLACKLISTED_LINES_REGEX_PATTERN = ".* PAGOS.*"

ITAU_CC_PARSER_AUTHOR_REGEX_PATTERN = ".*Banco Ita.* Uruguay S\.A\..*"

DOLLAR_CURRENCY_CODE = 'USD' 
LOCAL_CURRENCY_CODE = 'UYU' 

CALCULATION_TOLERANCE = 2

# ------------------------------ PARSER CONFIG ------------------------------
OTHER_EXPENSE_TYPE_TOKEN='OTHERS'

EXPENSES_TYPE_PATTERNS = {}
EXPENSES_TYPE_PATTERNS['^SUBWAY$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^EL ITALIANO$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^EL REFUGIO$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^BLE$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^CONFITERIA .*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^SUSHIAPP$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^SBARRO$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^PORTO VANILA$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^MC DONALD\'S$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^OSOBAR$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^TIQUI TACA$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^PIZZERIA .*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^MAGNUM$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^EL CLUB DE LA PAPA F.*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^LA FABRICA$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^XIMENA MIGUEZ$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^JARDIN CERVECERO.*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['.*PANADERIA.*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['.*CAFE.*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^RECOLETA$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^BAR .*'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^LOS TROVADORES$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^GALLAGHER\'S$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^SOPRANOS$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^MVD$'] = 'FOOD'
EXPENSES_TYPE_PATTERNS['^QR$'] = 'FOOD'

EXPENSES_TYPE_PATTERNS['^.* CALZADOS$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^MISTRAL$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^PHILOSOPHY$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^LEGACY$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^ONLY$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^H&M$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^ADAM TAILOR$'] = 'CLOTHING'
EXPENSES_TYPE_PATTERNS['^LOJAS RENNER$'] = 'CLOTHING'

EXPENSES_TYPE_PATTERNS['^DEVOTO (EXPRESS|SUPERMERCADO)$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^MACRO MERCADO$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^KINKO$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^DISCO N.*'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^TIENDA INGLESA$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^TATA$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^TIM ALMACENES$'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^SUPER ARIEL.*'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^SUPERMERCADO.*'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['.*L\. GROSS Y ASO.*'] = 'SUPERMARKET'
EXPENSES_TYPE_PATTERNS['^SAMUD SABORES DEL MU*'] = 'SUPERMARKET'

EXPENSES_TYPE_PATTERNS['^ANCAP .*'] = 'FUEL'
EXPENSES_TYPE_PATTERNS['^PETROBRAS .*'] = 'FUEL'
EXPENSES_TYPE_PATTERNS['^ESSO .*'] = 'FUEL'

EXPENSES_TYPE_PATTERNS['^AIRBNB \* .*'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^IBIS .*'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^ASSIST CARD$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^DESPEGAR$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^CAR HIRE .*'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^.*BOOKING.COM$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^EASYJET$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^.*BOOKING.COM$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^.*BOOKING.COM$'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['.*TAX.?FREE.*'] = 'TRAVEL'
EXPENSES_TYPE_PATTERNS['^GLOBALBLUE.*'] = 'TRAVEL'

EXPENSES_TYPE_PATTERNS['^UBER .*'] = 'TANSPORT'

EXPENSES_TYPE_PATTERNS['^AMZN MKTP .*'] = 'ONLINE_SHOPPING'
EXPENSES_TYPE_PATTERNS['^PUNTOMIO .*'] = 'ONLINE_SHOPPING'
EXPENSES_TYPE_PATTERNS['^DHL COURIER$'] = 'ONLINE_SHOPPING'
EXPENSES_TYPE_PATTERNS['^CORREO URUGUAYO\-TRIB$'] = 'ONLINE_SHOPPING'

EXPENSES_TYPE_PATTERNS['^NETFLIX\.COM$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^CLUB MALVIN.*'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^DTO ITA.*\- MALV.*N$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^DBD BOOK$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^PASSENGER$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^COPACABANA SHOPPING$'] = 'ENTERTAINMENT' # COPACABANA STORE
EXPENSES_TYPE_PATTERNS['^MACRI SPORT CENTER$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^FOTOESTUDIO 18$'] = 'ENTERTAINMENT'
EXPENSES_TYPE_PATTERNS['^LIBRERIA.*'] = 'ENTERTAINMENT'
 
EXPENSES_TYPE_PATTERNS['^ARREDO$'] = 'HOME'
EXPENSES_TYPE_PATTERNS['^TIENDAS MONTEVIDEO$'] = 'HOME'
EXPENSES_TYPE_PATTERNS['^SODIMAC .*'] = 'HOME'
EXPENSES_TYPE_PATTERNS['^LIDER PLAST$'] = 'HOME'
EXPENSES_TYPE_PATTERNS['^VIVERO .*'] = 'HOME'

EXPENSES_TYPE_PATTERNS['^PUNTA CARRETAS SHOPP$'] = 'PARKING'

EXPENSES_TYPE_PATTERNS['^BANCO DE SEGUROS$'] = 'CAR'

EXPENSES_TYPE_PATTERNS['^MAPFRE$'] = 'CREDIT_CARD_COST'

EXPENSES_TYPE_PATTERNS['^SAN ROQUE$'] = 'HEALTH'


# ------------------------------ CLASSES ------------------------------

class Expense:
    # class attributes ...

    # initializer / instance attributes ...
    def __init__(self, title, date, card_last_digits, amount, currency_code):
        super().__init__()
        self.title = title
        self.date = date
        self.card_last_digits = card_last_digits
        self.amount = amount # decimal.Decimal data type
        self.currency_code = currency_code
    
    def __str__(self):
        return self.title + " - " + self.date +  " - " + self.card_last_digits + " + " + self.currency_code + " " + str(self.amount)

# ------------------------------ RPIVATE FUNCTIONS ------------------------------

def _get_pdf_author(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        # pdf=pdf.encode("utf-8")
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        # print(info.author)
        
        a_str=str(info.author.encode("utf-8"))

        if VERBOSE: print("Author: " + a_str)

        return a_str


def _add_item_to_multimap(map, key, item):
    key_list = map.get(key)
    if key_list is None :
        key_list = []
    key_list.append(item)
    map[key] = key_list

def _add_amount_to_currency_map(map, currency_code, amount):
    total = map.get(currency_code)
    if total is None:
        total = decimal.Decimal("0")
    total = total + amount
    map[currency_code] = total

def _generate_expenses_report(map):

    # expense category type ...
    for expense_type in map.keys():
        if DETAILED_REPORT: print("> " + expense_type)
        if DETAILED_REPORT: print("\t---------------------------------------------------")
        amounts_by_currency_type = {}
        
        # expense lines ...
        expenses = map.get(expense_type)
        for expense in expenses:
            if DETAILED_REPORT: print("\t> " + str(expense))
            _add_amount_to_currency_map(amounts_by_currency_type, expense.currency_code, expense.amount)

        # summary by currency code ...        
        if DETAILED_REPORT: print("\t---------------------------------------------------")

        for currency_code in amounts_by_currency_type.keys():
            amount = str(amounts_by_currency_type.get(currency_code))
            if DETAILED_REPORT: print("\t" + currency_code + ": " + amount)
            if not DETAILED_REPORT: print(expense_type + " " + currency_code + ": " + amount)

        if DETAILED_REPORT: print("\t---------------------------------------------------")
        if DETAILED_REPORT: print("")

def is_decimal(num_text):
    if num_text is None:
        return False
    try:    
        val = float(num_text.replace(',','.')) 
        return True
    except ValueError:
        return False    

# ------------------------------ ITAU PARSER ------------------------------

def _itau_cc_parser_apply(file_name):
    if re.match('.*\.pdf$', file_name):
        pdf_author = _get_pdf_author(file_name)
        return re.match(ITAU_CC_PARSER_AUTHOR_REGEX_PATTERN, pdf_author)
    return False

def _itau_cc_parser_do(file_name):
    # load your PDF ...
    with open(file_name, "rb") as f:
        pdf = pdftotext.PDF(f)

    # show pages ...
    if VERBOSE: print("Pages: " + str(len(pdf)))

    expenses_by_type={}

    # iterate over all the pages ...
    for page in pdf:
        page=page.encode("utf-8")

        reference_line_length = None
        reference_line_dollar_amount = None
        reference_line_dollar_index = None
        reference_line_local_amount = None
        reference_line_local_index = None

        try:
            # read the full page (JUST FOR TEST)
            if VERY_VERBOSE: print("#" * 100)
            if VERY_VERBOSE: print(str(page).replace("\\n", "\n"))
            if VERY_VERBOSE: print("#" * 100)

            lines = str(page).split("\\n")
            
            if VERY_VERBOSE: print("Lines count: " + str(len(lines)))

            last_expense_cache = None # in order to apply tax discounts ...

            for line in lines:

                line_length = len(line.strip())

                if VERY_VERBOSE: print("\n" * 3)
                if VERY_VERBOSE: print("\tRAW LINE BEFORE FILTER: " + line)

                first_char_is_numeric = line[0].isdigit()

                # if it is a detail line (by length) ...
                if re.match(DETAIL_LINE_REGEX_PATTERN, line) and not re.match(BLACKLISTED_LINES_REGEX_PATTERN, line):

                    # resolve reference length in other to parse amount currencies better ...
                    if reference_line_length is None:
                        if VERBOSE: print("\t\tCURRENCY REFERENCE LINE: " + line + " - size: " + str(line_length))
                        reference_line_length = line_length

                        line_list = list(filter(lambda x: x != '' and is_decimal(x), line[45:].split(' ')))

                        last_amount = line_list[-1]
                        
                        reference_line_dollar_amount = last_amount
                        reference_line_dollar_index = line.rfind(reference_line_dollar_amount)
          
                        reference_line_local_amount = None
                        reference_line_local_index = None

                        

                        line_list_without_last_amount= line_list[:-1]

                        # if it has both amounts, the last one is dollars, and the other one is local ...
                        if len(line_list_without_last_amount) > 0:
                            before_last_amount = line_list_without_last_amount[-1]
                            reference_line_local_amount = before_last_amount
                            reference_line_local_index = line.find(before_last_amount)

                        else:
                            # if line has only one amount, it is on local currency ...
                            reference_line_local_amount = reference_line_dollar_amount
                            reference_line_local_index = reference_line_dollar_index
                            reference_line_dollar_amount = None
                            reference_line_dollar_index = None

                        
                        if VERBOSE: print("\t\t\tList: " + str(line_list))
                        if VERBOSE: print("\t\t\tLength: " + str(reference_line_length))
                        if VERBOSE: print("\t\t\tDOLLAR:")
                        if VERBOSE: print("\t\t\t\tAmount:" + str(reference_line_dollar_amount))
                        if VERBOSE: print("\t\t\t\tIndex:" + str(reference_line_dollar_index))
                        if VERBOSE:  print("\t\t\tLOCAL:")
                        if VERBOSE: print("\t\t\t\tAmount:" + str(reference_line_local_amount))
                        if VERBOSE: print("\t\t\t\tIndex:" + str(reference_line_local_index))
                        if VERBOSE: print("\n")

                    if VERBOSE: print("\n" * 2)

                    line_amounts_array = line[60:].split(" ")
                    # line_amounts_array = list(filter(lambda c: c != "" or c is None, line_amounts_array))
                    raw_amount = line_amounts_array[-1]
                    raw_amount_first_index = line.find(raw_amount)
                    raw_amount_last_index = line.rfind(raw_amount)

                    if VERBOSE: print("\tRAW LINE: " + line + " - size: " + str(line_length))

                    if VERBOSE: print("\t\tNEW AMOUNT VALUE: \t" + str(raw_amount))
                    if VERBOSE: print("\t\tNEW AMOUNT F_INDEX: \t" + str(raw_amount_first_index))
                    if VERBOSE: print("\t\tNEW AMOUNT L_INDEX: \t" + str(raw_amount_last_index))
                    if VERBOSE: print("\t\tLINE LENGTH: \t" + str(line_length))

                    # resolve currencies ...
                    is_dolar_currency = False
                    is_local_currency = False 

                    if reference_line_dollar_amount is None:
                        is_local_currency = True
                    else:
                        lower_index = raw_amount_last_index - CALCULATION_TOLERANCE
                        upper_index = raw_amount_last_index + CALCULATION_TOLERANCE

                        if lower_index <= reference_line_dollar_index and upper_index >= reference_line_dollar_index:
                            is_dolar_currency = True
                        else:
                            is_local_currency = True 
                

                    '''
                    if reference_line_length is None:
                        if VERBOSE: print("WARNING: Could not resolve reference line! (useful to parse currencies in a better way)")
                            
                        is_dolar_currency = raw_amount_first_index != raw_amount_last_index
                        is_dolar_currency = is_dolar_currency or line_length == 94
                        if not is_dolar_currency:
                            is_a_dolar_line_length = line_length >= 92 and line_length <= 94
                            is_a_dolar_amount_index = raw_amount_first_index == 87 or raw_amount_first_index == 88
                            is_dolar_currency = is_a_dolar_line_length and is_a_dolar_amount_index

                        is_local_currency = not is_dolar_currency

                    else:
                        is_dolar_currency = line_length == reference_line_length
                        is_local_currency = not is_dolar_currency
                    '''

                    '''
                    # new pdf lengths ...
                    is_dolar_currency = line_length == 108 or line_length == 94
                    is_local_currency = line_length == 98

                    # old pdf lengths ...
                    if not is_dolar_currency and not is_local_currency:
                        is_dolar_currency = is_dolar_currency or line_length == 93
                        is_local_currency = is_local_currency or line_length == 84

                    # old pdf lengths ...
                    if not is_dolar_currency and not is_local_currency:
                        is_dolar_currency = is_dolar_currency or line_length == 92
                        is_local_currency = is_local_currency or line_length == 83
                    '''

                    if VERBOSE: print("\t\tis_dolar_currency:\t" + str(is_dolar_currency))
                    if VERBOSE: print("\t\tis_local_currency:\t" + str(is_local_currency))

                    

                    if ((is_dolar_currency or is_local_currency)):

                        # parsing date ...
                        day=line[0:2]
                        month=line[3:5]
                        year=line[6:8]
                        expense_date = day + "/" + month + "/" + year
                        
                        # parsing credit card last digits ...
                        cc_last_digits = line[9:14]

                        # remove date and cc data from line ..
                        first_letter = re.search("[a-zA-Z]", line).group()
                        first_letter_index = line.find(first_letter)
                        reduced_line = line[first_letter_index:]

                        line_array = reduced_line.split("   ")

                        expense_amount_str = line_array[-1].strip().replace(",",".")
                        expense_amount = decimal.Decimal(expense_amount_str)

                        expense_title = line_array[0].strip()
                        
                        # check if it is a valid expense line ...
                        if expense_title != "":

                            if re.match(TAX_DISCOUNT_REGEX_PATTERN, expense_title):
                                last_expense_cache.amount = last_expense_cache.amount + expense_amount
                                if VERBOSE: print("\t\tIS A TAX DISCOUNT!!!  :  " + expense_title)

                            else:

                                currency_code = DOLLAR_CURRENCY_CODE if is_dolar_currency else LOCAL_CURRENCY_CODE 

                                expense = Expense(expense_title, expense_date, cc_last_digits, expense_amount, currency_code)
                                last_expense_cache = expense
                                if VERBOSE: print("\t\tRESOLVED LINE: \t\t" + expense.__str__())

                                # get expense type ...
                                expense_type_match_found = False
                                for expense_type_pattern in EXPENSES_TYPE_PATTERNS.keys():
                                    if re.match(expense_type_pattern, expense_title) and not expense_type_match_found:
                                        expense_type_match_found = True
                                        expense_type = EXPENSES_TYPE_PATTERNS[expense_type_pattern]
                                        _add_item_to_multimap(expenses_by_type, expense_type, expense)

                                if not expense_type_match_found:
                                    _add_item_to_multimap(expenses_by_type, OTHER_EXPENSE_TYPE_TOKEN, expense)

        except ZeroDivisionError:
        # except:
            print("Error!")

    # print(expenses_by_type)
    return expenses_by_type
    
# ------------------------------ MAIN ------------------------------

if __name__== "__main__":   

    current_folder = '.'
    first_param = None
    for arg in sys.argv[1:]:
        if arg == "-v":
            VERBOSE = True
        elif arg == "-vv":
            VERY_VERBOSE = True
        elif arg == "-d":
            DETAILED_REPORT = True    
        else:
            first_param=arg
        
    for current_file in os.listdir(current_folder):
        if os.path.isfile(current_file):

            if VERBOSE: print("Trying to parse file \"" + current_file + "\" ...")

            # find and run parser ...
            if _itau_cc_parser_apply(current_file):

                if first_param is None or first_param == current_file:
                    file_title="File: " + current_file
                    print(file_title)
                    print("-" * len(file_title))
                    
                    result = _itau_cc_parser_do(current_file)
                    _generate_expenses_report(result)   
                    print("")
            else:
                if VERBOSE: print("No parser found for file: " + current_file)
