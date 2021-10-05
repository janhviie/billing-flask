import sys, os
from datetime import datetime
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
    
import sqlalchemy.exc
from datetime import date
from datetime import datetime
from sqlalchemy.sql import text
from sqlalchemy.sql import text
from flask import Flask, render_template,url_for,request,redirect , session,flash, make_response;
import sys;
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from werkzeug.utils import secure_filename
import pdfkit



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/product_information'

app.secret_key = "any random string"
db = SQLAlchemy(app)

class items_info(db.Model):
    item_code = db.Column(db.String(200), unique=True, primary_key=True, nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)

class bill_info(db.Model):
    bill_no = db.Column(db.String(100), unique=True, primary_key=True, nullable=False)
    bill_date = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    billing_address = db.Column(db.String(200), nullable=False)
    mobile_no = db.Column(db.Integer, nullable=False)

    # item_code = db.Column(db.Integer, nullable=False)
    # quantity = db.Column(db.Integer, nullable=False)
    # discount = db.Column(db.Integer, nullable=False)

class items_brought_info(db.Model):
    itemname = db.Column(db.String(100), nullable=False,primary_key=True)
    itemcode = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Integer, nullable=False)
    totalprice = db.Column(db.Integer, nullable=False)
    bill_no = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    tax = db.Column(db.Integer, nullable=False)


class generated_bill_info(db.Model):
    itemcode = db.Column(db.String(100), nullable=False, primary_key=True)
    bill_no = db.Column(db.String(100), nullable=False)
    bill_date = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    billing_address = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.Integer, nullable=False)
    tax = db.Column(db.Integer, nullable=False)
    itemname = db.Column(db.String(100), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unitprice = db.Column(db.Integer, nullable=False)
    totalprice = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)


@app.route("/guide", methods=['GET'])
def guide():
    return render_template('guide.html')



@app.route("/", methods=['GET', 'POST'])
def mainpage():
    session.clear()




    # print(session["customername"])
    if request.method == "POST":
        parameter = request.form.get('searchParameter')
        parameter = str(parameter)
        print(parameter)
        if parameter!='':
            resultlist = db.session.execute(
                "select * from generated_bill_info where customer_name like :name or bill_no = :billno or billing_address = :addr or mobile_no = :phone or itemname = :prodname or itemcode = :itemcode or totalprice = :price order by bill_date",
                {'name': parameter+'%' , 'billno': parameter+'%' , 'addr': parameter+'%', 'phone': parameter+'%', 'prodname': parameter+'%', 'itemcode': parameter+'%', 'price': parameter+'%'})
            result = resultlist.fetchall()
            print(result)
        else:
            resultl = db.session.execute("select * from generated_bill_info")
            result = resultl.fetchall()

        if result:
            return render_template('oldbills.html', result=result)

        else:
            flash("No Records Found")


    return render_template('mainpage.html')



@app.route("/additem", methods=['GET', 'POST'])
def home():

    if request.method == "POST":
        itemcode = request.form.get("itemcode")
        itemname = request.form.get("itemname")
        unit = request.form.get("unit")
        price = request.form.get("price")
        basicInfoentry = items_info(item_code = itemcode, item_name= itemname, unit=unit, price=price)
        try:
            db.session.add(basicInfoentry)
            db.session.commit()
            flash("Item Added in Database Successfully")

        except sqlalchemy.exc.IntegrityError:
            return (sqlalchemy.exc.IntegrityError)

    return render_template("additemForm.html")


