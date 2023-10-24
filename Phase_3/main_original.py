from flask import Flask, render_template,  request, url_for, flash, redirect
import pyodbc 
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RANDOM_KEY'

def queryDB(query, insert = False):
    conn_str = (
        "DRIVER={PostgreSQL ODBC Driver(ANSI)};"
        "DATABASE=CSCE6400;"
        "UID=postgres;"
        "PWD=root;"
        "SERVER=localhost;"
        "PORT=5432;"
        )

    conn = pyodbc.connect(conn_str)
    crsr = conn.execute(query)
    if insert:
        crsr.commit()
        return "Success"
    else:
        result = crsr.fetchall()
    
    crsr.close()
    conn.close()
    return result


@app.route('/', methods=["GET", "POST"])
def home():
     return render_template('main_menu.html')


@app.route('/household_info', methods=["GET", "POST"])
def household_info():
    if request.method == 'POST':
        emails = [c[0] for c in queryDB("Select email from public.Household")]
        zipcodes = [c[0] for c in queryDB("Select Zip_code from public.PostalCode")]

        email = request.form['email']
        sqft = request.form['sqft']
        home_type = request.form['home_type']
        heating = request.form['heating'] if request.form['heating'] != "" else "NULL"
        cooling = request.form['cooling'] if request.form['cooling'] != "" else "NULL"
        zipcode = request.form['zip']   
        
        fail = False

        if email in emails:
            flash("Email already in use!")
            fail=True

        if int(zipcode) not in zipcodes:
            flash("Zipcode not found in DB!")
            fail=True

        if fail:
            return render_template('household_info.html')

        household_query = """
                                INSERT INTO public.Household VALUES ('{0}', {1}, '{2}', {3}, {4}, {5})
                        """.format(email, sqft, home_type, cooling, heating, zipcode)
        queryDB(household_query, True)
        utilities = [v for k,v in request.form.items() if 'utility' in k]

        for u in utilities:
            utility_query = """
                                INSERT INTO public.utility VALUES ('{0}', '{1}')
                            """.format(email, u)

            queryDB(utility_query, True)
        
        return redirect(url_for('add_appliance', email=email))
    else:
        emails = [c[0] for c in queryDB("Select email from public.Household")]

        return render_template('household_info.html')


@app.route('/add_appliance/<email>', methods=["GET", "POST"])
def add_appliance(email):
    if request.method == 'POST':
        print(request.form)
        a_type = request.form['appliance_type']
        model = request.form['modelname'] if 'modelname' in request.form.keys() else "NULL"
        manufacturer = request.form['manufacturer']
        email = request.form['email']
        btu_rating = request.form['btu_rating']

        aon_return = queryDB("SELECT max(Appliance_order_num) from public.Appliance where email='{0}'".format(email))[0][0]
        aon = int(aon_return)+1 if aon_return != None else 1

        #Creating an appliance
        queryDB(""" 
                INSERT INTO public.Appliance VALUES ('{0}',{1},'{2}','{3}',{4},'{5}')
                """.format(email, aon, a_type, model, btu_rating, manufacturer), True)

        if a_type == 'waterheater':
            wh_es = request.form['wh_energy_source']
            capacity = request.form['capacity']
            temperature = request.form['temperature']

            #Creating a water heater
            queryDB(""" INSERT INTO public.WaterHeater VALUES ('{0}', {1}, {2}, {3}, '{4}')
                    """.format(email, aon, capacity, temperature, wh_es), True)


        else:
            if "airconditioner" in request.form.keys():
                eer = request.form['eer']
                #Creating an air conditioner
                queryDB(""" INSERT INTO public.AirConditioner VALUES ('{0}',{1},'{2}')
                        """.format(email, aon, eer), True)
                
            #Changed elif to if, it was skipping if an airhandler had more than one      
            if "heater" in request.form.keys():
                hes = request.form['heater_energy_source']
                #Creating a heater
                queryDB(""" INSERT INTO public.Heater VALUES ('{0}', {1}, '{2}')
                        """.format(email, aon, hes), True)
            
            #Changed elif to if, it was skipping if an airhandler had more than one   
            if "heatpump" in request.form.keys():
                hspf = request.form['hspf']
                seer = request.form['seer']
                #Creating a heat pump
                queryDB(""" INSERT INTO public.HeatPump VALUES ('{0}', {1}, {2}, {3})
                        """.format(email, aon, seer, hspf), True)


        appliances = queryDB("SELECT Appliance_order_num, Appliance_type, Manufacturer_name, Model_name from public.Appliance ORDER BY Appliance_order_num ASC")
        return redirect(url_for('appliance_list', appliances = appliances, email=email))

    else:
        manufacturers_sql = """
                                    SELECT NAME from public.manufacturer
        """
        manufacturers = [c[0] for c in queryDB(manufacturers_sql)]
        return render_template("add_appliance.html",manufacturers=manufacturers, email=email)


