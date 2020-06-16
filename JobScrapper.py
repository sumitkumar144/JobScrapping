import os
from lib2to3.pgen2 import driver
import urllib
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
#import requests
from bs4 import BeautifulSoup as bs
#from urllib.request import urlopen as uReq
from selenium import webdriver

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/jobscrap', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            jobString = request.form['jobstring'].split(' ')
            joinJobString = '-'.join(jobString)
            location = 'in-'+request.form['location']
            getvars={'Sort': 2}
            totaljobs_url = 'https://www.totaljobs.com/jobs'+ '/' + joinJobString + '/' + location + '?' + urllib.parse.urlencode(getvars)
            chrome_options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get(totaljobs_url)
            driver.implicitly_wait(30)
            source = driver.page_source
            html = bs(source, "html.parser")
            bigboxes = html.findAll("div", {"class": "col-sm-12"})
            del bigboxes[0:3]
            filename = joinJobString + ".csv"
            fw = open(filename, "w")
            headers = "Job Title, Company Name, Job Location, Job Posting Time, Job Link \n"
            fw.write(headers)
            job_details=[]
            job_details = []
            for bigbox in bigboxes:
                try:
                    job_title = bigbox.find("div", {"class": "job-title"}).a.text.strip()

                except:
                    job_title = "No Title"

                try:
                    company_name = bigbox.find_all("div", {"class": "col-xs-12"})[1].ul.find("li", {
                        "class": "company"}).h3.a.text

                except:
                    company_name = "No Company Name"

                if company_name == "No Company Name":
                    try:
                        company_name = bigbox.find("div", {"class": "col-xs-7 col-sm-8"}).ul.find("li", {
                            "class": "company"}).h3.a.text
                    except:
                        company_name = "No Company Name"

                try:
                    job_link = bigbox.find("div", {"class": "job-title"}).a['href']

                except:
                    job_link = "No Job Link"

                try:
                    job_location = bigbox.find("div", {"class": "detail-body"}).div.div.ul.li.span.a.text

                except:
                    job_location = "No Job Location"

                if job_location == "No Job Location":
                    try:
                        job_location = bigbox.find("div", {"class": "detail-body"}).div.div.ul.li.span.text.strip()
                    except:
                        job_location = "No Job Location"

                try:
                    job_posting_time = bigbox.find("li", {"class": "date-posted"}).span.text.strip()

                except:
                    job_posting_time = "No Job Posting Time"

                mydict = {"Job Link": job_link, "Job Title": job_title, "Company Name": company_name,
                          "Job Location": job_location, "Job Posting Time": job_posting_time}

                job_details.append(mydict)
                keyValList = ["No Job Link"]
                Total_Jobs = list(filter(lambda x: x['Job Link'] not in keyValList, job_details))
            return render_template('results.html', Total_Jobs=Total_Jobs[0:(len(Total_Jobs) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'

    else:
        return render_template('index.html')

port = int(os.getenv("PORT"))
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    app.run(host='0.0.0.0', port=port)
    #app.run(host='127.0.0.1', port=8001, debug=True)