@app.route("/billing", methods=['GET' , 'POST'])
def billing():
    session.clear()
    countofrows = 0;
    count = db.session.execute("select * from bill_info")
    countlist = count.fetchall()
    for n in countlist:
        countofrows += 1;


    # get date and time
    now = datetime.now()
    dt_string = now.strftime('%Y-%m-%d %I:%M:%S %p')
    print("date and time =", dt_string)
    billdate = dt_string

    billno = countofrows + 1
    session["billno"] = countofrows + 1

    # if request.method == "POST":
    #     # billno = request.form.get("billno")
    #     # billdate = request.form.get("billdate")
    #     customername = request.form.get("customername")
    #     billingaddress = request.form.get("billingaddress")
    #     mobileno = request.form.get("mobileno")
    #
    #     countofrows=0;
    #     count = db.session.execute("select * from bill_info")
    #     countlist = count.fetchall()
    #     for n in countlist:
    #         countofrows+=1;
    #
    #     # get date and time
    #     now = datetime.now()
    #     dt_string = now.strftime('%Y-%m-%d %I:%M:%S %p')
    #     print("date and time =", dt_string)
    #     billdate = dt_string
    #
    #     billno = countofrows+1
    #     session["billno"] = countofrows+1
    #     session["billdate"] = billdate
    #     session["customername"] = customername
    #     session["billingaddress"] = billingaddress
    #     session["mobileno"] = mobileno
    #
    #     print(request.form.get("mobileno"))
    #
    #
    #     basicInfoentry = bill_info(bill_no=billno, bill_date=billdate, customer_name=customername,
    #                                billing_address=billingaddress, mobile_no=request.form.get("mobileno")
    #
    #                                )
    #     try:
    #         db.session.add(basicInfoentry)
    #         db.session.commit()
    #         print("SUCCESSFUl")
    #     except sqlalchemy.exc.IntegrityError:
    #         print("ERROR")
    #         flash("Error generating bill")
    #         return (sqlalchemy.exc.IntegrityError)

    return render_template("bill_form.html")

class items:
    def __init__(self, name, itemcode, quantity, unitprice, totalprice):
        self.name = name
        self.itemcode = itemcode
        self.quantity = quantity
        self.unitprice = unitprice
        self.totalprice = totalprice


