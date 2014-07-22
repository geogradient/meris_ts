def openExcelFile(self, filename='hola'):
        import xlrd 
        book = xlrd.open_workbook(filename)
        sh = book.sheet_by_index(0) 
        for r in range(sh.nrows)[1:]:  print sh.row(r)[:4]
