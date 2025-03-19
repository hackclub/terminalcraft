import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import pandas as pd


URL = input("Enter the website URL: ")
HTMLVar = input("Enter HTML tags you're looking for separated by spaces (one tag for each selection of data you want): ")
IDVar = input('Enter the HTML classes you are looking for, again in order and one per selection. If none, type "N": ')
tagList = HTMLVar.split()
idList = IDVar.split()


def dataSetup():
    dataList = []
    indexVar = 0
    for tag in tagList:
        dataList.append([tag])
    for id in idList:
        dataList[indexVar].insert(1, id)
        indexVar += 1
    return dataList



def scraper():
    #setup function with soup parse and data structures
    inputList = dataSetup()
    resultList = []
    pageVar = requests.get(URL)
    soup = BeautifulSoup(pageVar.content, "html.parser")

    #setup column titles
    ColTitlesList = ColTitles.split(",")

    #setup list structure for excel data
    for colTitle in ColTitlesList:
        resultList.append([colTitle])


    #iterate through column titles with according data
    for item in dataSetup():
        indexVar = dataSetup().index(item)

        if idList[indexVar] == 'N':
            results = soup.find_all(tagList[indexVar])
        else:
            results = soup.find_all(tagList[indexVar], attrs={'class': idList[indexVar]})

        innerindNum = 1
        for thing in results:
            resultList[indexVar].insert(innerindNum, thing.text.rstrip().lstrip())
            innerindNum += 1

    return resultList




ExcelName = input("Enter your Excel document's name: ")
ColTitles = input("Enter the title of each Excel column separated by commas: ")
ExcelLink = ExcelName + ".xlsx"

wb = Workbook()
ws = wb.active



def process(data):
    wb.save(ExcelLink)
    df = pd.DataFrame(data)
    newdf = df.transpose()
    df_existing = pd.read_excel(ExcelLink)
    df_combined = df_existing._append(newdf, ignore_index=True)
    df_combined.to_excel(ExcelLink, index=False)



process(scraper())