@app.route("/broughtItems", methods=['GET', 'POST'])
def broughtItem():
    if "visitedbilling" in session:
        return redirect(url_for("billing"))


    sum = "0"
    session["visitedbroughtitem"] = "yes"
    if request.method == "POST":
            # session["visitedbilling"] = "yes"
            countofrows = 0;
            count = db.session.execute("select * from bill_info")
            countlist = count.fetchall()
            for n in countlist:
                countofrows += 1;

            # get date and time
            now = datetime.now()
            dt_string = now.strftime('%Y-%m-%d %I:%M:%S %p')
            print("date and time =", dt_string)
            billdate = dt_string

            billno = countofrows + 1
            session["billno"] = billno
            itemcode = request.form.get("itemcode")

            resultlist = db.session.execute(
                "SELECT * FROM items_info WHERE item_code = :val",
                {'val': itemcode})
            resultlistitems = resultlist.fetchall()

            # if resultlistitems:
            #
            #     for i in resultlistitems:
            #         unitprice = int(i.price)
            #         name = i.item_name
            #
            # else:
            #     flash("No Such Item exists")
            #     return redirect(url_for('broughtItem'))





            if request.form.get('action') == "Next":
                # billno = request.form.get("billno")
                # billdate = request.form.get("billdate")
                customername = request.form.get("customername")
                billingaddress = request.form.get("billingaddress")
                mobileno = request.form.get("mobileno")

                countofrows = 0;
                count = db.session.execute("select * from bill_info")
                countlist = count.fetchall()
                for n in countlist:
                    countofrows += 1;

                # get date and time
                now = datetime.now()
                dt_string = now.strftime('%Y-%m-%d %I:%M:%S %p')
                print("date and time =", dt_string)
                billdate = dt_string

                billno = countofrows + 1
                # session["billno"] = countofrows + 1
                session["billdate"] = billdate
                session["customername"] = customername
                session["billingaddress"] = billingaddress
                session["mobileno"] = mobileno

                print(request.form.get("mobileno"))

                basicInfoentry = bill_info(bill_no=billno, bill_date=billdate, customer_name=customername,
                                           billing_address=billingaddress, mobile_no=request.form.get("mobileno")

                                           )
                try:
                    db.session.add(basicInfoentry)
                    db.session.commit()
                    print("SUCCESSFUl")
                except sqlalchemy.exc.IntegrityError:
                    print("ERROR")
                    flash("Error generating bill")
                    return (sqlalchemy.exc.IntegrityError)






            if request.form.get('action') == "ADD":

                itemname = request.form.get("itemname")
                quantity = request.form.get("quantity")
                session["quantity"] = quantity
                discount = request.form.get("discount")
                session["disc"] = discount
                tax = request.form.get("tax")
                session["tax"]  =tax
                resultlist = db.session.execute(
                    "SELECT * FROM items_info WHERE item_name = :val",
                    {'val': itemname})
                resultlistitems = resultlist.fetchall()
                if resultlistitems:

                    for i in resultlistitems:
                        unitprice = int(i.price)
                        code = i.item_code

                else:
                    flash("No Such Item exists")
                    return redirect(url_for('broughtItem'))


                Finallist = []
                for i in resultlistitems:
                    unitprice = int(i.price)
                    code = i.item_code

                if (session["tax"] != "0" and discount != "0"):

                    totalPrice = ((unitprice - (unitprice * (int(discount)/100))) * int(quantity))
                    taxamount = (int(tax)/100) * totalPrice

                    totalPrice = totalPrice+taxamount
                if (session["tax"] !="0" and discount == "0"):
                    taxamount = ((int(tax) / 100) * unitprice)

                    totalPrice = unitprice + taxamount
                    totalPrice = totalPrice * int(quantity)

                if session["tax"] == "0" and discount != "0":
                    taxamount = ((int(discount) / 100) * unitprice)

                    totalPrice = unitprice - taxamount
                    totalPrice= totalPrice*int(quantity)
                if session["tax"] == "0" and discount == "0":
                    totalPrice = unitprice*int(quantity)






                # print(taxamount)
                session['code'] = code
                Finallist.append(items(itemname, code, quantity, unitprice, totalPrice))

                entry = items_brought_info(bill_no = session["billno"], itemname = itemname, itemcode=code, quantity=quantity , unitprice=unitprice,totalprice=totalPrice,
                                           discount=session["disc"], tax=session["tax"])


                entryinbilldb = generated_bill_info(itemcode = code,bill_no= session["billno"], bill_date= session["billdate"],
                                                    customer_name = session["customername"], billing_address =session["billingaddress"],
                                                    mobile_no = session["mobileno"] , tax = session["tax"], itemname =itemname, quantity = quantity
                                                    , unitprice=unitprice, totalprice = totalPrice, discount=discount
                                                    )
                try:
                    db.session.add(entry)
                    db.session.add(entryinbilldb)
                    db.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    return (sqlalchemy.exc.IntegrityError)

                resultlist = db.session.execute(
                    "SELECT * FROM generated_bill_info where bill_no = :val", {'val': session["billno"]})
                result = resultlist.fetchall()
                for i in result:
                    print("discount")
                    print(i.discount)
                return redirect(url_for('broughtItem', Finallist=result , sum=sum))

                # return render_template("broughtItemForm.html", Finallist=result)

            if request.form.get('action') == "Calculate Total":
                print("in add total")
                resultlist = db.session.execute(
                    "select * from generated_bill_info where bill_no = :val",
                    {'val': session["billno"]})
                result = resultlist.fetchall()
                sumTotal=0
                for i in result:
                    sumTotal = sumTotal+i.totalprice
                stringsum = str(sumTotal)
                sum = "Total: " + stringsum + " Rs."

                print("SUM")
                print(sum)





            if request.form.get('action') == 'Generate Bill':
                print("clicked on generated")
    countofrows = 0;
    count = db.session.execute("select * from bill_info")
    countlist = count.fetchall()
    for n in countlist:
        countofrows += 1;

    # get date and time
    now = datetime.now()
    dt_string = now.strftime('%Y-%m-%d %I:%M:%S %p')
    print("date and time =", dt_string)
    billdate = dt_string

    billno = countofrows + 1
    session["bno"] = countofrows + 1

    print("SESSION")
    print(session["bno"])
    resultlist = db.session.execute(
        "SELECT * FROM generated_bill_info where bill_no = :val", {'val': session["bno"]})
    result = resultlist.fetchall()

    for i in result:
        print(i.itemcode)


    return render_template("broughtItemForm.html" , Finallist = result, sum=sum)


