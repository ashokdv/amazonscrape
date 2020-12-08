from bs4 import BeautifulSoup # BeautifulSoup is in bs4 package 
import requests
from flask import Flask,request ,jsonify
import uuid ,json
from pyshorteners import Shortener 
  


app = Flask(__name__)   
@app.route('/') 
def home():
    return "<h1>Welcome to our server !!</h1>"
#    return render_template("home.html")


@app.route('/users',methods=['POST'])
def users():
      


    usercontent = request.get_json()
    if usercontent is None:
        name = request.form['name']
        URL = request.form['URL']
        mobilenumber = request.form['mobilenumber']
        yourprice = request.form['yourprice']
    else:
        name = usercontent['name']
        URL = usercontent['URL']
        mobilenumber = usercontent['mobilenumber']
        yourprice = usercontent['yourprice']
    uuid_user = uuid.uuid1()
    product_details = json.loads(sampletrigger(URL))

    linkRequest = {"destination": URL, "domain": { "fullName": "rebrand.ly" }}
    requestHeaders = {"Content-type": "application/json","apikey": "5c0a9490877942ecb3538236c7ec3ee6"}

    try:
        r = requests.post("https://api.rebrandly.com/v1/links", data = json.dumps(linkRequest),headers=requestHeaders)
        if (r.status_code == requests.codes.ok):
            link = r.json()
            short_url = link["shortUrl"]
    except Exception as e:
        print(e)
    
    

    def write_json(data, filename='users.json'): 
        with open(filename,'w') as f: 
            json.dump(data, f, indent=4) 
    
    with open('users.json') as json_file: 
        data = json.load(json_file) 
        temp = data['users'] 
  
        # python object to be appended 
        y = {
            "name" : name,
            "title" : product_details['title'],
            "URL" : URL,
            "mobilenumber" : mobilenumber,
            "yourprice" : yourprice,
            "UUID": str(uuid_user),
            "subscribe": "Y",
            "actual_price":product_details['ourprice'],
            "deal_price":product_details['dealprice'],
            "sale_price":product_details['saleprice'],
            "stock":product_details['stock'],
            "short_url":short_url

            } 
        temp.append(y) 
        
    write_json(data)
    # print ("SHORT URL is {}".format(url_shortener.short(url))) 

    message = "Hi "+ name + " , You have subscribed to a Product  "+ product_details['title'] + " .Thanks for your subscription. Your product id is "+str(uuid_user)
    sms = sms_trigger(message,mobilenumber)
    return "Thanks for the subscription"
    # return render_template("subscribe.html")


        

def sampletrigger(URL):
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})

    URL = URL
    content = requests.get(URL , headers= HEADERS)
    soup = BeautifulSoup(content.text, 'lxml')
    try:
        title = soup.find(id='productTitle').get_text().strip()
    except Exception as e:
        title = 'Not found'
    # print(title)
   
    if len(title) > 100:
        title = title[0:70]

    try:
        try:
            ourprice = float(soup.find(id='priceblock_ourprice').get_text().replace('₹','').replace(',','').strip())
            print(ourprice)
        except Exception as e :
            print(e)
            ourprice = 0

        try:
            dealprice = float(soup.find(id='priceblock_dealprice').get_text().replace('₹','').replace(',','').strip())
            print(dealprice)
        except Exception as e:
            print(e)
            dealprice = 0

        try:
            saleprice = float(soup.find(id='priceblock_saleprice').get_text().replace('₹','').replace(',','').strip())
            print(saleprice)
        except Exception as e:
            print(e)
            saleprice = 0
                
        if ourprice == 0 and dealprice == 0 and saleprice ==0 :
            msg = 'Unable to load product'
        
                    
    except Exception as e:
        print(e)


    try:
        soup.select('#availability .a-color-state')[0].get_text().strip()
        print(soup.select('#availability .a-color-state')[0].get_text().strip())
        stock = 'Out of Stock'
    except:
        stock = 'Available'

    # print(stock)
    return json.dumps({'ourprice':ourprice,"dealprice":dealprice,"saleprice":saleprice,'title':title,'stock':stock})

