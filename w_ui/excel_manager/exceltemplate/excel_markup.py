import re
import datetime
from excel_wrap import Excel_Wrap


#0v2# JC  Sep 11, 2023  Use in WT
#0v1# JC  Aug  8, 2018  Setup initial

#NOTES:
#- watch when no entry for date.  Use blank?
#- deal with hour and minutes? ie/ 11:30?


def convert2datetime(a_date,a_time):
    # 8/6/2018    11.00

    #Raw time assumption if <6 then am
    hh,mm=re.split(r'\.',a_time)
    hh=int(hh)
    if hh<6: hh+=12

    a_time=str(hh)+"."+str(mm)
    date_str=a_date+" "+a_time
    format_str = '%m/%d/%Y %H.%M' # The format
    datetime_obj = datetime.datetime.strptime(date_str, format_str)
    return datetime_obj

def load_raw():
    #Iterate over raw file as a dictionary
    #Date    Time    Subject    Account Name    First Name    LastName    Location
    #8/6/2018    11.00    Introduction    Motor Drive    D    Molloy    River

    filename='raw_data.tsv'
    fp=open(filename)
    c=0
    for line in fp.readlines():
        c+=1
        cols=re.split("\t",line.strip())
        if c==1:
            headers=cols
            continue
        dd={}
        for i,col in enumerate(cols):
            dd[headers[i]]=col.strip()
        yield dd
    fp.close()
    return

def get_weeknum(date_obj):
    # week 1 is always January 1 through January 7, regardless of the day of the week
    # https://stackoverflow.com/questions/2600775/how-to-get-week-number-in-python
    return (((date_obj - datetime.datetime(date_obj.year,1,1)).days // 7) + 1)

def do_markup():
    Excel=Excel_Wrap()

    filename="Spreadsheet Template.xlsx"
    filename_out="marked_up.xlsx"
    
    #/  Create copy
    Excel.create_copy_from_to(filename,filename_out)
    
    #/  Load worksheet
    Excel.open(filename_out)
    
    sheet1=Excel.load_sheet(sheet_name='Call Plan')  #Assumes first or use name  sheet_name='Template')
    
    #/  Iterate over raw data
    for row in load_raw():
        date_obj=convert2datetime(row['Date'],row['Time']) #Expect 8/6/2018 11.00
        row['weeknum']=get_weeknum(date_obj)               #32 (Week 32)
        row['dayofweek']=date_obj.strftime('%A')           #Wednesday
        row['dayofweeknum']=date_obj.weekday()             #0 is Monday
        row['hour']=date_obj.hour                          #11
        
        print (str(row))
        
        #/  Set date heading (8/6/2018)
        #date_heading=str(date_obj.strftime("%m/%d/%Y"))
        colnum=3+row['dayofweeknum']
        date_heading=str(date_obj.strftime("%d-%b"))
        date_heading=re.sub(r'^0','',str(date_heading))#remove leading 0 as %-d is platform specific
        sheet1.cell(row=4,column=colnum).value=date_heading
        

        #/  Set info into cells
        
        #/  Calc location of row:
        #   - 6 is offset from top
        #   - 4 is height of cells
        #   - hour adjusted since 1 is 1pm or 13
        hour_adjusted=row['hour']
        #Adjust for am/pm
        if hour_adjusted<7:hour_adjusted+=12
        #Offset hour as starts at 6 so 6 is 0
        hour_adjusted-=6
        row_start=6+(hour_adjusted*4)
        
        #/  Write rows
        sheet1.cell(row=row_start+0,column=colnum).value=row['Subject']
        sheet1.cell(row=row_start+1,column=colnum).value=row['Account Name']
        sheet1.cell(row=row_start+2,column=colnum).value=row['First Name']+" "+row['LastName']
        sheet1.cell(row=row_start+3,column=colnum).value=row['Location']
        

    #/ Set global info
    sheet1.cell(row=4,column=2).value="Week "+str(row['weeknum'])
    
    Excel.save()
    print ("Done.")
    return

def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    branches=['do_markup']
    for b in branches:
        globals()[b]()












