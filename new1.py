from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import pandas as pd
import traceback
import os, time
import requests
import json
import csv

flask_app = Flask(__name__, static_folder='static', template_folder='/home/urbano-infotech/Documents/Flask Application P/static')
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user8:password9@localhost:5432/linkedindb'
flask_app.config['SECRET_KEY'] = 'AnonymousWorld'
db = SQLAlchemy(flask_app)
# db.init_app(flask_app)

#___________Define Models for Postgres DB____________# 
class CompanyData(db.Model):
    __tablename__ = 'dataTable'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(2550))
    company_name = db.Column(db.String(2550))
    title = db.Column(db.String(2550))
    services_and_location = db.Column(db.String(2550))
    company_description = db.Column(db.String(2550))
    followers = db.Column(db.String(2550))
    navigation_url = db.Column(db.String(2550))

class LinkedInDetailedData(db.Model):
    __tablename__ = 'linkedin_detailed_data'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    linkedin_url = db.Column(db.String(200))
    company_url = db.Column(db.String(200))
    contact_number = db.Column(db.String(20))
    num_employees = db.Column(db.Integer)
    company_size = db.Column(db.Integer)
    headquarter_country = db.Column(db.String(500))
    headquarter_city = db.Column(db.String(500))
    headquarter_geographic_area = db.Column(db.String(500))  
    headquarter_postal_code = db.Column(db.String(200))  
    headquarter_line1 = db.Column(db.String(200))  
    headquarter_line2 = db.Column(db.String(200)) 
    company_type = db.Column(db.String(50))
    founded_year = db.Column(db.Integer)
    specialities = db.Column(db.Text)
    industries = db.Column(db.Text)

class Clutch(db.Model):
    __tablename__ = 'clutch'
    __table_args__ = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2550))
    description = db.Column(db.String(2550))
    rating = db.Column(db.Float)
    reviews = db.Column(db.String)
    minimum_project_size = db.Column(db.String(2550))
    hourly_rate = db.Column(db.String(2550))
    location = db.Column(db.String(2550))
    profile_url = db.Column(db.String(2550))
    detailed_info = db.Column(db.String(2550))

with flask_app.app_context():
    # db.drop_all()
    db.create_all()

latest_key = []
latest_location = []




#_____________Clutch_______________#