def sms_trigger(message,number):
    print('----------------',message)
    print('---------------',number)
    url = "https://www.fast2sms.com/dev/bulk"


    # create a dictionary
    my_data = {
    	'sender_id': 'FSTSMS',
    	'message': message,
    	'language': 'unicode',
    	'route': 'p',
    	'numbers': number
    }

    # create a dictionary
    headers = {
    	'authorization': 'bh4NsVrzJa9vQjZFHWlx36PoOqefnGBw7pmTdY8t1uIK0XCS5DUrQCk9N1hxmMtyKAwoa540VZfzWOnX',
    	'Content-Type': "application/x-www-form-urlencoded",
    	'Cache-Control': "no-cache"
    }

    response = requests.request("POST",
                                url,
                                data = my_data,
                                headers = headers)
    # load json data from source
    returned_msg = json.loads(response.text)

    # print the send message
    print(returned_msg['message'])
    return returned_msg['message']


    
@app.route('/alert-sms',methods=['POST'])
def alerts():
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    with open('users.json') as f:
        data = json.load(f)


    # print(data['users'][1])
    for users in data['users']:
        # print(users)

        # for product_details in users:
        print(users['URL'])
        print(users['yourprice'])
        content = requests.get(users['URL'] , headers= HEADERS)
        soup = BeautifulSoup(content.text, 'lxml')

        try:
            try:
                ourprice = float(soup.find(id='priceblock_ourprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                ourprice = 0    
            try:
                dealprice = float(soup.find(id='priceblock_dealprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                dealprice = 0
            try:
                saleprice = float(soup.find(id='priceblock_saleprice').get_text().replace('₹','').replace(",",'').strip())
            except:
                saleprice = 0

            print('--------ourprice-------',ourprice)
            print('--------dealprice-------',dealprice)
            print('--------saleprice-------',type(saleprice))

            print('-----------Oldourprice----',users['actual_price'])
            print('--------olddealprice-------',users['deal_price'])
            print('--------oldsaleprice-------',users['sale_price'])


            if ourprice == 0 and dealprice == 0 and saleprice==0:
                msg = 'Unable to load product'
            
        except Exception as e:
            print(e)

        message = "Hi "+ users['name'] + " , Your subscription Product  "+ users['title'] + " is available at lower price,  "


        try:
            soup.select('#availability .a-color-state')[0].get_text().strip()
            stock = 'Out of Stock'
        except:
            stock = 'Available On Stock'
        # if (int(saleprice)!=0):
        #     print("true")
        # el
            
        # if (int(ourprice) <= int(users['yourprice']))  or (int(saleprice) <= int(users['yourprice']))   or (int(dealprice) <= int(users['yourprice'])) :
        
        if dealprice > 0 and ( dealprice < users['deal_price'] or dealprice < users['sale_price'] or dealprice < users['actual_price']) :
            message = message + 'Price : '+str(dealprice) + ". Product is "+stock +".Deal is Available on this  Product"+ "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])


        elif saleprice > 0 and ( saleprice < users['deal_price'] or saleprice < users['sale_price'] or saleprice < users['actual_price']):
            message = message + 'Price : '+str(saleprice) + ". Product is "+stock +". Sale is going on." + "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])

        elif ourprice > 0 and ( ourprice < users['deal_price'] or ourprice < users['sale_price'] or ourprice < users['actual_price']):
            message = message + 'Price : '+str(ourprice) + ". Product is "+stock +". No Deal Available and Not on sale.  " + "link:" + users['short_url']
            sms = sms_trigger(message,users['mobilenumber'])

        else :
            pass

        # elif  int(saleprice) > 0 and  (int(saleprice) <= int(users['yourprice'])) :
        #     print("--------------IF--LO IF----------------")

        #     message = message + 'Saleprice : '+str(saleprice) + "Product is "+stock
        #     print("--------------IF--LO elIF----------------")
    
        #     sms = sms_trigger(message,users['mobilenumber'])

        # elif int(dealprice) > 0 and (int(dealprice) <= int(users['yourprice'])) :
        #     print("--------------IF--LO elIF----------------")

        #     message = message + 'Dealprice : '+str(dealprice) + "Product is "+stock

        #     sms = sms_trigger(message,users['mobilenumber'])

        # elif int(ourprice) > 0 and (int(ourprice) <= int(users['yourprice'])) :
        #     print("--------------IF--LO elIF----------------")

        #     print("------------Your price-------------",users['yourprice'])
        #     message = message + 'Actual MRP : '+str(ourprice) + " .Product is "+stock
        #     sms = sms_trigger(message,users['mobilenumber'])
        # # else:
        # #     print("--------------IF--LO else---------------")

        # #     # pass
            
        # elif (int(saleprice) != 0):
        #     print("--------------IF--LO elIF-1---------------")
            

        #     if  saleprice <= users["actual_price"] or saleprice <= users["sale_price"] or saleprice <= users["deal_price"]:
        #         message = message + 'Price : '+ str(saleprice) + ".On Sale" + "Product is "+stock
        #         sms = sms_trigger(message,users['mobilenumber'])

        # elif dealprice != 0 :
        #     print("--------------IF--LO elIF-2---------------")

        #     if  dealprice <= users["actual_price"] or dealprice <= users["sale_price"] or dealprice <= users["deal_price"]:
        #         message = message + 'Price : '+ str(dealprice) + ". Deal Available" + "Product is "+stock    
        #         sms = sms_trigger(message,users['mobilenumber'])
     
        # elif ourprice != 0 :
        #     print("--------------IF--LO elIF-3---------------")

        #     if  ourprice <= users["actual_price"] or ourprice <= users["sale_price"] or ourprice <= users["deal_price"]:
        #         message = message + 'Price : '+ str(ourprice) + "No Deal Available or Not in Sale" + "Product is "+stock
        #         sms = sms_trigger(message,users['mobilenumber'])
                

        # else:
        #     print("--------------IF--LO elIF-3---------------")

        #     if dealprice >=0 :
        #         # Amazon offered a deal 
        #         #trigger-sms()
        #         pass
        #     elif saleprice >= 0:
        #         # Sale is going on this product
        #         #trigger-sms()
        #         pass
        #     else:
        #         pass
        
        
        
       
    return "Sms triggered"





















# @app.route('/trigger-sms',methods=['POST'])
# def trigger():     
#     HEADERS = ({'User-Agent':
#                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
#                 'Accept-Language': 'en-US, en;q=0.5'})

#     URL = "https://www.amazon.in/Purifier-Active-Copper-PRIMIUM-Quality/dp/B08DP5VCPQ/ref=sr_1_1_sspa?dchild=1&pd_rd_r=50379ee9-9534-4616-9cd4-edb916bf991e&pd_rd_w=Ma6VB&pd_rd_wg=KMqfo&pf_rd_p=47bc7ca3-6922-4837-a66e-7c6588edc2c1&pf_rd_r=1YTATD1XX8NMT89NGTWA&qid=1607269488&refinements=p_72%3A1318477031&s=kitchen&sr=1-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyT0NGV08zVkJHR1g4JmVuY3J5cHRlZElkPUEwNzUyNzQwR0JTNjRRN1hFTUQ2JmVuY3J5cHRlZEFkSWQ9QTEwMjYzNzYyVTlYWExBUVVWVlpGJndpZGdldE5hbWU9c3BfYXRmX2Jyb3dzZSZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU="
#     content = requests.get(URL , headers= HEADERS)
#     soup = BeautifulSoup(content.text, 'lxml')
#     # print(soup)

#     title = soup.find(id='productTitle').get_text().strip()
#     # print(len(title))
#     if len(title) > 100:
#         title = title[0:100]
#         print(title)
#     try:
#         # price = float(soup.find(id='priceblock_ourprice').get_text().replace('.', '').replace('€', '').replace(',', '.').strip())
#         ourprice = soup.find(id='priceblock_ourprice').get_text().replace('₹','').strip()
#         print(ourprice)
#         try:
#             dealprice = soup.find(id='priceblock_dealprice').get_text().replace('₹','').strip()
#             print(dealprice)
#         except:
#             pass
        
#     except Exception as e:
#         print(e)
#         # price = ''


#     try:
#         soup.select('#availability .a-color-state')[0].get_text().strip()
#         stock = 'Out of Stock'
#     except:
#         stock = 'Available'

#     print(stock)
#     return 'sms-triggered to all subscribed users'

if __name__ == '__main__': 

    app.run() 
