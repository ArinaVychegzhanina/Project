from tkinter import *
from tkinter.ttk import Combobox
from tkinter.ttk import Checkbutton
from tkinter.ttk import Radiobutton
from tkinter import Menu
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Notebook, Style
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import investpy # пакет, откуда получаем информацию по рыночным ценам акций
import sqlite3 # модуль для работы с базой данных
import json # модуль для работы типом json
import statistics # модуль, в котором реализован метод mean()



types = ["Banks", "Biotechnology", "Cars", "Hotels", "IT", "Entertainments", "Clothes", "Food"] # типы компаний
countries = ["United States", "Russia", "China", "France", "Japan"] # названия стран
dict_types = {"Banks": "1", "Biotechnology": "2", "Cars": "3", "Hotels": "4", "IT": "5", "Entertainments": "6",
              "Clothes": "7", "Food": "8"} # коды названий компаний, которые им присвоены в базе данных
dict_countries = {"United States": "1", "Russia": "2", "China": "3", "France": "4", "Japan": "5"} # коды стран, которые им присвоены в базе данных
dict_currency = {"United States": "USD", "Russia": "RUB", "China": "CNY", "France": "EUR", "Japan": "JPY"} # валюта каждой из наших стран
dict_transfer = {"USD": 1, "RUB": 64.74, "CNY": 0.16, "EUR": 1.04, "JPY": 0.0078} # сколько долларов в единице данной валюты


stocks = sqlite3.connect("C:\\Users\\Моя госпожа\\Desktop\\Питонище\\Stocks.s3db") # соединение с базой данных
cursor = stocks.cursor() # объект для работы с базой данных: формирования запросов поиска, добавления, удаления и т.д.


# функция, которая возвращает информацию по рыночным ценам акций компаний выбранного типа в выбраной стране в течении выбранного периода времени
def info_stocks(country: str, type: str, date_from: str, date_to: str):
    tos = date_to.split("/")
    fro = date_from.split("/")
    # проверка на правильность ввода даты
    if int(tos[2]) < 2012 or int(fro[2]) < 2012:
        messagebox.showerror("Ошибка", "Дата введена неккоректно")
        return f"Date entered incorrectly"
    elif int(fro[2]) > int(tos[2]):
        messagebox.showerror("Ошибка", "Дата введена неккоректно")
        return f"Date entered incorrectly"
    elif int(fro[2]) == int(tos[2]) and int(fro[1]) > int(tos[1]):
        messagebox.showerror("Ошибка", "Дата введена неккоректно")
        return f"Date entered incorrectly"
    elif int(fro[2]) == int(tos[2]) and int(fro[1]) == int(tos[1]) and int(fro[0]) > int(tos[0]):
        messagebox.showerror("Ошибка", "Дата введена неккоректно")
        return f"Date entered incorrectly"
    else:
	# формирование запроса по выбору из базы данных из поля Code компаний, у которых страна и тип совпадают с выбранными	
        result = cursor.execute("select Code from Stocks where country=:code_count and type=:code_type",
                                {"code_count": dict_countries[country], "code_type": dict_types[type]})
        dict_result = {} # наш будущий результат
        for row in result:
            info = json.loads(investpy.get_stock_historical_data(stock=row[0], country=country, from_date=date_from,
                                to_date=date_to, as_json=True)) # получаем информацию в формате json и преобразуем в словарь
	    # формируем словарь для красивого вывода графика
            if int(tos[2]) - int(fro[2]) == 0:
                if int(tos[1]) - int(fro[1]) == 0:
                    dict_result[info["name"]] = {}
                    for pr in info["historical"]:
                        dict_result[info["name"]][pr["date"].split("/")[0]] = pr["close"]
                elif int(tos[1]) - int(fro[1]) == 1:
                    dict_result[info["name"]] = {}
                    for pr in info["historical"]:
                        if fro[1] in pr["date"]:
                            dict_result[info["name"]][f"{pr['date'].split('/')[0]}/{fro[1]}"] = pr["close"]
                        elif tos[1] in pr["date"]:
                            dict_result[info["name"]][f"{pr['date'].split('/')[0]}/{tos[1]}"] = pr["close"]
                else:
                    list_result = []
                    for pr in info["historical"]:
                        list_result.append(pr["close"])
                    dict_result[info["name"]] = list_result
	    # формируем словарь для большого периода
            elif int(fro[1]) == 12 and int(tos[1]) == 1 and int(tos[2]) - int(fro[2]) == 1:
                dict_result[info["name"]] = {}
                for pr in info["historical"]:
                    if fro[1] in pr["date"]:
                        dict_result[info["name"]][f"{pr['date'].split('/')[0]}/{fro[1]}/{fro[2][2:]}"] = pr["close"]
                    elif tos[1] in pr["date"]:
                        dict_result[info["name"]][f"{pr['date'].split('/')[0]}/{tos[1]}/{tos[2][2:]}"] = pr["close"]
            else:
                list_result = []
                for pr in info["historical"]:
                    list_result.append(pr["close"])
                dict_result[info["name"]] = list_result
	# проверка на отсутствие информации	
        if dict_result == {}:
            return f"Unfortunately there are no companies of this type"
        return dict_result # возвращаем результат