class WebScrapp:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Alt-Used': 'clutch.co',
            'Connection': 'keep-alive',
            'Cookie': 'exp_primary-cta-ab-test_attribute=old-main-CTA; cf_clearance=CElLkfgXYUHd19jbJcgVm.jdkky7RKAzikr5rhGNTG8-1703091322-0-1-47cea029.59fb99c7.717adce6-0.2.1703091322; _hp2_props.1079324124=%7B%22analyticjs%22%3Atrue%2C%22category%22%3A%22Web%20Developers%22%2C%22content_group%22%3A%22directory%22%2C%22debug_mode%22%3Afalse%2C%22page_canonical_id%22%3A1006022600000%2C%22page_number%22%3A0%2C%22page_type%22%3A%22directory%22%2C%22trace_id%22%3A%22ea80844902eb8b6347224bd0d12c42fc%22%2C%22transport_url%22%3A%22https%3A%2F%2Fg.clutch.co%22%2C%22bot%22%3A%22%22%7D; _hp2_id.1079324124=%7B%22userId%22%3A%224621621289075911%22%2C%22pageviewId%22%3A%221031630412510173%22%2C%22sessionId%22%3A%22526683078644898%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _ga_D0WFGX8X3V=GS1.1.1703093512.6.1.1703093517.55.0.0; _ga=GA1.1.477616294.1702974174; _fbp=fb.1.1702974174430.760116764; FPID=FPID2.2.Pwyn3SJjS1wojZJcokA86jUPv38fAdgeR%2B%2F9WQMqSqI%3D.1702974174; CookieConsent={stamp:%27iWxdb6a1nZvD7Ww1Zu1/7tP0/Uswn+k05CFR6NY6nFww8Q8nb0IKHg==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:1%2Cutc:1702976265000%2Cregion:%27in%27}; exp_new-ab-test_attribute=1; shortlist_prompts=true; FPLC=fP4CNIKub9pC7gp3r2rHUJ%2FeAHFM2uCwxPAjypF16JpYd%2Bw%2BNlWfPGgeDEFNd3nLYx29StsZ%2FTw7IXotvJKVASTlJMO0PJP7CnD394LQrOdK6sPFydeMqyauaEF2iA%3D%3D; __cf_bm=Y6XKLnj0FCEXUm0NwLrWVIG06sEerACUB4fp1UlF6pI-1703093516-1-Acpm5XX2tUQcoFIR4t7gd2JAh8AT7cCmvZF1VgKNwx72CYEPiuHrLMpfVRgXUnw4aNCrAD+E+t4X+FwZ2XGK8uc=; _hp2_ses_props.1079324124=%7B%22z%22%3A1%2C%22r%22%3A%22https%3A%2F%2Fclutch.co%2F%22%2C%22ts%22%3A1703093516945%2C%22d%22%3A%22clutch.co%22%2C%22h%22%3A%22%2Fweb-developers%22%2C%22t%22%3A%22Top%20Web%20Developers%20in%20Ahmedabad%20-%202023%20Reviews%20%7C%20Clutch.co%22%2C%22q%22%3A%22%3Fgeona_id%3D12989%22%7D',
            'Host': 'clutch.co',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'        
        }
        self.provider_data_list = []
        self.detailed_info_list = []
        self.detailed_info = "" 
        self.final_output = []

    def extract_provider_info(self, raw_data):
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode('utf-8')

        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data)

        with open('clutchJson2.json', 'w', encoding='utf-8') as file:
            file.write(str(raw_data))

        page_title = raw_data['Title']
        description = raw_data.get('Description', '')
        head_title = raw_data.get('HeadTitle', '')
        url = raw_data.get('URL', '')
        clear_all_url = raw_data.get('ClearAllURL', '')
        base_url = 'https://clutch.co'
        gotoUrl =  base_url + url

        additional_data = {
            "Title": page_title,
            "Description": description,
            "HeadTitle": head_title,
            "URL": url,
            "ClearAllURL": clear_all_url
        }

        facets = raw_data['Facets']

        fields_to_extract = [
            "ClientBudgets",
            "ClientSizes",
            "CompanySizes",
            "Flags",
            "FocusAreas",
            "HourlyRates",
            "Industries",
            "ReviewsCount",
            "ServiceLines",
            "Specializations",
            "VerifiedProfilesCount"
        ]

        extracted_data_dict = {}
        extracted_data_dict.update(additional_data)

        for field in fields_to_extract:
            extracted_data_dict[field] = facets.get(field, '')

        output_file_path = 'clutch_extracted_data.json'

        with open(output_file_path, 'w') as json_file:
            json.dump(extracted_data_dict, json_file, indent=2)

        print(f"Extracted data saved to {output_file_path}")

        response3 = requests.get(gotoUrl, headers=self.headers)
        soup = BeautifulSoup(response3.text, 'lxml')
        # pdb.set_trace()
        provider_list = soup.find_all("div", class_="provider-info col-md-10")

        for provider in provider_list:
            provider_name = provider.find('h3', class_='company_info').text.strip() #
            provider_url = provider.find('a', class_='directory_profile')['href']
            description = provider.find('p', class_='company_info__wrap tagline').text.strip()
            rating_element = provider.find('span', class_='rating sg-rating__number')
            rating = rating_element.text.strip() if rating_element else "N/A"
            Location = provider.find('span', class_='locality').text.strip()
            MinProSize1 = provider.find('div', class_='list-item block_tag custom_popover')
            MinimumProjectSize = MinProSize1.find('span').text.strip()
            hourly_rate_div1 = provider.find('div', class_='col-md-3 provider-info__details')
            hourly_rate_div2 = hourly_rate_div1.find('div', class_='module-list')
            hourly_rate_div3 = hourly_rate_div2.find('div', class_='list-item custom_popover')
            hourly_rate = 'N/A'

            if hourly_rate_div3:
                for item in hourly_rate_div3.find_all('span'):
                    if 'hr' in item.text:
                        hourly_rate = item.text.strip()
                        break

            reviews = provider.find('a', class_='reviews-link sg-rating__reviews directory_profile').text.strip()

            provider_data = {
                'Name': provider_name,
                'Description': description,
                'Rating': rating,
                'Reviews': reviews,
                'MinimumProjectSize': MinimumProjectSize,
                'Hourly Rate': hourly_rate,
                'Location': Location,
            }

            
            profile_link = provider.find('a', class_='directory_profile')
            if profile_link:
                provider_data['Profile URL'] = profile_link.get('href')
                link = provider_data['Profile URL']
                profile_url1 = link
                profile_url = 'https://clutch.co' + profile_url1
                if "#reviews" in profile_url:
                    profile_url2 = profile_url.split("#reviews")[0]
                    self.extract_detailed_info(profile_url2)
                else:
                    self.extract_detailed_info(profile_url)

            self.provider_data_list.append(provider_data)

    def extract_detailed_info(self, profile_url):
            # pdb.set_trace()
            response = requests.get(profile_url, headers=self.headers)
            if response.status_code == 200:
                page_content = response.text
                soup = BeautifulSoup(page_content, 'lxml')
                Info_list = soup.find("div", class_="profile-summary__text cropped-summary-text")

                if Info_list:
                    try:
                        info_text = Info_list.find('p').text.strip()
                        self.detailed_info = info_text + '\n'
                    except AttributeError:
                        pass  

                else:
                    self.detailed_info = "No detailed information available"
                
                # if self.detailed_info not in self.detailed_info_list:
                self.detailed_info_list.append(self.detailed_info)

            if os.path.exists('provider_info1.csv') and os.stat('provider_info1.csv').st_size > 0:
                df_provider_info = pd.read_csv('provider_info1.csv')
                df_detailed_info = pd.read_csv('detailed_info1.csv')
                final_df = pd.concat([df_provider_info, df_detailed_info], axis=1)
                final_df.to_csv('clutchData.csv', index=False)

            with open('output.txt', 'w', encoding='utf-8') as file:
                for info in self.detailed_info_list:
                    file.write(info.encode('utf-8').decode('latin-1') + "\n")

    def save_data(self):
        if self.provider_data_list:
            df_provider_info = pd.DataFrame(self.provider_data_list)
            df_provider_info.to_csv('provider_info1.csv', index=False)

        if self.detailed_info_list:
            df_detailed_info = pd.DataFrame({'Detailed Info': self.detailed_info_list})
            df_detailed_info.to_csv('detailed_info1.csv', index=False)

    def make_req(self, geona_id, service):
        url2 = f"https://clutch.co/directory/facets?geona_id={geona_id}&sort_by=Sponsorship&path=/{service.replace(' ', '-').lower()}&nonce=bvUBRFIoWXkBXKGc"
        # print(url2)
        response2 = requests.get(url2, headers=self.headers)
        if response2.status_code != 200:
            print("Response is not 200")
        # pdb.set_trace()
        raw_data = response2.content
        with open('clutchJson.json', 'w', encoding='utf-8') as file:
            file.write(str(raw_data))
        self.extract_provider_info(raw_data)

    def scrape_data(self, service, location):
        # service = 'Web developers'
        # location = 'Netherlands'
        
        for page in range(1, 2):
            url = f"https://clutch.co/directory/locations?q={location}&facets?geona_id=356&sort_by=Sponsorship&path=/{service.replace(' ', '-').lower()}&nonce=mUMirmQayNUopUKj"
            response = requests.get(url, headers=self.headers)
            print(response)
            data = json.loads(response.text)
            geona_id = data[0].get('GeonaID', '')
            
            # print(geona_id)

            if response.status_code != 200:
                print("Response is not 200")
                break

            # pdb.set_trace()
            self.make_req(geona_id, service)

            new_csv_filename = "new_output.csv"
            new_fieldnames = ['Name', 'Description', 'Rating', 'Reviews', 'MinimumProjectSize', 'Hourly Rate', 'Location', 'Info', 'Profile URL','Detailed Info']

            
            self.save_data()

            with open(new_csv_filename, mode='w', newline='') as new_csvfile:
                new_writer = csv.DictWriter(new_csvfile, fieldnames=new_fieldnames)
                new_writer.writeheader()

                for provider_info in self.provider_data_list:
                    filtered_provider_info = {key: provider_info.get(key, '') for key in new_fieldnames}
                    new_writer.writerow(filtered_provider_info)

            if os.path.exists('provider_info.csv') and os.stat('provider_info.csv').st_size > 0:
                df_provider_info = pd.read_csv('provider_info1.csv')
                df_detailed_info = pd.read_csv('detailed_info1.csv')
                final_df = pd.concat([df_provider_info, df_detailed_info], axis=1)
                final_df.to_csv('clutchData.csv', index=False)

            print(f"Modified data saved to {new_csv_filename}")