@app.route('/appliance_list/<appliances>/<email>', methods=["GET", "POST"])
def appliance_list(appliances, email):
    if request.method == 'POST':
        values = request.form['delete']
        return render_template("appliance_list.html")
    else:
        apps = ast.literal_eval(appliances)
    
        return render_template("appliance_list.html", appliances = apps, email=email)

@app.route("/delete/<email>/<aon>/<type>", methods=['GET'])
def delete(email, aon, type):
    queryDB("Delete FROM public.Appliance cascade where email='{0}' and Appliance_order_num={1}".format(email, aon), True)
    appliances = queryDB("SELECT Appliance_order_num, Appliance_type, Manufacturer_name, Model_name from public.Appliance ORDER BY Appliance_order_num ASC")
    return redirect(url_for('appliance_list', appliances = appliances, email=email))

@app.route('/add_power/<email>', methods=['GET', 'POST'])
def add_power(email):
    if request.method == 'POST':
        emailed = email
        Generation_type = request.form['power_type']
        Avg_kwh = request.form['monthly_kwh']
        Battery_storage = request.form['storage_kwh']
        pon_return = queryDB("SELECT max(Power_order_num) from public.PowerGenerator where email='{0}'".format(email))[0][0]
        pon = int(pon_return)+1 if pon_return != None else 1
        
        power_query = """
                            INSERT INTO public.PowerGenerator VALUES ('{0}', {1}, '{2}', {3}, {4})
                        """.format(emailed, pon, Generation_type, Battery_storage, Avg_kwh)
        queryDB(power_query, True)
        return redirect(url_for('power_list', email=emailed))                
    else:
        skip_query = queryDB("SELECT Utility FROM public.Utility WHERE Email = '{0}'".format(email))
        if skip_query == []:
            skip = 1
        else:
            skip = 0
        return render_template("add_power.html", email=email, skip=skip)

@app.route('/power_list/<email>', methods=['GET', 'POST'])
def power_list(email):
    if request.method == 'POST':
        #placeholder for now
        pass
    else:
        rows = queryDB("SELECT Power_order_num, Generation_type, Avg_kwh, Battery_storage FROM public.PowerGenerator WHERE Email = '{0}' ORDER BY Power_order_num ASC".format(email))
        return render_template("power_list.html", rows=rows, email=email)

@app.route('/delete_gen/<email>/<pon>', methods=['GET'])
def delete_gen(email, pon):
    queryDB("Delete FROM public.PowerGenerator cascade where email='{0}' and Power_order_num={1}".format(email, pon), True)
    print("AT LEAST GOT HERE")
    return redirect(url_for('power_list', email=email))

@app.route('/end_submission/<email>', methods=['GET'])
def end_submission(email):

    return render_template("end_submission.html", email=email)



if __name__ == '__main__':
    app.run(debug=True)