# функция для сравнения рыночных цен акций выбранного типа компаний в двух выбранных странах в течении выбранного периода времени
def compare_stocks(country_1: str, country_2: str, typen: str, date_from: str, date_to: str):
    info_1 = info_stocks(country_1, typen, date_from, date_to) # информация по акциям в первой стране
    info_2 = info_stocks(country_2, typen, date_from, date_to) # информация по акциям во второй стране
    # проверка на неправильно введённую дату
    if info_1 == f"Date entered incorrectly":
        return f"Date entered incorrectly"
    # проверка на отсутствие информации
    elif info_1 == f"Unfortunately there are no companies of this type" and \
            not info_2 == f"Unfortunately there are no companies of this type":
        return f"The stocks of {country_2} are more beneficial"
    elif not info_1 == f"Unfortunately there are no companies of this type" and \
            info_2 == f"Unfortunately there are no companies of this type":
        return f"The stocks of {country_1} are more beneficial"
    elif info_1 == f"Unfortunately there are no companies of this type" and \
            info_2 == f"Unfortunately there are no companies of this type":
        return f"Unfortunately there are no companies of this type"
    else:
        comp_1 = 0 # будущий результат в первой стране
        comp_2 = 0 # будущий результат во второй стране
	# высчитываем среднее арифметическое по всем рыночным ценам акций в первой стране
        for i in info_1.keys():
            if type(info_1[i]) is dict:
                comp_1 += round(statistics.mean(info_1[i].values()) * dict_transfer[dict_currency[country_1]], 2)
            else:
                comp_1 += round(statistics.mean(info_1[i]) * dict_transfer[dict_currency[country_1]], 2)
	# высчитываем среднее арифметическое по всем рыночным ценам акций во второй стране	
        for i in info_2.keys():
            if type(info_2[i]) is dict:
                comp_2 += round(statistics.mean(info_2[i].values()) * dict_transfer[dict_currency[country_2]], 2)
            else:
                comp_2 += round(statistics.mean(info_2[i]) * dict_transfer[dict_currency[country_2]], 2)
	# сравнение и выдача окончательного результата	
        if comp_1 > comp_2:
            return f"The stocks of {country_1} are more beneficial than the stocks of {country_2}"
        elif comp_1 < comp_2:
            return f"The stocks of {country_2} are more beneficial than the stocks of {country_1}"
        else:
            return f"The stocks of both countries are beneficial"


# функция, возвращающая профиль компании
def company_description(company: str):
    # формирование запроса по поиску в базе данных такой компании	
    result = cursor.execute("select Description from Stocks where Name=:company", {"company": company})
    # передвигаемся по выбранным строкам и возвращаем описание	
    for row in result:
        return row[0]

import tkinter as tk
from tkinter import ttk


def clicked4():
    win = tk.Tk()
    win.title('Информация о компаниях')
    win.geometry('800x750')
    win.configure(bg='paleturquoise')
    n=1
    for i in range(len(list(info_stocks(var10.get(), var20.get(), str(var30.get()), str(var40.get()))))):
        ttk.Label(win,
                  text=company_description(list(info_stocks(var10.get(), var20.get(), str(var30.get()), str(var40.get())))[i]),
                  wraplength=800, justify="center", background='violet', foreground="white",
                  font=("Times New Roman", 10)).grid(row=i, column=0)
        n+=1
    for i in range(len(list(info_stocks(var11.get(), var20.get(), str(var30.get()), str(var40.get()))))):
        ttk.Label(win,
                text=company_description(list(info_stocks(var11.get(), var20.get(), str(var30.get()), str(var40.get())))[i]),
                wraplength=800, justify="center", background='violet', foreground="white",
                font=("Times New Roman", 10)).grid(row=n+i, column=0)
    wind.mainloop()

