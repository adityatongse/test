# importing necesasary libraries

from flask import Flask, render_template, redirect, request, url_for ,session,redirect ,flash
from flask_mysqldb import MySQL
from adapter import otp,barcode_scanner
import time

# flask app variable 
app = Flask(__name__)
app.secret_key = ("superkey")

# connecting the application with localdatabase
app.config["SESSION_PERMANENT"] = False
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "inventory"
mysql = MySQL(app)


# This route will navigate user to the welcome page of the webapp
@app.route('/')
def welcome():
  time.sleep(1)
  return render_template("welcome.html",current_page="welcome",session=(len(session) > 0))

# This route will navigate user to the contactus page
@app.route('/contactus',methods=['GET','POST'] )
def contactus():
  print(len(session) > 0)
  return render_template('contactus.html',session=(len(session) > 0))

''' This route will navigate user to the login page 
checks weather user entered username and password is available into the database or not 
if avaiable it'll send the one time password to the user for authentication purpose
after sucessful query session will be start'''
@app.route('/login', methods=['GET','POST'])
def login():
    record = ""
    # To remove
    print(session)
    if len(session) > 0:
      # To remove
      print("session")
      # redirect(url_for('logout'))
      logout()
    print(session)
    
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      cur = mysql.connection.cursor()
      cur.execute('select * from users where user_username =%s and user_password = %s',(username, password,))
      record = cur.fetchone()
      # To remove
      print("LOG: record user-m:Post:", record)
      if record :
        # To remove
          print("LOG: record user:", record) 
          #Session start
          session['loggedin'] = True
          session["username"] = username
          #session['user_role'] = fetch_user_role(session["username"])
          cur = mysql.connection.cursor()
          cur.execute('select user_contact from users where user_username = %s',(session['username'],))
          user_contact_fromdb=cur.fetchone()
          for user_contact in user_contact_fromdb:
            print(user_contact)
          print("The user is =",session["username"])
          print("user contact is : ",user_contact)
          global created_otp
          created_otp = otp.generate_otp()
          cur.close()
          print("created otp : ", created_otp)
          otp.send_otp(user_contact,created_otp)
          return redirect(url_for('otp_page'))
      else:
          print("else")
          flash("incorrect username or password")
          return render_template('login.html') 
    else:
      return render_template('login.html')


@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
  if request.method=='POST':
    fp_username=  request.form['fp_username']
    print(fp_username)
    cur = mysql.connection.cursor()
    cur.execute('select user_password,user_contact from users where user_username=%s',(fp_username,))
    ps=cur.fetchone()
    if ps!=None:
      ps=list(ps)
      print(ps[0],ps[1])
      otp.send_otp(ps[1],ps[0])
      flash("Password has beed sent successfully on your registered whatsapp number.")
      return render_template('login.html')
    else:
      flash("Invalid Username.")
      return render_template('forgot_password.html') 
  else:
    return render_template('forgot_password.html')    

#created_otp= otp.generate_otp()
@app.route('/otp_page',methods= ['GET','POST'])
def otp_page():

    if request.method == "POST":
      print(request.form["otp"])
      print(request.form["otp"] in created_otp[-5::]  )
      print(type(created_otp[-5::]),type(request.form["otp"]))
      
      if request.form["otp"] in created_otp:
          return redirect(url_for('dashboard'))
      else:
          flash("Wrong OTP !! TRY AGAIN !!",'danger')
          return redirect(url_for('otp_page'))
    else:
      return render_template("otp_page.html")


#Dashboard Page
@app.route('/dashboard')
def dashboard():
  if len(session)>0:
    total_items=0
    cur=mysql.connection.cursor()
    cur.execute('select COUNT(product_id) from products')
    temp=cur.fetchone()
    for item in temp:
      total_items=item
    
    print('Dashboard = ',session["username"])
    return render_template('dashboard.html',total_items=total_items)
  else:
    return render_template('login.html')
 