@app.route("/generatebill", methods=['GET', 'POST'])
def generatebill():
    if "visitedbroughtitem" not in session:
        return redirect(url_for("billing"))
    session["visitedgeneratebill"] = "yes"

    resultlist = db.session.execute(
        "select * from generated_bill_info where bill_no = :val",
        {'val': session["billno"]})
    result = resultlist.fetchall()
    total = 0
    for item in result:
        total = total + item.totalprice
        billno = item.bill_no
        billdate = item.bill_date
        cusname = item.customer_name
        address = item.billing_address
        phoneNo = item.mobile_no
        tax = item.tax
    options = {
        "enable-local-file-access": None
    }
    if request.method == "POST":
        session['visitedgeneratebill'] = "yes"
        resultlist = db.session.execute(
            "select * from generated_bill_info where bill_no = :val",
            {'val': session["bno"]})
        result = resultlist.fetchall()
        total=0
        for item in result:
            total = total + item.totalprice
            billno = item.bill_no
            billdate = item.bill_date
            cusname = item.customer_name
            address = item.billing_address
            phoneNo = item.mobile_no
            tax = item.tax


        options = {
            "enable-local-file-access": None
        }

        if result:

            for i in result:
                # unitprice = int(i.price)
                name = i.itemname

        else:

            flash("Cannot Generate Bill with empty items")
            return redirect(url_for('broughtItem'))
    resultlist = db.session.execute(
        "select * from generated_bill_info where bill_no = :val",
        {'val': session["billno"]})
    result = resultlist.fetchall()
    rowcount=0
    discountcount=0
    taxcount=0
    for i in result:
        rowcount+=1
        if (i.discount >0):
            discountcount+=1
        if(i.tax>0):
            taxcount+=1


    if(discountcount>0 and taxcount>0):
        return render_template("invoice1.html", result=result, billno=billno, billdate=billdate, name=cusname,
                               address=address, phoneNo=phoneNo, tax=tax, total=total
                               )
    if(discountcount==0 and taxcount>0):
        return render_template("invoice1withtax.html", result=result, billno=billno, billdate=billdate, name=cusname,
                               address=address, phoneNo=phoneNo, tax=tax, total=total
                               )
    if (discountcount > 0 and taxcount == 0):
        return render_template("invoice1withdiscount.html", result=result, billno=billno, billdate=billdate,
                               name=cusname,
                               address=address, phoneNo=phoneNo, tax=tax, total=total
                               )
    if (discountcount == 0 and taxcount == 0):
        return render_template("invoicewithoutanything.html", result=result, billno=billno, billdate=billdate,
                               name=cusname,
                               address=address, phoneNo=phoneNo, tax=tax, total=total
                               )









