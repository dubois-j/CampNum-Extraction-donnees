import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import  datetime
from dateutil.relativedelta import relativedelta

class MeteocielProcessor:
    def __init__(self):
        self.base_url = "https://www.meteociel.fr/climatologie/obs_villes.php?code2=75107005"
    
    def get_daily_data_from_period(self, start_month:int, start_year:int, end_month:int, end_year:int):
        # Init on start date
        current_date = datetime.date(year=start_year, month=start_month, day=1)
        end_date = datetime.date(year=end_year, month=end_month, day=1)
        try:
            df = self.get_daily_data_from_date(current_date.month, current_date.year)
        except:
            df = pd.DataFrame()
            
        # Loop until end date is reached
        while current_date < end_date:
            current_date = current_date + relativedelta(months=1)
            try:
                df = pd.concat([df, self.get_daily_data_from_date(current_date.month, current_date.year)], axis=0)
            except:
                print(f"Failed to load data from {current_date.month}-{current_date.year}")
        return df
    
    def get_daily_data_from_date(self, month:int, year:int):
        page = self.fetch_page_from_date(month, year)
        df = self.get_daily_data_from_page(page, month, year)
        return df
    
    def fetch_page_from_date(self, month:int, year:int):
        """
        Fetch the content of the the meteociel website for station 'Eiffel Tower' for a given month & year.as_integer_ratio

        :
        """
        # Error handling
        if month not in [i for i in range(1,13)]:
            raise ValueError(f"Month must be an `int` from 1 to 12, was given {month} instead.")
        if year not in [i for i in range(1996, 2026)]:
            raise ValueError(f"Year must be an ``int from 1996 to 2025, was given {year} instead.")
        
        # Fetch data
        url = f"{self.base_url}&mois={month}&annee={year}"
        response = requests.get(url)

        if response.status_code == 200:
            #print(f"Content from {month}-{year} successfully fetched.")
            return BeautifulSoup(response.content, "html.parser")
        else:
            print(f"Failed to load content from {month}-{year}.")
            print(response.text)
    
    def get_daily_data_from_page(self, page, month:int, year:int):
        data = {"date": [],
        "temp_max": [],
        "temp_min": []
        }

        # Retrieve dates
        dates_content = (
            page
            .find_all("table", cellpadding="2")[0]
            .find_all("td", bgcolor="#FFFFCC")
            )
        for el in dates_content:
            data["date"].append(f"{el.text.split(" ")[-1]}-{month}-{year}")

        # Retrieve max temp
        maxtemp_content = (
            page
            .find_all("table", cellpadding="2")[0]
            .find_all("td", bgcolor="#FFDDDD")
        )
        for el in maxtemp_content:
            temp = el.text.split()[0]
            if temp == "---":
                temp = None
            else:
                temp = float(temp)
            data["temp_max"].append(temp)

        # Retrieve min temp
        mintemp_content = (
            page
            .find_all("table", cellpadding="2")[0]
            .find_all("td", bgcolor="#DDDDFF")
        )
        for el in mintemp_content:
            temp = el.text.split()[0]
            if temp == "---":
                temp = None
            else:
                temp = float(temp)
            data["temp_min"].append(temp)
        
        # Transform to dataframe and return
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df = df.set_index(keys="date")
        return df