#Add new product
@app.route('/add_new_product',methods=['GET','POST'])
def add_new_product(): 
  if len(session)>0:
    
    if fetch_user_role(session['username'])==0:
      print("Inside permission 1")
      flash('You dont have a permission to add a new product.','danger')
      return render_template('dashboard.html')
    else:
      print("Inside permission 1 or 2")
      # fetching data from user 
      global barcode_value,p_manu_code,p_cate_code,p_name_code,p_barcode
      

      if request.method=='GET':
        barcode_value=barcode_scanner.extract_barcode()
        print(check_product(barcode_value[0]))
        if check_product(barcode_value[0]):
          flash("You already have this product into the inventory kindly uodate.")
          return render_template('update_product.html',p_barcode=barcode_value[0])
        else:
          p_barcode=barcode_value[0]
          p_manu_code =  barcode_value[2]
          p_cate_code = barcode_value[1]
          p_name_code = barcode_value[4]
          return render_template('add_new_product.html',p_barcode=p_barcode,p_manu_code=p_manu_code,p_cate_code=p_cate_code,p_name_code=p_name_code)

      else:
        product_manufacturer =request.form['productmanufacturer']
        product_category=request.form['productcategory']
        product_name =request.form['productname']
        product_price =request.form['productprice']
        product_expirydate =request.form['productexpirydate']
        product_size =request.form['productsize']
        product_mfg =request.form['productmanufacturedate']
        product_measure =request.form['productmeasure']
        product_stock_quantity =request.form['productstockquantity']
        print("barcode value from api : ",barcode_value)
        cur = mysql.connection.cursor()
        cur.execute('insert into products values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(p_barcode,product_manufacturer,p_manu_code,product_category,p_cate_code,product_name,p_name_code,product_price,product_measure,product_size,product_expirydate,product_mfg,product_stock_quantity))
        mysql.connection.commit()
        cur.close()
        flash("Added")
        return render_template('dashboard.html')
  else:
    return render_template('login.html')

#Product List   
@app.route('/product_list', methods=['GET', 'POST'])
def product_list():
  if len(session)>0:
    cur = mysql.connection.cursor()
    cur.execute('select product_id, product_category, product_name, product_stock_quantity from products')
    productList = cur.fetchall()
    print(productList)
    cur.close()
    return render_template('product_list.html', productList = productList)
  else:
    return render_template('login.html')
 

#Product Details List
@app.route('/product_details_page/<product_id>' , methods=['GET', 'POST'])
def product_details_page(product_id):
  if len(session)>0:
    cur = mysql.connection.cursor()
    cur.execute('select * from products where product_id = %s',(product_id,))
    productdetails=cur.fetchone()
    print(productdetails)
    cur.close()
    return render_template('product_details_page.html',productdetails=productdetails)
  else:
    return render_template('login.html')


#update new product
@app.route('/update_product',methods=['GET','POST'])
def update_product():
  if len(session)>0:
    # fetching data from user
    global barcode_value,p_barcode,available_stock
    if request.method=='GET':
      available_stock=0
      barcode_value=barcode_scanner.extract_barcode()
      if check_product(barcode_value[0]):
        p_barcode=barcode_value[0]
        cur = mysql.connection.cursor()
        cur.execute('select product_stock_quantity from products where product_id =%s ',(p_barcode,))
        stock_query_result=cur.fetchone()
        for i in stock_query_result:
          available_stock=i     
        print(available_stock)
        cur.close()
        return render_template('update_product.html',p_barcode=p_barcode)
      else:
        if fetch_user_role(session['username'])==0:
          flash("No product found, contact manager to add new product into inventory.")
          return redirect(url_for('dashboard'))
        else:
          flash("No product found in inentory kindly add new product.")
          session['p_barcode_existing']=barcode_value[0]
          return redirect(url_for('add_new_product'))
    else:
      #product_stock_quantity =request.form['productstockquantity']
      cur = mysql.connection.cursor()
      new_stock = request.form['productstockquantity']
      cur.execute('update products set product_stock_quantity =%s where product_id=%s',(available_stock+int(new_stock),p_barcode))
      mysql.connection.commit()
      cur.close()
      flash("Added")
      return render_template('dashboard.html')
  else:
    return render_template('login.html')

# customer details page
@app.route('/customer_details',methods=['GET','POST'])
def customer_details():
  if len(session)>0:
    if request.method=='GET':
      return render_template('customer_details.html')
    else:
      print("inside post method customer_details")
      customer_name= request.form['customername']
      customer_contact="+91"+request.form['customercontact']
      customer_email=request.form['customeremail']
      cur=mysql.connect.cursor()
      cur.execute('insert into customers values(%s,%s,%s)',('a','a','a'))
      mysql.connection.commit()
      cur.close()
      return render_template('create_bill.html',customer_name=customer_name,customer_contact=customer_contact,customer_email=customer_email)
  else:
    return render_template('login.html')

# create bill
global billing_items,item_list,total_sum
item_list=[]
billing_items={}
@app.route('/create_bill',methods=['GET','POST'])
def create_bill():
  if len(session)>0:
    cur=mysql.connection.cursor()
    value=barcode_scanner.extract_barcode()
    if check_product(value[0]):
      if value[0] in billing_items:
        billing_items[value[0]]+=1
      else:
        cur.execute('select product_id, product_name, product_price from products where product_id =%s',(value[0],))
        billing_items[value[0]]=1
        r=cur.fetchall() 
        for item in r:
          item_list.append(list(item)) 
        cur.close()
      print(billing_items,item_list)
      for item in billing_items:
        for i in range(len(item_list)):
          if item_list[i][0]==item:
            if len(item_list[i])==3:
              item_list[i].append(billing_items[item])
            else:
              item_list[i].pop()
              item_list[i].append(billing_items[item])
      total_sum=0.0
      for item in item_list:
        total_sum=total_sum+(item[3]*item[2])
      print("total_sum of the items are : ",total_sum)
      print(item_list)

      if request.method=='POST':
        print('inside post method')
        total_sum=0.0
        for item in item_list:
          total_sum=total_sum+(item[3]*item[2])
        print("total_sum of the items are : ",total_sum)
        print(item_list)
        return render_template('create_bill.html',billing_items_barcodes=item_list,total_sum=total_sum)
      return render_template('create_bill.html',billing_items_barcodes=item_list,total_sum=total_sum)
    else:
      flash('Product not found in inventory try with another product')
      return render_template('create_bill.html',billing_items_barcodes=item_list,total_sum=total_sum)
  else:
    return render_template('login.html')

# sending the bill
@app.route('/send_bill',methods=['GET','POST'])
def send_bill():
  a=[[1,2,3],[3,4,5]]
  t=77
  if len(session)>0:
    otp.send_otp("+917757963133",f"{a},{t}")
    flash("Bill has been sent successfully.")
    return render_template('dashboard.html')
  else:
    return render_template('login.html')

#View employee List
@app.route('/employee_list', methods=['GET', 'POST'])
def employee_list():
  if fetch_user_role(session['username'])==0:
    print("Inside permission 1")
    flash('You dont have a permission to view employee list.','danger')
    return render_template('dashboard.html')
  else:
   cur = mysql.connection.cursor()
   cur.execute('select user_id, user_role,user_username from users')
   employeeList = cur.fetchall()
   print(employeeList)
   cur.close()
   return render_template('employee_list.html', employeeList = employeeList)
 
#users details page
@app.route('/users_details_page/<user_id>' , methods=['GET', 'POST'])
def users_details_page(user_id):
   cur = mysql.connection.cursor()
   cur.execute('select * from users where user_id = %s',(user_id,))
   employeedetails=cur.fetchone()
   print(employeedetails)
   cur.close()
   return render_template('users_details_page.html',employeedetails=employeedetails)

#Resend otp page:
@app.route('/resend_otp')
def resend_otp():
   otp.send_otp("+917757963133",created_otp)
   flash("New OTP Sent!! ",'success')
   return redirect(url_for('otp_page'))
 
#profile page
@app.route('/profile',methods=['GET', 'POST'])
def profile():
  cur = mysql.connection.cursor()
  cur.execute('select user_fullname, user_role, user_contact, user_email from users where user_username = %s',(session['username'],))
  user = cur.fetchone()
  cur.close()
 
  return render_template('profile.html', user = user)

#logout function  
@app.route('/logout', methods=['GET','POST'])
def logout():
   session.pop("username")
   session.pop("loggedin")
   return render_template("logout.html")

# 404 Notfound error
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404

# 500 error
@app.errorhandler(500)
def page_not_found(e):
  return render_template("500.html"), 500
''' 
def for fetching user_role who is currently logged in into to system
this function takes parameter as username where session['username'] indicates the currently logged in user 
returns the 0,1,2 where 0 indicates role employee, 1 indicates role manager and 2 indicates role root user or super admin
'''
def fetch_user_role(username):
  cur=mysql.connection.cursor()
  cur.execute('select user_role from users where user_username = %s',(username,))
  permission=cur.fetchone()
  cur.close()
  for user_role in permission:
    permission = user_role
    print("Permission : ",user_role)
  return permission

''' 
def for checking product is already exist or not,
this function takes the b_value as a parameter which idicated the 13 digit string barcode value
extracted by the extract_barcode module present in adapter.barcode_scanner 
return bool value depends on the enrty found in db or not
'''
def check_product(b_value):
  cur = mysql.connection.cursor()
  cur.execute('select product_id from products where product_id = %s',(b_value,))
  record = cur.fetchone()
  if record:
    return True
  else:
    return False
  
'''
Entry point of the app.py file
execution of programm will starts from here and then it runs the flask app name app with debug option as True
'''
if __name__ == '__main__':
    app.run(debug=True)