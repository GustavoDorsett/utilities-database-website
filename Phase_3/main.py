from flask import Flask, render_template,  request, url_for, flash, redirect
import pyodbc 
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'RANDOM_KEY'

def queryDB(query, insert = False):
    conn_str = (
        "DRIVER={PostgreSQL ODBC Driver(ANSI)};"         #CHANGE AS NEEDED TO YOUR LOCAL DRIVER:      
        "DATABASE=CSCE6400;"                     #For Alex - PostgreSQL ANSI(x64)
        "UID=postgres;"                          #For Others - PostgreSQL ODBC Driver(ANSI)
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

        if zipcode not in zipcodes:
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


        #appliances = queryDB("SELECT Appliance_order_num, Appliance_type, Manufacturer_name, Model_name from public.Appliance ORDER BY Appliance_order_num ASC")
        return redirect(url_for('appliance_list', email=email))

    else:
        manufacturers_sql = """
                                    SELECT NAME from public.manufacturer
        """
        manufacturers = [c[0] for c in queryDB(manufacturers_sql)]
        return render_template("add_appliance.html",manufacturers=manufacturers, email=email)


@app.route('/appliance_list/<email>', methods=["GET", "POST"])
def appliance_list(email):
    if request.method == 'POST':
        #placeholder for now
        pass
    
    else:
        disable_query = queryDB("SELECT Appliance_order_num FROM public.Appliance WHERE Email = '{0}'".format(email))
        if disable_query == []:
            disable = 1
        else:
            disable = 0    
        appliances = queryDB("SELECT Appliance_order_num, Appliance_type, Manufacturer_name, Model_name FROM public.Appliance WHERE email='{0}' ORDER BY Appliance_order_num ASC".format(email))
        return render_template("appliance_list.html", appliances = appliances, email=email, disable=disable)

@app.route("/delete/<email>/<aon>", methods=['GET'])
def delete(email, aon):
    queryDB("Delete FROM public.Appliance cascade where email='{0}' and Appliance_order_num={1}".format(email, aon), True)
    return redirect(url_for('appliance_list', email=email))

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
        disable_query = queryDB("SELECT utility FROM utility WHERE email = '{0}'".format(email))
        if disable_query == []:
            disable_query2 = queryDB("SELECT power_order_num FROM powergenerator WHERE email = '{0}'".format(email))
            if disable_query2 == []:
                disable = 1
            else:
                disable = 0 
        else:
            disable = 0  
        
        rows = queryDB("SELECT Power_order_num, Generation_type, Avg_kwh, Battery_storage FROM public.PowerGenerator WHERE Email = '{0}' ORDER BY Power_order_num ASC".format(email))
        return render_template("power_list.html", rows=rows, email=email,disable=disable)

@app.route('/delete_gen/<email>/<pon>', methods=['GET'])
def delete_gen(email, pon):
    queryDB("Delete FROM public.PowerGenerator cascade where email='{0}' and Power_order_num={1}".format(email, pon), True)
    return redirect(url_for('power_list', email=email))

@app.route('/end_submission/<email>', methods=['GET'])
def end_submission(email):

    return render_template("end_submission.html", email=email)



@app.route('/report_menu', methods=['GET'])
def report_menu():
     return render_template('report_menu.html')

@app.route('/report_top25', methods=['GET'])
def report_top25():
    top25 = queryDB("SELECT A.manufacturer_name, COUNT(A.manufacturer_name), (SELECT COUNT(*) AS AirHandler FROM appliance AS B WHERE B.manufacturer_name = A.manufacturer_name AND B.appliance_type = 'air_handler'), (SELECT COUNT(*) AS WaterHeater FROM appliance AS C WHERE C.manufacturer_name = A.manufacturer_name AND C.appliance_type = 'water_heater') FROM appliance AS A GROUP BY A.manufacturer_name ORDER BY COUNT(A.manufacturer_name) DESC LIMIT 25")
    return render_template('report_top25.html', top25 = top25)

@app.route('/report_manufacturer-model_search', methods=['GET' , 'POST'])
def report_manufacturer_model_search():
    
    if request.method == 'POST':
        manu_str = request.form['manusearch'].lower()
        manu_query = """SELECT Manufacturer_name, Model_name 
                        FROM public.Appliance 
                        WHERE LOWER(Model_name) LIKE '%'  || '{0}' || '%'
                        OR LOWER(Manufacturer_name) LIKE '%'  || '{0}' || '%'
                        ORDER BY Manufacturer_name, Model_name ASC
                     """.format(manu_str)
        results = queryDB(manu_query)
        return render_template('report_manufacturer-model_search.html', results=results, manu_str=manu_str)
    else:
        return render_template('report_manufacturer-model_search.html')

@app.route('/report_heat-cool_details', methods=['GET'])
def report_heat_cool_details():
    
    ac_query = """SELECT home_type, 
                        COUNT(energy_efficiency_ratio) AS NumAC,
                        ROUND(CAST(AVG(btu_rating) AS NUMERIC), 0) AS AvgACBTUs,
                        ROUND(CAST(AVG(energy_efficiency_ratio) AS NUMERIC), 1) AS AvgEER 
                    FROM (airconditioner NATURAL JOIN appliance) NATURAL JOIN household 
                    GROUP BY home_type"""

    heater_query = """SELECT home_type, 
                            COUNT(heater_energy_source) AS NumHeaters,
                            ROUND(CAST(AVG(btu_rating) AS NUMERIC), 0) AS AvgHeaterBTUs,
                            (SELECT heater_energy_source AS MostCommonEnergySource
                                FROM (heater NATURAL JOIN appliance) NATURAL JOIN household  
                                GROUP BY heater_energy_source
                                ORDER BY COUNT(heater_energy_source) DESC LIMIT 1)
                        FROM (heater NATURAL JOIN appliance) NATURAL JOIN household 
                        GROUP BY home_type"""

    heatpump_query = """SELECT home_type, 
                                COUNT(email) AS NumHeatPumps, 
                                ROUND(CAST(AVG(btu_rating) AS NUMERIC), 0) AS AvgHeatPumpBTUs,
                                ROUND(CAST(AVG(seasonal_efficiency_ratio) AS NUMERIC), 1) AS AvgSEER,
                                ROUND(CAST(AVG(heat_performance_factor) AS NUMERIC), 1) AS AvgHSPF 
                        FROM (heatpump NATURAL JOIN appliance) NATURAL JOIN household 
                        GROUP BY home_type"""

    all_details = []
    ac_details = queryDB(ac_query)
    heater_details = queryDB(heater_query)
    heatpump_details = queryDB(heatpump_query)

    for a in range(0,len(ac_details)):
        all_details.append(list(ac_details[a]))

    for a in range(0,len(heater_details)):
        all_details[a].extend(heater_details[a])

    for a in range(0,len(heatpump_details)):
        all_details[a].extend(heatpump_details[a])

    return render_template('report_heat-cool_details.html', all_details = all_details)

@app.route('/report_waterheater_state', methods=['GET'])
def report_waterheater_state():
    state_waterheaters = queryDB("SELECT pc.state, ROUND(CAST(AVG(capacity) AS NUMERIC), 0), ROUND(CAST(AVG(btu_rating) AS NUMERIC), 0), ROUND(CAST(AVG(current_temp_setting) AS NUMERIC), 1), COUNT(current_temp_setting), (COUNT(email) - COUNT (current_temp_setting)) FROM ((waterheater NATURAL JOIN appliance) NATURAL JOIN household) NATURAL JOIN postalcode AS pc GROUP BY pc.state ORDER BY pc.state ASC")
    return render_template('report_waterheater_state.html', state_waterheaters = state_waterheaters)

@app.route('/report_drilldown_state/<drilldown_state>', methods=['GET'])
def report_drilldown_state(drilldown_state):
     drilldown_waterheaters = queryDB("SELECT waterheater_energy_source, ROUND(CAST(MIN(capacity) AS NUMERIC), 0), ROUND(CAST(AVG(capacity) AS NUMERIC), 0), ROUND(CAST(MAX(capacity) AS NUMERIC), 0), ROUND(CAST(MIN(current_temp_setting) AS NUMERIC), 1), ROUND(CAST(AVG(current_temp_setting) AS NUMERIC), 1), ROUND(CAST(MAX(current_temp_setting) AS NUMERIC), 1) FROM (waterheater NATURAL JOIN household) NATURAL JOIN postalcode AS PC WHERE PC.state = '{0}' GROUP BY waterheater_energy_source ORDER BY waterheater_energy_source ASC".format(drilldown_state))
     return render_template('report_drilldown_state.html', drilldown_waterheaters = drilldown_waterheaters, drilldown_state = drilldown_state)

@app.route('/report_offthegrid_dashboard', methods=['GET'])
def report_offthegrid_dashboard():
    hh = queryDB('''SELECT State, COUNT (DISTINCT(email)) AS "Count of household" FROM  Household NATURAL JOIN postalcode where email not IN(select email from utility) GROUP BY
                                            State ORDER BY "Count of household" DESC LIMIT 1;
                                            ''')
    
    abc =  queryDB('''SELECT ROUND (AVG(CAST(battery_storage AS numeric)), 0) AS "Average of battery storage capacity" FROM powergenerator;
                                            ''')
    
    pp = queryDB('''SELECT Generation_Type, ROUND(SUM (battery_storage), 0)*100/(select sum(battery_storage) from powergenerator) AS "Percentage of battery storage capacity" FROM powergenerator
                                                    GROUP BY Generation_Type
                                            ''')
    

    awc = queryDB('''SELECT ROUND(AVG(CAST(oncapacity AS numeric)), 1) AS "Average Water Heater Gallon capacity of all on-the-grid", 
                                                    ROUND(AVG(CAST(foo2.offcapacity AS numeric)), 1) AS "Average Water Heater Gallon capacity of all off-the-grid"
                                            FROM
                                                (
                                                    (SELECT waterheater.email, waterheater.appliance_order_num, capacity AS "oncapacity" FROM waterheater 
                                                    INNER JOIN utility on waterheater.email = utility.email) AS foo3
                                                    FULL OUTER JOIN (SELECT email, appliance_order_num, capacity AS "offcapacity" FROM waterheater WHERE email NOT IN
                                                    (SELECT email FROM utility)) AS foo ON foo.email = foo3.email) as foo2
                                            ''')
    
    btu_stats = queryDB('''SELECT ROUND(MIN(CAST(btu_rating AS numeric)), 0) AS "Minimum BTUs", 
                                            ROUND(AVG(CAST(btu_rating AS numeric)), 0) AS "Average BTUs", 
                                            ROUND(MAX(CAST(btu_rating AS numeric)), 0) AS "Maximum BTUs" FROM
                                            (SELECT email, Appliance_order_num, Appliance_Type, btu_rating FROM "appliance"
                                                    WHERE email NOT IN (SELECT email FROM "utility")) b GROUP BY Appliance_Type;
                                            ''')

    
    return render_template('report_offthegrid_dashboard.html', hh=hh, abc = abc, pp= pp, awc= awc, btu_stats =btu_stats)

@app.route('/report_household-radius_average', methods=['GET', 'POST'])
def report_household_radius_average():
    
    if request.method == 'POST':
        print(request.form)
        zipcodes = [c[0] for c in queryDB("Select Zip_code from public.PostalCode")]
        zip = request.form['zip_code']
        radius = request.form['radius']
    
        if zip not in zipcodes:
            flash("Zipcode not found in DB!")
            fail=True
        results = queryDB("""
       WITH base_table as ( 
                SELECT foo7.zip_code, {0},
                    square_footage, heat_setting, cool_setting, 
                    generation_type, avg_kwh, battery_storage , utility, home_type
                FROM (household JOIN powergenerator ON household.email = powergenerator.email)
                        JOIN(
                           SELECT zip_code FROM postalcode , (
                                SELECT 3958.75*C AS distance 
                                FROM (
                                    SELECT 2*ATAN2(SQRT(A), SQRT(1-A) ) AS C
                                    FROM(
                                        SELECT (SIN((lat2-lat1)/2)*SIN((lat2-lat1)/2)) + (COS(lat1)* COS(lat2)) * (SIN((lon2-lon1)/2)*SIN((lon2-lon1)/2)) AS A 
                                        FROM(
                                            SELECT Latitude*3.14/180 AS lat2, Longitude*3.14/180 AS lon2, lat1, lon1 
                                            FROM postalcode, ( 
                                                SELECT Latitude*3.14/180 AS lat1, Longitude*3.14/180 AS lon1 FROM postalcode WHERE zip_code = '{1}' ) as foo
                                            ) as foo2
                                        ) as foo3 
                                    ) as foo4
                                ) as foo5 WHERE distance <= {0} ) as foo7 
                            ON foo7.zip_code = household.zip_code
                            JOIN (SELECT email, utility FROM utility) AS foo8
                        ON household.email = foo8.email

	   			) select * from (
					(select count(*) from base_table) foo12 CROSS JOIN 
					(select COUNT(base_table.zip_code) as htc, home_type from base_table GROUP BY home_type) foo13 CROSS JOIN
					( select ROUND(AVG(CAST( square_footage AS numeric)), 0), 
								ROUND(AVG(CAST( heat_setting AS numeric)),1), 
								ROUND(AVG( CAST(cool_setting AS numeric)),1),
								ROUND(AVG(CAST(avg_kwh AS numeric)), 0) from base_table ) foo14 CROSS JOIN
					(select max(util_count) from (select count(utility) as util_count from base_table GROUP BY utility) foo16 ) foo15 
				) as foo10
        """.format(radius, zip))
            
        print(results)
            
        return render_template('report_household-radius_average.html', results = results)    
    else:
        return render_template('report_household-radius_average.html', results = [])

if __name__ == '__main__':
    app.run(debug=True)