@app.route("/invoice", methods=['GET', 'POST'])
def invoice():
    if "visitedgeneratebill" not in session:
        return redirect(url_for('billing'))
    if request.method == "POST":

        total = 0
        resultlist = db.session.execute(
            "select * from generated_bill_info where bill_no = :val",
            {'val': session["billno"]})
        result = resultlist.fetchall()
        for item in result:
            total = total + item.totalprice
            billno = item.bill_no
            billdate = item.bill_date
            cusname = item.customer_name
            address = item.billing_address
            phoneNo = item.mobile_no
            tax = item.tax
        options = {
            "enable-local-file-access": None
        }

        rowcount = 0
        discountcount = 0
        taxcount = 0
        for i in result:
            rowcount += 1
            if (i.discount > 0):
                discountcount += 1
            if (i.tax > 0):
                taxcount += 1

        if (discountcount > 0 and taxcount > 0):
            rendered= render_template("invoice1bill.html", result=result, billno=billno, billdate=billdate, name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
        if (discountcount == 0 and taxcount > 0):
            rendered= render_template("invoice1withtaxbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
        if (discountcount > 0 and taxcount == 0):
            rendered= render_template("invoice1withdiscountbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
        if (discountcount == 0 and taxcount == 0):
            rendered= render_template("invoicewithoutanythingbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )

        css=['invoicestyle.css']
        pdf = pdfkit.from_string(rendered, False, options=options, css=css)
        response = make_response(pdf)
        response.headers['Content-Type'] = "application/pdf"
        response.headers['Content-Disposition'] = 'inline; filename=out.pdf'



        resultlist = db.session.execute(
        "select * from generated_bill_info where bill_no = :val",
        {'val': session["billno"]})
        result = resultlist.fetchall()
        total=0
        for item in result:
            total = total+item.totalprice
            billno = item.bill_no
            billdate = item.bill_date
            name = item.customer_name
            address = item.billing_address
            phoneNo = item.mobile_no
            tax = item.tax


        return response
    total = 0
    resultlist = db.session.execute(
        "select * from generated_bill_info where bill_no = :val",
        {'val': session["billno"]})
    result = resultlist.fetchall()
    for item in result:
        total = total + item.totalprice
        billno = item.bill_no
        billdate = item.bill_date
        cusname = item.customer_name
        address = item.billing_address
        phoneNo = item.mobile_no
        tax = item.tax
    options = {
        "enable-local-file-access": None
    }

    rowcount = 0
    discountcount = 0
    taxcount = 0
    for i in result:
        rowcount += 1
        if (i.discount > 0):
            discountcount += 1
        if (i.tax > 0):
            taxcount += 1

    if (discountcount > 0 and taxcount > 0):
        rendered = render_template("invoice1bill.html", result=result, billno=billno, billdate=billdate, name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
    if (discountcount == 0 and taxcount > 0):
        rendered = render_template("invoice1withtaxbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
    if (discountcount > 0 and taxcount == 0):
        rendered = render_template("invoice1withdiscountbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )
    if (discountcount == 0 and taxcount == 0):
        rendered = render_template("invoicewithoutanythingbill.html", result=result, billno=billno, billdate=billdate,
                                   name=cusname,
                                   address=address, phoneNo=phoneNo, tax=tax, total=total
                                   )

    css = ['invoicestyle.css']
    pdf = pdfkit.from_string(rendered, False, options=options, css=css)
    response = make_response(pdf)
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = 'inline; filename=out.pdf'

    resultlist = db.session.execute(
        "select * from generated_bill_info where bill_no = :val",
        {'val': session["billno"]})
    result = resultlist.fetchall()
    total = 0
    for item in result:
        total = total + item.totalprice
        billno = item.bill_no
        billdate = item.bill_date
        name = item.customer_name
        address = item.billing_address
        phoneNo = item.mobile_no
        tax = item.tax

    return response



@app.route("/delete", methods=['GET', 'POST'])
def delete():

    itemcode = request.args.get('itemcode', None)
    quantity = request.args.get('qt', None)
    resultlist = db.session.execute(
        "delete from generated_bill_info where itemcode = :val and quantity = :val2 and bill_no=:val3 ",
        {'val': itemcode , 'val2' : quantity, 'val3': session['bno'] })

    # rlist = db.session.execute(
    #     "delete from items_brought_info where itemcode = :val and quantity = :val2 and discount = :disc and tax = :tax",
    #     {'val': itemcode , 'val2' : quantity, 'disc': session["disc"], 'tax': session["tax"] })
    db.session.commit()
    return redirect(url_for('broughtItem'))







logging.basicConfig(level=logging.DEBUG)
app.debug=True
app.run(debug=True)




