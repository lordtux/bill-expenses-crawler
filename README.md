# Bill expenses report generator

(Currently, only supports Itaú credit card bills)

## Usage:
---------
	bill_crawler.py [folder or file] [modifiers]
		Scan all pdfs files in current folder

## Usage examples:
------------------
```bash
    bill_crawler.py
	  or
	bill_crawler.py V_22.pdf -d
	  or
	bill_crawler.py -d -v
```

## Arguments:
-------------
```bash
	-d, --details              Show details, every expense line by type
	-v, -verbose               Verbose output. Just for debugging ...
	-vv, -very-verbose         Very verbose output. Just for debugging (really hard) ...
```

## Example outputs

### Scan full current folder
```bash
$ ./bill_crawler.py

File: V_201912.pdf
------------------
ONLINE_SHOPPING UYU: 15.50
ENTERTAINMENT UYU: 4250.99
CLOTHING UYU: 3178.73
HOME UYU: 1686.00
HEALTH UYU: 653.00
FOOD UYU: 6595.58
SUPERMARKET UYU: 15914.40
CREDIT_CARD_COST UYU: 254.00
CAR UYU: 4563.00
FUEL UYU: 2260.00

File: V_202001.pdf
------------------
TRAVEL USD: 206.14
ENTERTAINMENT USD: 15.99
ENTERTAINMENT UYU: 5216.50
ONLINE_SHOPPING USD: 21.00
HOME UYU: 126.00
CLOTHING UYU: 3601.84
FOOD UYU: 7184.80
SUPERMARKET UYU: 15651.57
FUEL UYU: 5341.00
PARKING UYU: 210.00
CAR UYU: 4563.00
CREDIT_CARD_COST UYU: 254.00
TANSPORT UYU: 137.43
HEALTH UYU: 1681.00
```

### Scann current foder filtering by file name, with details
```bash
$ ./bill_crawler.py V_201912.pdf -d

File: V_201912.pdf
------------------
> ONLINE_SHOPPING
	---------------------------------------------------
	> CORREO URUGUAYO-TRIB - 27/11/19 - XXXX  + UYU 15.50
	---------------------------------------------------
	UYU: 15.50
	---------------------------------------------------

> ENTERTAINMENT
	---------------------------------------------------
	> NETFLIX.COM - 02/12/19 - XXXX  + UYU 15.99
	> CLUB MALVIN - 26/11/19 - XXXX  + UYU 2604.00
	> DTO ITA\xc3\x9a- MALV\xc3\x8dN - 26/11/19 - XXXX  + UYU -130.20
	> CLUB MALVIN - 03/12/19 - XXXX  + UYU 2516.00
	> CLUB MALVIN 5% - 03/12/19 - XXXX  + UYU -754.80
	---------------------------------------------------
	UYU: 4250.99
	---------------------------------------------------

> CLOTHING
	---------------------------------------------------
	> ADAM TAILOR - 02/11/19 - XXXX  + UYU 1756.00
	> H&M - 01/12/19 - XXXX  + UYU 224.50
	> RENNER - 10/12/19 -  XXXX + UYU 1198.23
	---------------------------------------------------
	UYU: 3178.73
	---------------------------------------------------

> HOME
	---------------------------------------------------
	> ARREDO - 05/11/19 - XXXX  + UYU 126.00
	> SODIMAC GIANNATTASIO - 19/11/19 - XXXX  + UYU 601.00
	> SODIMAC GIANNATTASIO - 19/11/19 - XXXX  + UYU 560.00
	> LIDER PLAST - 02/12/19 - XXXX  + UYU 279.00
	---------------------------------------------------
	UYU: 1686.00
	---------------------------------------------------
```