def clicked3():
    wind = tk.Tk()
    wind.title('Информация о компаниях')
    wind.geometry('800x750')
    wind.configure(bg='paleturquoise')
    for i in range(len(list(info_stocks(var1.get(), var2.get(), str(var3.get()), str(var4.get()))))):
        ttk.Label(wind,
                  text=company_description(list(info_stocks(var1.get(), var2.get(), str(var3.get()), str(var4.get())))[i]),
                  wraplength=800, justify="center", background='violet', foreground="white",
                  font=("Times New Roman", 15)).grid(row=i, column=0)
    wind.mainloop()


def clicked2():
    df1 = pd.DataFrame(info_stocks(var10.get(), var20.get(), str(var30.get()), str(var40.get())),
                      columns=list(info_stocks(var10.get(), var20.get(), str(var30.get()), str(var40.get()))))
    df1.plot(y=list(info_stocks(var10.get(), var20.get(),  str(var30.get()), str(var40.get())))).patch.set_facecolor('antiquewhite')
    plt.gcf().canvas.set_window_title("Chart")  # меняем заголовок
    plt.grid()  # выводим решётку (сетку)
    plt.title('Stock chart of '+ var10.get())
    plt.xlabel("Time interval", fontsize=14, fontweight="bold")
    plt.ylabel("Stock value, " + dict_currency[var10.get()], fontsize=14, fontweight="bold")

    df2 = pd.DataFrame(info_stocks(var11.get(), var20.get(), str(var30.get()), str(var40.get())),
                      columns=list(info_stocks(var11.get(), var20.get(), str(var30.get()), str(var40.get()))))
    df2.plot(y=list(info_stocks(var11.get(), var20.get(), str(var30.get()), str(var40.get())))).patch.set_facecolor(
        'antiquewhite')
    plt.gcf().canvas.set_window_title("Chart")  # меняем заголовок
    plt.grid()  # выводим решётку (сетку)
    plt.title('Stock chart of ' + var11.get())
    plt.xlabel("Time interval", fontsize=14, fontweight="bold")
    plt.ylabel("Stock value, " + dict_currency[var11.get()], fontsize=14, fontweight="bold")

    plt.show()
    messagebox.showinfo('Summary', compare_stocks(var10.get(), var11.get(), var20.get(), str(var30.get()), str(var40.get())))
    print(var10.get(), var11.get(), var20.get(), str(var30.get()), str(var40.get()))



def clicked1():
    df = pd.DataFrame(info_stocks(var1.get(), var2.get(), str(var3.get()), str(var4.get())),
                      columns=list(info_stocks(var1.get(), var2.get(), str(var3.get()), str(var4.get()))))
    df.plot(y=list(info_stocks(var1.get(), var2.get(),  str(var3.get()), str(var4.get())))).patch.set_facecolor('antiquewhite')
    plt.gcf().canvas.set_window_title("Chart")  # меняем заголовок
    plt.grid()  # выводим решётку (сетку)
    plt.title('Stock chart of '+ var10.get())
    plt.xlabel("Time interval", fontsize=14, fontweight="bold")
    plt.ylabel("Stock value, " + dict_currency[var10.get()], fontsize=14, fontweight="bold")
    plt.show()
    print(var1.get(), var2.get(), str(var3.get()), str(var4.get()))


# Creating tkinter window
window = tk.Tk()
window.title('Акции')
window.geometry('800x750')
style = Style()
style.theme_use('default')
style.configure('TNotebook.Tab', background="greenyellow", font=('URW Gothic L','25','bold'))


# Create a Notebook widget
note =Notebook(window)

# Add a frame for adding a new tab
frame1= Frame(note, width= 800, height=750)
frame1.configure(background='moccasin')
# Adding the Tab Name
note.add(frame1, text= 'Получить данные')
frame2 = Frame(note, width= 800, height=750)
frame2.configure(background='moccasin')
note.add(frame2, text= "Сравнить данные")


