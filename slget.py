re = 0
from bs4 import BeautifulSoup as bs
import requests
def getslserver(pb) -> dict:
    print(pb)
    global re
    try:
        sl = requests.get("https://kigen.co/scpsl/browser.php",{"table":"y"})
        html = sl.text
        soup = bs(html, 'html.parser')
        table = soup.find('table')
        col = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all('td'):
                row_data.append(cell.text.strip()) 
            col.append(row_data)  
        print(col)
        column_indices = []
        printed_rows = set()
        for now in pb:
            print(now)
            for i, row in enumerate(col):
                for j, value in enumerate(row):
                    if value == now:
                        column_indices.append(j)
            if column_indices:
                print(f"pbin=",now)
                
                for index in column_indices:
                    for row in col:
                        if len(row) > index:
                            if row[index] == now:
                                row_tuple = tuple(row)
                                if row_tuple not in printed_rows:
                                    print(row_tuple)
                                    printed_rows.add(row_tuple)
            
            else:
                continue
        if printed_rows == set():
            print("服务器死了 好似")
            return "404"
        return printed_rows
    except:
        if re == 0:
            re = 1
            return getslserver(pb)
        else:
            re = 0
            return "500"