#_____________Clutch_______________#

class WebScrap:

    def __init__(self):
        headers1 = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Alt-Used': 'clutch.co',
        'Connection': 'keep-alive',
        'Cookie': 'exp_primary-cta-ab-test_attribute=old-main-CTA; cf_clearance=CElLkfgXYUHd19jbJcgVm.jdkky7RKAzikr5rhGNTG8-1703091322-0-1-47cea029.59fb99c7.717adce6-0.2.1703091322; _hp2_props.1079324124=%7B%22analyticjs%22%3Atrue%2C%22category%22%3A%22Web%20Developers%22%2C%22content_group%22%3A%22directory%22%2C%22debug_mode%22%3Afalse%2C%22page_canonical_id%22%3A1006022600000%2C%22page_number%22%3A0%2C%22page_type%22%3A%22directory%22%2C%22trace_id%22%3A%22ea80844902eb8b6347224bd0d12c42fc%22%2C%22transport_url%22%3A%22https%3A%2F%2Fg.clutch.co%22%2C%22bot%22%3A%22%22%7D; _hp2_id.1079324124=%7B%22userId%22%3A%224621621289075911%22%2C%22pageviewId%22%3A%221031630412510173%22%2C%22sessionId%22%3A%22526683078644898%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _ga_D0WFGX8X3V=GS1.1.1703093512.6.1.1703093517.55.0.0; _ga=GA1.1.477616294.1702974174; _fbp=fb.1.1702974174430.760116764; FPID=FPID2.2.Pwyn3SJjS1wojZJcokA86jUPv38fAdgeR%2B%2F9WQMqSqI%3D.1702974174; CookieConsent={stamp:%27iWxdb6a1nZvD7Ww1Zu1/7tP0/Uswn+k05CFR6NY6nFww8Q8nb0IKHg==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:1%2Cutc:1702976265000%2Cregion:%27in%27}; exp_new-ab-test_attribute=1; shortlist_prompts=true; FPLC=fP4CNIKub9pC7gp3r2rHUJ%2FeAHFM2uCwxPAjypF16JpYd%2Bw%2BNlWfPGgeDEFNd3nLYx29StsZ%2FTw7IXotvJKVASTlJMO0PJP7CnD394LQrOdK6sPFydeMqyauaEF2iA%3D%3D; __cf_bm=Y6XKLnj0FCEXUm0NwLrWVIG06sEerACUB4fp1UlF6pI-1703093516-1-Acpm5XX2tUQcoFIR4t7gd2JAh8AT7cCmvZF1VgKNwx72CYEPiuHrLMpfVRgXUnw4aNCrAD+E+t4X+FwZ2XGK8uc=; _hp2_ses_props.1079324124=%7B%22z%22%3A1%2C%22r%22%3A%22https%3A%2F%2Fclutch.co%2F%22%2C%22ts%22%3A1703093516945%2C%22d%22%3A%22clutch.co%22%2C%22h%22%3A%22%2Fweb-developers%22%2C%22t%22%3A%22Top%20Web%20Developers%20in%20Ahmedabad%20-%202023%20Reviews%20%7C%20Clutch.co%22%2C%22q%22%3A%22%3Fgeona_id%3D12989%22%7D',
        'Host': 'clutch.co',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0'
        }
        self.headers = headers1
        self.provider_data_list = []
        self.detailed_info_list = []
        self.detailed_info = "" 

    def extract_provider_info(self, page_content):
        soup = BeautifulSoup(page_content, 'lxml')
        provider_list = soup.find_all("div", class_="provider-info col-md-10")

        for provider in provider_list:
            provider_name = provider.find('h3', class_='company_info').text.strip() #
            provider_url = provider.find('a', class_='directory_profile')['href']
            description = provider.find('p', class_='company_info__wrap tagline').text.strip()
            rating_element = provider.find('span', class_='rating sg-rating__number')
            rating = rating_element.text.strip() if rating_element else "N/A"
            Location = provider.find('span', class_='locality').text.strip()
            MinProSize1 = provider.find('div', class_='list-item block_tag custom_popover')
            MinimumProjectSize = MinProSize1.find('span').text.strip()
            hourly_rate_div1 = provider.find('div', class_='col-md-3 provider-info__details')
            hourly_rate_div2 = hourly_rate_div1.find('div', class_='module-list')
            hourly_rate_div3 = hourly_rate_div2.find('div', class_='list-item custom_popover')
            hourly_rate = 'N/A'

            if hourly_rate_div3:
                for item in hourly_rate_div3.find_all('span'):
                    if 'hr' in item.text:
                        hourly_rate = item.text.strip()
                        break

            reviews = provider.find('a', class_='reviews-link sg-rating__reviews directory_profile').text.strip()

            provider_data = {
                'Name': provider_name,
                'Description': description,
                'Rating': rating,
                'Reviews': reviews,
                'MinimumProjectSize': MinimumProjectSize,
                'Hourly Rate': hourly_rate,
                'Location': Location,
            }

            
            profile_link = provider.find('a', class_='directory_profile')
            if profile_link:
                provider_data['Profile URL'] = profile_link.get('href')
                link = provider_data['Profile URL']
                profile_url1 = link
                profile_url = 'https://clutch.co' + profile_url1
                if "#reviews" in profile_url:
                    profile_url2 = profile_url.split("#reviews")[0]
                    self.extract_detailed_info(profile_url2)
                else:
                    self.extract_detailed_info(profile_url)

            self.provider_data_list.append(provider_data)

    def extract_detailed_info(self, profile_url):
        response = requests.get(profile_url, headers=self.headers)
        if response.status_code == 200:
            page_content = response.text
            soup = BeautifulSoup(page_content, 'lxml')
            Info_list = soup.find("div", class_="profile-summary__text cropped-summary-text")

            if Info_list:
                try:
                    info_text = Info_list.find('p').text.strip()
                    self.detailed_info = info_text + '\n'
                except AttributeError:
                    pass  

            else:
                self.detailed_info = "No detailed information available"
            
            # if self.detailed_info not in self.detailed_info_list:
            self.detailed_info_list.append(self.detailed_info)

        with open('output.txt', 'w', encoding='utf-8') as file:
            for info in self.detailed_info_list:
                file.write(info.encode('utf-8').decode('latin-1') + "\n")

    def save_data(self):
        if self.provider_data_list:
            df_provider_info = pd.DataFrame(self.provider_data_list)
            df_provider_info.to_csv('provider_info.csv', index=False)

        if self.detailed_info_list:
            df_detailed_info = pd.DataFrame({'Detailed Info': self.detailed_info_list})
            df_detailed_info.to_csv('detailed_info.csv', index=False)

    def scrape_data(self, service, location):
        country = 'in'
        data_list = []

        url = f"https://clutch.co/{country}/{service.replace(' ','-').lower()}/{location.replace(' ','-').lower()}"

        for page in range(1,2): 
            response = requests.get(url,headers=self.headers)

            if response.status_code != 200:
                print("Response is not 200")
                break

            page_content = response.text
            self.extract_provider_info(page_content)

            self.save_data()
            time.sleep(5)

        if os.path.exists('provider_info.csv') and os.stat('provider_info.csv').st_size > 0:
            df_provider_info = pd.read_csv('provider_info.csv')
            df_detailed_info = pd.read_csv('detailed_info.csv')
            final_df = pd.concat([df_provider_info, df_detailed_info], axis=1)
            final_df.to_csv('final_data.csv', index=False)

        return