# frame1
ttk.Label(frame1, text = "Здесь Вы можете получить данные по акциям крупных компаний выбранного типа в выбранной стране в течении выбранного периода, которые будут представлены в виде графика.",
		wraplength=800, justify="center", background = 'coral', foreground ="white",
		font = ("Times New Roman", 20)).grid(row = 0, column = 0, columnspan=5, **{ 'ipadx': 10, 'ipady': 10 , 'sticky': 'nswe' })

ttk.Label(frame1, text = "Выберите страну:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 1, padx = 10, pady = 25)
v1 = StringVar()
var1 = ttk.Combobox(frame1, width = 20, textvariable = v1, font=("Times New Roman", 20))
var1['values'] = countries
var1.grid(column = 1, row = 1)
var1.current()

ttk.Label(frame1, text = "Выберите тип:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 2, padx = 10, pady = 25)
v2 = StringVar()
var2 = ttk.Combobox(frame1, width = 20, textvariable = v2, font=("Times New Roman", 20))
var2['values'] = types
var2.grid(column = 1, row = 2)
var2.current()

ttk.Label(frame1, text = "Введите первый день:\n(в формате дд/мм/гг)",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 3, padx = 10, pady = 25)
v3 = StringVar()
var3 = Entry(frame1, width = 20, textvariable = v3, font=("Times New Roman", 20))
var3.grid(column = 1, row = 3)

ttk.Label(frame1, text = "Введите последний день:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 4, padx = 10, pady = 25)
v4 = StringVar()
var4 = Entry(frame1, width = 20, textvariable = v4, font=("Times New Roman", 20))
var4.grid(column = 1, row = 4)
button1 = Button(frame1, text="Построить график",font = ("Times New Roman", 25), command=clicked1).grid(column = 1, row =5)
button11 = Button(frame1, text="Информация о компаниях",font = ("Times New Roman", 25), command=clicked3).grid(column = 1, row =6)

# frame2
ttk.Label(frame2, text = 'Здесь Вы можете сравнить акции крупных компаний выбранного типа в двух выбранных странах за выбранный период времени.',
		wraplength=800, justify="center", background = 'coral', foreground ="white",
		font = ("Times New Roman", 20)).grid(row = 0, column = 0, columnspan=5, **{ 'ipadx': 10, 'ipady': 10 , 'sticky': 'nswe' })

ttk.Label(frame2, text = "Выберите первую страну:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 1, padx = 10, pady = 25)
v10 = StringVar()
var10 = ttk.Combobox(frame2, width = 20, textvariable = v10, font=("Times New Roman", 20))
var10['values'] = countries
var10.grid(column = 1, row = 1)
var10.current()

ttk.Label(frame2, text = "Выберите вторую страну:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 2, padx = 10, pady = 25)
v11 = StringVar()
var11 = ttk.Combobox(frame2, width = 20, textvariable = v11, font=("Times New Roman", 20))
var11['values'] = countries
var11.grid(column = 1, row = 2)
var11.current()

ttk.Label(frame2, text = "Выберите тип:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 3, padx = 10, pady = 25)
v20 = StringVar()
var20 = ttk.Combobox(frame2, width = 20, textvariable = v20, font=("Times New Roman", 20))
var20['values'] = types
var20.grid(column = 1, row = 3)
var20.current()

ttk.Label(frame2, text = "Введите первый день:\n(в формате дд/мм/гг)",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 4, padx = 10, pady = 25)
v30 = StringVar()
var30 = Entry(frame2, width = 20, textvariable = v30, font=("Times New Roman", 20))
var30.grid(column = 1, row = 4)

ttk.Label(frame2, text = "Введите последний день:",
		font = ("Times New Roman", 25), background = 'darkorange', foreground ="lavenderblush").grid(column = 0,
		row = 5, padx = 10, pady = 25)
v40 = StringVar()
var40 = Entry(frame2, width = 20, textvariable = v40, font=("Times New Roman", 20))
var40.grid(column = 1, row = 5)
button2 = Button(frame2, text="Построить график",font = ("Times New Roman", 25), command=clicked2).grid(column = 1, row =6)
button22 = Button(frame2, text="Информация о компаниях",font = ("Times New Roman", 25), command=clicked4).grid(column = 1, row =7)




note.pack(expand= True, fill=BOTH)
window.mainloop()