#_____________LinkedIn______________#

def get_headers_and_cookies():
    headers = {
    # 'authority': 'www.linkedin.com',
    # 'method': 'GET',
    # 'path': '/search/results/companies/?keywords=software%20development&origin=SWITCH_SEARCH_VERTICAL&sid=iAn',
    # 'scheme': 'https',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }

    return headers, cookies

def make_request2(link, cookies, headers):
    
    try:
        response = requests.get(link, cookies=cookies, headers=headers)
        raw_content = response.content
        return raw_content#['searchDashClustersByAll']['elements']
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def extract_company_data(link, cookies, headers):
    try:
        response = make_request2(link, cookies, headers)
        soup = BeautifulSoup(response, 'lxml')
        code_elements = soup.find_all('code')
        extracted_data_list = []
        industries = []
        linkedinUrl = link.replace("/about", "/")
        
        for element in code_elements:
            try:
                json_data_str = element.string.strip()
                json_data = json.loads(json_data_str)
            except:
                pass

            try:
                if json_data.get('included'):
                    data_part_list = json_data['included']
                    for data_part in data_part_list:
                        if data_part.get("url") == linkedinUrl:
                            try:
                                itype = '$type'
                                if data_part[itype] == 'com.linkedin.voyager.dash.identity.profile.IndustryV2':
                                    industries.append(data_part['name'])

                                grouped_locations = data_part.get("groupedLocations", [])
                                if grouped_locations:
                                    specialities = grouped_locations[0].get("specialities", [])
                                else:
                                    specialities = []

                                employee_count_range = data_part.get('employeeCountRange')
                                employee_count = data_part.get('employeeCount')
                                if data_part.get('employeeCount'):
                                    employee_count_range = data_part.get('employeeCountRange', {})
                                    employee_count = employee_count_range.get('start', None) if employee_count else None

                                founded_year_info = data_part.get("foundedOn")
                                if founded_year_info and isinstance(founded_year_info, dict):
                                    foundedYear = founded_year_info.get("year")
                                    if foundedYear and not isinstance(foundedYear, int):
                                        foundedYear = int(foundedYear)
                                else:
                                    foundedYear = None

                                specialities = data_part.get("specialities")

                                if not specialities and "groupedLocations" in data_part and data_part["groupedLocations"]:
                                    specialities = data_part["groupedLocations"][0].get("specialities")

                                try:
                                    headquarter_info = data_part.get('headquarter').get('address')
                                except:
                                    continue
                                company_url = data_part.get('websiteUrl')
                                callToAction = data_part.get('callToAction')

                                if callToAction and 'url' in callToAction:
                                    company_url = callToAction['url']

                                contant_number = None
                                if data_part.get("phone"):
                                    try:
                                        phone_info = data_part.get("phone").get("number")
                                        print(phone_info)
                                        contant_number = phone_info
                                    except:
                                        pass

                                address_info = {
                                    "country": headquarter_info.get("country"),
                                    "city": headquarter_info.get("city"),
                                    "geographicArea": headquarter_info.get("geographicArea"),
                                    "postalCode": headquarter_info.get("postalCode"),
                                    "line1": headquarter_info.get("line1"),
                                    "line2": headquarter_info.get("line2"),
                                }

                                extracted_data = {
                                    "company_name": data_part.get("name"),
                                    "description": data_part.get("description"),
                                    "linkedin_url": data_part.get("url"),
                                    "company_url": company_url,
                                    "contant_number": contant_number,
                                    "num_employees": employee_count,
                                    "company_size": employee_count,
                                    "headquarter": address_info,
                                    "company_type": data_part.get("type"),
                                    "founded_year": foundedYear,
                                    "specialities": data_part.get("specialities"),
                                    "industries": industries,
                                }

                                if any(value is not None for value in extracted_data.values()):
                                    # print(json.dumps({k: v for k, v in extracted_data.items() if v is not None}, indent=2))
                                    # logging.debug(json.dumps({k: v for k, v in extracted_data.items() if v is not None}, indent=2))
                                    extracted_data_list.append(extracted_data)
                            except Exception as e:
                                print("Exception: {e}")
                                pass
            except Exception as e:
                print("Exception: {e}")
                pass

        with open('linkedin_detailed_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data_list, json_file, ensure_ascii=False, indent=2)


        return extracted_data_list

    except Exception as e:
        print(f"Error extracting data: {e}")
        return []








#__________Extract Geo Codes__________#


def get_headers_and_cookies_location1():
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }

    return headers, cookies

def make_request1(key, filter,location, cookies, headers):
    try:
        response = requests.get(
            # f'https://api.linkedin.com/v2/geoTypeahead?q=India',
            # f'https://www.linkedin.com/search/results/companies/?companyHqGeo=["102713980"]&keywords=software development&origin=GLOBAL_SEARCH_HEADER&sid=KXy,', #geoTypeahead?q={location}
            f'https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{location},query:(typeaheadFilterQuery:(geoSearchTypes:List(MARKET_AREA,COUNTRY_REGION,ADMIN_DIVISION_1,CITY))),type:GEO)&queryId=voyagerSearchDashReusableTypeahead.23c9f700d1a32edbb7f6646dda5e7480',
            # f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:FACETED_SEARCH,query:(keywords:{key},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List(103644278)),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.11392247dc0905b4439815927dcdf04a&page={page}',
            # f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:FACETED_SEARCH,query:(keywords:{key},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List(103644278)),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.11392247dc0905b4439815927dcdf04a&page={page}',
            # f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{key},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List({filter})),(key:searchId,value:List(ecf51eb6-bd77-4915-90f2-a7aa8bda1cc4))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.994bf4e7d2173b92ccdb5935710c3c5d&page={page}',
            cookies=cookies,
            headers=headers
        )
        return response #.json()['data']['searchDashClustersByAll']['elements']
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def extract_location1(key, filter, location, cookies, headers):
    with open('location_codes.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Searched Keyword', 'Searched Location', 'Location Name', 'Geo Number']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            response = make_request1(key, filter, location, cookies, headers)

            if response and response.status_code == 200:
                json_data_str = response.content.strip()
                json_data = json.loads(json_data_str)

                for element in json_data['data']['searchDashReusableTypeaheadByType']['elements']:
                    tracking_urn = element.get('trackingUrn')
                    geo_data = element['target']['geo'] if element.get('target') and element['target'].get('geo') else None

                    if geo_data:
                        geo_number = geo_data['entityUrn'].split(':')[-1]
                        location_name = element.get('title', {}).get('text')

                        print("Tracking URN:", tracking_urn)
                        print("Geo Number:", geo_number)
                        print("Location Name:", location_name)
                        print()

                        writer.writerow({
                            'Searched Keyword': key,
                            'Searched Location': location,
                            'Location Name': location_name,
                            'Geo Number': geo_number
                        })








#_____________Scrap brief data____________#

def get_headers_and_cookies2():
    headers = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }

    return headers, cookies

def make_request2( start, key, location_code, cookies, headers):
    url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{key},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List({location_code})),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.cdde35dd1bbe30664513df622bcfad50'
    # print(url)
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        response_json = response.json()
        return response_json 

    except Exception as e:
        print(f"Error making request: {e}")

    return None, None

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }
def start_linkedin_search_scrape2(key, filter, total_results, headers, cookies):
        start = 0
        output = []
        json_output = json.dumps([])
        unique_entries = set()
        with open('/home/urbano-infotech/Documents/Flask Application P/location_codes.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                location_code = row['Geo Number']
                # print(f"Location Code: {location_code}")
                while start <= int(total_results):
                    response = make_request2(start, key, location_code, cookies, headers)

                    elements = response['data']['searchDashClustersByAll']['elements']
                    if response and "data" in response:
                        try:
                            for element in elements:  
                                items = element['items']
                                rootEntity = items 
                                for k in rootEntity:
                                    sub_items = k['item']
                                    if sub_items['entityResult'] is not None:
                                        entityResult = sub_items['entityResult']
                                        if entityResult:
                                            try:
                                                company_data = {}

                                                template_name = entityResult['template']
                                                company_data['Template_Name'] = template_name

                                                insightsResolutionResults_list = entityResult.get('insightsResolutionResults', [])
                                                if insightsResolutionResults_list:
                                                    simpleInsight_i = insightsResolutionResults_list[0].get('simpleInsight', {}).get('title', {}).get('attributesV2', [])
                                                    if simpleInsight_i:
                                                        company_name = simpleInsight_i[0]['detailData']['companyName']['name']
                                                        company_data['company_name'] = company_name

                                                title = entityResult['title']['text']
                                                company_data['title'] = title

                                                if 'primarySubtitle' in entityResult and 'text' in entityResult['primarySubtitle']:
                                                    ServicesAndLocation = entityResult['primarySubtitle']['text']
                                                    company_data['ServicesAndLocation'] = ServicesAndLocation
                                                else:
                                                    company_data['ServicesAndLocation'] = None

                                                if 'summary' in entityResult and 'text' in entityResult['summary']:
                                                    Description = entityResult['summary']['text']
                                                    company_data['company_description'] = Description
                                                else:
                                                    company_data['company_description'] = None

                                                # company_data['Company_URN'] = entityResult['lazyLoadedActions']['entityUrn'] if 'lazyLoadedActions' in entityResult and 'entityUrn' in entityResult['lazyLoadedActions'] else None

                                                company_data['Followers'] = entityResult['secondarySubtitle']['text'] if 'secondarySubtitle' in entityResult and 'text' in entityResult['secondarySubtitle'] else None

                                                company_data['Navigation_URL'] = entityResult['navigationUrl'] if 'navigationUrl' in entityResult else None

                                                entry_key = tuple(company_data.items())
                                                if entry_key not in unique_entries:
                                                    output.append(company_data)
                                                    unique_entries.add(entry_key)

                                                json_output = json.dumps(output, indent=2)
                                                
                                            except Exception as e:
                                                print(f"Error extracting data: {e}")

                            start += 1
                        except Exception as e:
                            print(f"Error processing response: {e}")

            # json_output = json.dumps(output, indent=2)
            with open('new_Company_Data.json', 'w', encoding='utf-8') as f:
                f.write(json_output)


keywords_list = []
location_list = []






#_________________Get Geo Codes_________________________#

def make_requests(start, key, location_code, cookies, headers):
    url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{key},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:companyHqGeo,value:List({location_code})),(key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.cdde35dd1bbe30664513df622bcfad50'
    # print(url)
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        response_json = response.json()
        return response_json 

    except Exception as e:
        print(f"Error making request: {e}")

    return None, None

@flask_app.route('/codes', methods=['GET', 'POST'])
def get_geo_codes():
    if request.method == 'POST':
        key = request.form.get('keywords')
        location = request.form.get('location')
        keywords_list.append(key)
        location_list.append(location)
        headers, cookies = get_headers_and_cookies_location1()
        filter = 'COMPANIES'
        extract_location1(key, filter, location, cookies, headers)
        start = 0
        output = []
        json_output = json.dumps([])
        unique_entries = set()
        with open('/home/urbano-infotech/Documents/Flask Application P/location_codes.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                location_code = row['Geo Number']
                # print(f"Location Code: {location_code}")
                while start <= int(2):
                    response = make_requests(start, key, location_code, cookies, headers)

                    elements = response['data']['searchDashClustersByAll']['elements']
                    if response and "data" in response:
                        try:
                            for element in elements:                            
                                items = element['items']
                                rootEntity = items 
                                for k in rootEntity:
                                    sub_items = k['item']
                                    if sub_items['entityResult'] is not None:
                                        entityResult = sub_items['entityResult']
                                        if entityResult:
                                            try:
                                                company_data = {}

                                                template_name = entityResult['template']
                                                company_data['Template_Name'] = template_name

                                                insightsResolutionResults_list = entityResult.get('insightsResolutionResults', [])
                                                if insightsResolutionResults_list:
                                                    simpleInsight_i = insightsResolutionResults_list[0].get('simpleInsight', {}).get('title', {}).get('attributesV2', [])
                                                    if simpleInsight_i:
                                                        company_name = simpleInsight_i[0]['detailData']['companyName']['name']
                                                        company_data['company_name'] = company_name

                                                title = entityResult['title']['text']
                                                company_data['title'] = title

                                                if 'primarySubtitle' in entityResult and 'text' in entityResult['primarySubtitle']:
                                                    ServicesAndLocation = entityResult['primarySubtitle']['text']
                                                    company_data['ServicesAndLocation'] = ServicesAndLocation
                                                else:
                                                    company_data['ServicesAndLocation'] = None

                                                if 'summary' in entityResult and 'text' in entityResult['summary']:
                                                    Description = entityResult['summary']['text']
                                                    company_data['company_description'] = Description
                                                else:
                                                    company_data['company_description'] = None

                                                # company_data['Company_URN'] = entityResult['lazyLoadedActions']['entityUrn'] if 'lazyLoadedActions' in entityResult and 'entityUrn' in entityResult['lazyLoadedActions'] else None

                                                company_data['Followers'] = entityResult['secondarySubtitle']['text'] if 'secondarySubtitle' in entityResult and 'text' in entityResult['secondarySubtitle'] else None

                                                company_data['Navigation_URL'] = entityResult['navigationUrl'] if 'navigationUrl' in entityResult else None

                                                entry_key = tuple(company_data.items())
                                                if entry_key not in unique_entries:
                                                    output.append(company_data)
                                                    unique_entries.add(entry_key)

                                                json_output = json.dumps(output, indent=2)
                                                
                                            except Exception as e:
                                                print(f"Error extracting data: {e}")

                            start += 1
                        except Exception as e:
                            print(f"Error processing response: {e}")

            # json_output = json.dumps(output, indent=2)

            with open('new_Company_Data.json', 'w', encoding='utf-8') as f:
                f.write(json_output)
            
        with open('new_Company_Data.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        get_company_data()

        data = json_data if isinstance(json_data, list) else [json_data]
        
        return render_template('index.html')

    return render_template('get_geo_codes.html')




#_________________Scrape LinkedIn_________________________#

@flask_app.route('/scrape', methods=['GET', 'POST'])
def linkedin_scrape():
    if request.method == 'POST':
        try:
            # linkedin_scraper = LinkedInScrapperBrief()

            keywords = keywords_list[0]#request.form['keywords']
            total_results = request.form.get('totalResults')
            location = location_list[0]
            print(location)
            print(keywords)
            headers, cookies = get_headers_and_cookies_location1()
            start_linkedin_search_scrape2(keywords, 'COMPANIES', total_results, headers, cookies)
            time.sleep(1)

            with open('new_Company_Data.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            # pdb.set_trace()
            data = json_data if isinstance(json_data, list) else [json_data]
    
            for item in data:
                company_data = CompanyData(
                    template_name=item['Template_Name'],
                    title=item['title'],
                    services_and_location=item['ServicesAndLocation'],
                    company_description=item['company_description'],
                    followers=item['Followers'],
                    navigation_url=item['Navigation_URL']
                )
                db.session.add(company_data)

            db.session.commit()

            return render_template('index.html', message='Data saved successfully!', data=data)
        except Exception as e:
            flask_app.logger.error(f'Error: {e}')
            return render_template('index.html', message=f'Error: {e}')

    return render_template('index.html')







linkedin_urls = []

#_________________Extract Detailed Data__________________#

def get_headers_and_cookies():
    headers = {
    # 'authority': 'www.linkedin.com',
    # 'method': 'GET',
    # 'path': '/search/results/companies/?keywords=software%20development&origin=SWITCH_SEARCH_VERTICAL&sid=iAn',
    # 'scheme': 'https',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }

    return headers, cookies

def make_requestz(link, cookies, headers):
    
    try:
        response = requests.get(link, cookies=cookies, headers=headers)
        raw_content = response.content
        return raw_content#['searchDashClustersByAll']['elements']
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def extract_company_data(link, cookies, headers):
    try:
        response = make_requestz(link, cookies, headers)
        soup = BeautifulSoup(response, 'lxml')
        code_elements = soup.find_all('code')
        extracted_data_list = []
        industries = []
        linkedinUrl = link.replace("/about", "/")
        
        for element in code_elements:
            try:
                json_data_str = element.string.strip()
                json_data = json.loads(json_data_str)
            except:
                pass

            try:
                if json_data.get('included'):
                    data_part_list = json_data['included']
                    for data_part in data_part_list:
                        if data_part.get("url") == linkedinUrl:
                            try:
                                itype = '$type'
                                if data_part[itype] == 'com.linkedin.voyager.dash.identity.profile.IndustryV2':
                                    industries.append(data_part['name'])

                                grouped_locations = data_part.get("groupedLocations", [])
                                if grouped_locations:
                                    specialities = grouped_locations[0].get("specialities", [])
                                else:
                                    specialities = []

                                employee_count_range = data_part.get('employeeCountRange')
                                employee_count = data_part.get('employeeCount')
                                if data_part.get('employeeCount'):
                                    employee_count_range = data_part.get('employeeCountRange', {})
                                    employee_count = employee_count_range.get('start', None) if employee_count else None

                                founded_year_info = data_part.get("foundedOn")
                                if founded_year_info and isinstance(founded_year_info, dict):
                                    foundedYear = founded_year_info.get("year")
                                    if foundedYear and not isinstance(foundedYear, int):
                                        foundedYear = int(foundedYear)
                                else:
                                    foundedYear = None

                                specialities = data_part.get("specialities")

                                if not specialities and "groupedLocations" in data_part and data_part["groupedLocations"]:
                                    specialities = data_part["groupedLocations"][0].get("specialities")

                                try:
                                    headquarter_info = data_part.get('headquarter').get('address')
                                except:
                                    continue
                                company_url = data_part.get('websiteUrl')
                                callToAction = data_part.get('callToAction')

                                if callToAction and 'url' in callToAction:
                                    company_url = callToAction['url']

                                contant_number = None
                                if data_part.get("phone"):
                                    try:
                                        phone_info = data_part.get("phone").get("number")
                                        print(phone_info)
                                        contant_number = phone_info
                                    except:
                                        pass

                                address_info = {
                                    "country": headquarter_info.get("country"),
                                    "city": headquarter_info.get("city"),
                                    "geographicArea": headquarter_info.get("geographicArea"),
                                    "postalCode": headquarter_info.get("postalCode"),
                                    "line1": headquarter_info.get("line1"),
                                    "line2": headquarter_info.get("line2"),
                                }

                                extracted_data = {
                                    "company_name": data_part.get("name"),
                                    "description": data_part.get("description"),
                                    "linkedin_url": data_part.get("url"),
                                    "company_url": company_url,
                                    "contant_number": contant_number,
                                    "num_employees": employee_count,
                                    "company_size": employee_count,
                                    "headquarter": address_info,
                                    "company_type": data_part.get("type"),
                                    "founded_year": foundedYear,
                                    "specialities": data_part.get("specialities"),
                                    "industries": industries,
                                }

                                if any(value is not None for value in extracted_data.values()):
                                    # print(json.dumps({k: v for k, v in extracted_data.items() if v is not None}, indent=2))
                                    # logging.debug(json.dumps({k: v for k, v in extracted_data.items() if v is not None}, indent=2))
                                    extracted_data_list.append(extracted_data)
                            except Exception as e:
                                print("Exception: {e}")
                                pass
            except Exception as e:
                print("Exception: {e}")
                pass

        with open('linkedin_detailed_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data_list, json_file, ensure_ascii=False, indent=2)


        return extracted_data_list

    except Exception as e:
        print(f"Error extracting data: {e}")
        return []


@flask_app.route('/detailed_data', methods = ['GET','POST'])
def detailed_data():
    # pdb.set_trace()
    with open('Company_links.json', 'r', encoding='utf-8') as f:
        links_about = json.load(f)

    page_number = 1
    # headers, cookies = get_headers_and_cookies()
    all_extracted_data = []

    for link in links_about:
        print(f"\nExtracting data for {link}")
        extracted_data = extract_company_data(link, cookies, headers)
        if extracted_data:
            all_extracted_data.extend(extracted_data)

    with open('linkedin_detailed_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_extracted_data, json_file, ensure_ascii=False, indent=2)

    time.sleep(1)
    with open('linkedin_detailed_data.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    # db.session.query(LinkedInDetailedData).all()
    data = json_data if isinstance(json_data, list) else [json_data]
    try:
        for item in data:
            try:
                linkedin_detailed_data = LinkedInDetailedData(
                company_name=item['company_name'],
                description=item['description'],
                linkedin_url=item['linkedin_url'],
                company_url=item['company_url'],
                contact_number=item['contant_number'],
                num_employees=item['num_employees'],
                company_size=item['company_size'],
                headquarter_country=item['headquarter']['country'],
                headquarter_city=item['headquarter']['city'],
                headquarter_geographic_area=item['headquarter']['geographicArea'],
                headquarter_postal_code=item['headquarter']['postalCode'],
                headquarter_line1=item['headquarter']['line1'],
                headquarter_line2=item['headquarter']['line2'],
                company_type=item['company_type'],
                founded_year=item['founded_year'],
                specialities=item['specialities'],
                industries=item['industries'],
            )


                db.session.add(linkedin_detailed_data)
            except Exception as e:
                print(e)
        
        db.session.commit()
    except Exception as e:
        print('Exception : ',{e})

    return render_template('index.html')








#__________________Extract Links to Scrape______________________#
headers, cookies = get_headers_and_cookies2()
def make_request4(start,page, keywords, filter,headers, cookies):
    try:
        
        response = requests.get(
            f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{start},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{keywords},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List({filter})),(key:searchId,value:List(ecf51eb6-bd77-4915-90f2-a7aa8bda1cc4))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.994bf4e7d2173b92ccdb5935710c3c5d&page={page}',
            cookies=cookies,
            headers=headers
        )
        return response.json()['data']['searchDashClustersByAll']['elements']
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def extract_company_links(element):
    output = []
    rootEntity = element['items']
    for k in rootEntity:
        sub_items = k['item']
        if sub_items['entityResult'] is not None:
            entityResult = sub_items['entityResult']
            if entityResult:
                try:
                    Navigation_URL = entityResult['navigationUrl']
                    output.append({'Navigation_URL':Navigation_URL})
                except:
                    print('pass')
                    pass
    return output



def get_company_data():
    total_pages = 1
    # location = 'Paris'
    keywords = keywords_list#'Python Development'
    headers = {

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'csrf-token':'ajax:5422946553201053416',
    # 'Cookie': 'bcookie="v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad"; bscookie="v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM"; li_sugr=2fabd575-8467-40da-a417-c7fc75f2dc87; _gcl_au=1.1.1838768317.1700242109; aam_uuid=05546742905391860331534170237901243902; timezone=Asia/Calcutta; li_theme=light; li_theme_set=app; _guid=03f33cf2-753e-4a6e-bdbd-909fe3e5df55; li_rm=AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak; visit=v=1&M; liveagent_oref=https://www.linkedin.com/help/lms/answer/a424655; liveagent_vc=1; _uetvid=b99df460856e11eeb8b3d545613e8574; li_gc=MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==; li_alerts=e30=; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19686%7CMCMID%7C05397880909880168261550743019175966261%7CMCAAMLH-1701465611%7C12%7CMCAAMB-1701465611%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1700868011s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-2079391624; fcookie=AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==; g_state={"i_l":1,"i_p":1701350644941}; liap=true; li_at=AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p; JSESSIONID="ajax:5422946553201053416"; AnalyticsSyncHistory=AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ; lang=v=2&lang=en-us; fid=AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ; UserMatchHistory=AQLc85huLpwRLAAAAYw0k7sB4kAjYs3TR7O3tk0R7iWW7CIUu7nMOWh2QJ9ChwG-farpJ4pkcZLkTQ; lms_ads=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lms_analytics=AQEuID_pqUL31QAAAYw0k7weW7YsWN0NKU7zce-dy4tQlS1TRKA6S1aUDgQ3x9f8tH6GkrzEVrksxl_bPp-_orf5EZ9ebDdZ; lidc="b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701690350:t=1701691006:v=2:sig=AQFMTAxmKfKOyPNjLdnI8agrWpAol8YV"',
    'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Linux"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    cookies = {
    'bcookie': 'v=2&d41721f1-5bd9-41af-84c5-f4ea2965cdad',
    'bscookie': 'v=1&20231117162156ca611971-766d-430c-8f33-b97b552dce56AQE871YEYBFqqAx7Shj_KGPEvRVgsYbM',
    'li_sugr': '2fabd575-8467-40da-a417-c7fc75f2dc87',
    '_gcl_au': '1.1.1838768317.1700242109',
    'aam_uuid': '05546742905391860331534170237901243902',
    'timezone': 'Asia/Calcutta',
    'li_theme': 'light',
    'li_theme_set': 'app',
    '_guid': '03f33cf2-753e-4a6e-bdbd-909fe3e5df55',
    'li_rm': 'AQF4uveMJQowXgAAAYviHbRU4MK8I8AlYlGCZpYhvTxqvTkoH5vmv0u85uK_V-cbnodIVkFW7y7qdJKZ3z_9gCZ-zmWmIPkVU6d_wnrcL0kOmI_lqRZ-LtUOnIEcLjQeiYpb-_IF1h_ptS1j5JXxfn959jFRr2MJb9wsy9RxJMQ1L5Squ22I6QRPzPVjtlVrpJfGDCKsangpT86L_I2gynkaeic0DtTsxQFA2OiWgBPEWVGqxHqOFxwXA2NhqDk8VFcg6pCZZmqnVvapNPM8FUBTGhH6ZEAXetkVvXUBcpAeGcSXL3fE2q06ips7VEajsDPPaq5RCOjZNtgSDak',
    'visit': 'v=1&M',
    'liveagent_oref': 'https://www.linkedin.com/help/lms/answer/a424655',
    'liveagent_vc': '1',
    '_uetvid': 'b99df460856e11eeb8b3d545613e8574',
    'li_gc': 'MTswOzE3MDA4NTg5MTE7MjswMjFld30zZ0/4rqbHVwH4jKI8eo4amju6eUU0/9+tfZGW0A==',
    'li_alerts': 'e30=',
    'AMCV_14215E3D5995C57C0A495C55@AdobeOrg': '-637568504|MCIDTS|19686|MCMID|05397880909880168261550743019175966261|MCAAMLH-1701465611|12|MCAAMB-1701465611|6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y|MCOPTOUT-1700868011s|NONE|vVersion|5.1.1|MCCIDH|-2079391624',
    'fcookie': 'AQEDVJoy9akE3AAAAYwfLcb6Fz2e26_Sy4IPKpI14CouMfZXbVhTlfF6ZFVp4x68a3wzj0nUsrJ3nsMJ35vT686nv_NKoHJSu_ZdxNJ5mfCQT8Hz_IoNpylr1gqBRMEQdQ0cxJEJuJqbh7zQyYMvk8nIPc_ZAvJfU53DRyk6cPa4RyEFEc0S73y6xdSioS9MonknXR86fX3U6Eb4xrxl6mq7zOqnrPbxdiFsQANJG_f-Hym1iQjgt9U3RR9kT5ouCzc03pqQeJgNps/H3f+MiqvVX+Ig8d6cmkUTghn7KfxK05VVDX6tOM73uBRECLqg8ii3QU4ur7wfiOY8y/YUAg==',
    'g_state': '{"i_l":1,"i_p":1701350644941}',
    'liap': 'true',
    'li_at': 'AQEDATsd36oELHB7AAABjClL6GIAAAGMTVhsYk0AVpnMXH9blLajt8Gb1p862txHqdshAs3JLomxv23hPAxQ2glT4dFiC-0HWL_OENrX5bRWiD-i2mD5jQoJ54-yAjVmnYgymBHlFubUfrgJk7vccP6p',
    'JSESSIONID': 'ajax:5422946553201053416',
    'AnalyticsSyncHistory': 'AQKqymSAg51xeAAAAYwzR87xxydvFF1mX3wPbeugmC8e_VF78-2cU5G5JFJiIK0Kgn_Sx9nInkEgT2dHyNwGpQ',
    'lang': 'v=2&lang=en-us',
    'fid': 'AQFgRKDlvyTwCAAAAYwzviuZuCFxn8zGCXhv6LnWsxUSOETaOQN5iqS6w2jmHvI8JBzVXi6TgltFAQ',
    'UserMatchHistory': 'AQJotdFVUkuOugAAAYw0hd9f75tOYpfsLiTpUZolfhZBDI_-p2drPD696cMBxcPsSu0AzdgMvEySSA',
    'lms_ads': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lms_analytics': 'AQEcQ9EVkJ36SgAAAYw0heCE20TOBePxZlwIZT0EGrr1da4ja304lf194vaeXulBe1Veb-_oFn-8ugmGgxINg6esjWACwuSL',
    'lidc': 'b=OB46:s=O:r=O:a=O:p=O:g=4546:u=369:x=1:i=1701688240:t=1701692172:v=2:sig=AQHFE_RmC4BjEKNMNGsrYx8dROgChT9C'
    }
    links_about_list = []
    merged_dicts = []

    links_about = set()
    filter = 'COMPANIES'
    
    for page in range(1, total_pages + 1):
        start = (page - 1) * 10  
        elements = make_request4(start,page, keywords, filter,headers, cookies)

        if elements:
            for element in elements:
                output = extract_company_links(element)

                for z in output:
                    merged_dicts.append(z)

                    company_link = z.get('Navigation_URL')
                    print(company_link)
                    if company_link:
                        links_about.add(company_link + 'about')
    
        links_about_list = list(links_about)
        
        with open('Company_links.json', 'w', encoding='utf-8') as f:
            json.dump(links_about_list, f, indent=2)

    return jsonify({'success': True, 'links_about_list': links_about_list})


@flask_app.route('/', methods = ['GET', 'POST'])
def hello_world():
    return render_template('homepage.html')



@flask_app.route('/clutch', methods=['GET', 'POST'])
def display_clutch_data():
    if request.method == 'POST':
        service = request.form.get('service')
        location = request.form.get('location')

        a_obj = WebScrapp()
        a_obj.scrape_data(service, location)  
        df = pd.read_csv('clutchData.csv')
        data = df.to_dict(orient='records')
        try:
            with open('/home/urbano-infotech/Downloads/leadGeneration/Scripts1/Flask Project/clutchData.csv', 'r', encoding='utf-8') as csv_file:
                data_1 = csv.DictReader(csv_file)
                
                for row in data_1:
                    # pdb.set_trace()
                    clutch_data = Clutch(
                        name=row['Name'],
                        description=row['Description'],
                        rating=float(row['Rating']),
                        reviews=row['Reviews'],
                        minimum_project_size=row['MinimumProjectSize'],
                        hourly_rate=row['Hourly Rate'],
                        location=row['Location'],
                        profile_url=row['Profile URL'],
                        detailed_info=row['Detailed Info']
                    )
                    
                    db.session.add(clutch_data)

                db.session.commit()
                
                return render_template('clutch_template.html', data=data)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return "Error importing Clutch data"
            # print(data)
        
    else:
        return render_template('clutch_template.html')


if __name__ == '__main__':
    flask_app.run(debug=True)


