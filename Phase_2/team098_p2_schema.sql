-- CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password'; 

CREATE USER IF NOT EXISTS gatechUser@localhost IDENTIFIED BY 'gatech123'; 
DROP DATABASE IF EXISTS `cs6400_sp23_team098`;  
SET default_storage_engine=InnoDB; 
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci; 
CREATE DATABASE IF NOT EXISTS cs6400_ sp23_team098  
    DEFAULT CHARACTER SET utf8mb4  
    DEFAULT COLLATE utf8mb4_unicode_ci; 
USE cs6400_ sp23_team098; 
GRANT SELECT, INSERT, UPDATE, DELETE, FILE ON *.* TO 'gatechUser'@'localhost'; 
GRANT ALL PRIVILEGES ON `gatechuser`.* TO 'gatechUser'@'localhost'; 
GRANT ALL PRIVILEGES ON `cs6400_ sp23_team098`.* TO 'gatechUser'@'localhost'; 
FLUSH PRIVILEGES; 

-- Tables 

CREATE TABLE Household ( 
Email varchar(50) NOT NULL, 
Square_footage int NOT NULL, 
Home_type char(50) NOT NULL, 
Cool_setting int NULL, 
Heat_setting int NULL, 
Zip_code int NOT NULL, 
PRIMARY KEY (Email), 
FOREIGN KEY (Home_type) REFERENCES Household_type (Home_type) 
); 

CREATE TABLE HouseholdType ( 
Home_type varchar(20) NOT NULL, 
PRIMARY KEY (Home_type) 
); 

CREATE TABLE UtilityType( 
Utility_type varchar(20) NOT NULL, 
PRIMARY KEY (Utility_type) 
); 

CREATE TABLE Utility ( 
Email varchar(50) NOT NULL, 
Utility char(50) NOT NULL, 
PRIMARY KEY (Email, Utility), 
FOREIGN KEY (Email) REFERENCES Household (Email), 
FOREIGN KEY (Utility) REFERENCES UtilityType(Utility_type) 
); 

CREATE TABLE Appliance ( 
Email varchar(50) NOT NULL, 
Appliance_order_num int NOT NULL UNIQUE, 
Appliance_type char(50) NOT NULL, 
Model_name varchar(50) NULL, 
BTU_rating int NOT NULL, 
Manufacturer_name varchar(50) NOT NULL, 
PRIMARY KEY (Email, Appliance_order_num), 
FOREIGN KEY (Email) REFERENCES Household (Email), 
FOREIGN KEY (Appliance_type) REFERENCES ApplianceType (Appliance_type) 
); 

CREATE TABLE ApplianceType ( 
Appliance_type varchar(20) NOT NULL, 
PRIMARY KEY (Appliance_type) 
); 

CREATE TABLE AirConditioner ( 
Email varchar(50) NOT NULL, 
Appliance_order_num int NOT NULL, 
Energy_efficiency_ratio float NOT NULL, 
PRIMARY KEY (Email, Appliance_order_num), 
FOREIGN KEY (Email) REFERENCES Appliance (Email), 
FOREIGN KEY (Appliance_order_num) REFERENCES Appliance (Appliance_order_num) 
	ON DELETE CASCADE
); 

CREATE TABLE Heater ( 
Email varchar(50) NOT NULL, 
Appliance_order_num int NOT NULL, 
heater_energy_source char(50) NOT NULL, 
PRIMARY KEY (Email, Appliance_order_num), 
FOREIGN KEY (Email) REFERENCES Appliance (Email), 
FOREIGN KEY (Appliance_order_num) REFERENCES Appliance (Appliance_order_num)
	ON DELETE CASCADE, 
FOREIGN KEY (Heater_energy_source) REFERENCES HeaterEnergySourceType (HES_type) 
); 

CREATE TABLE HeaterEnergySourceType ( 
HES_type varchar(20) NOT NULL, 
PRIMARY KEY (HES_type) 
); 

CREATE TABLE HeatPump ( 
Email varchar(50) NOT NULL, 
Appliance_order_num int NOT NULL, 
seasonal_efficiency_ratio float NOT NULL, 
heat_performance_factor float NOT NULL, 
PRIMARY KEY (Email, Appliance_order_num), 
FOREIGN KEY (Email) REFERENCES Appliance (Email), 
FOREIGN KEY (Appliance_order_num) REFERENCES Appliance (Appliance_order_num) 
	ON DELETE CASCADE
); 

CREATE TABLE WaterHeater ( 
Email varchar(50) NOT NULL, 
Appliance_order_num int NOT NULL, 
Capacity float NOT NULL, 
Current_temp_setting int NULL, 
waterheater_energy_source char(50) NOT NULL, 
PRIMARY KEY (Email, Appliance_order_num), 
FOREIGN KEY (Email) REFERENCES Household (Email), 
FOREIGN KEY (Appliance_order_num) REFERENCES Appliance (Appliance_order_num)
	ON DELETE CASCADE, 
FOREIGN KEY (waterheater_energy_source) REFERENCES WaterHeaterEnergySourceType (WHES_type) 
); 

CREATE TABLE WaterHeaterEnergySourceType ( 
WHES_type varchar(20) NOT NULL, 
PRIMARY KEY (WHES_type) 
); 

CREATE TABLE PowerGenerator ( 
Email varchar(50) NOT NULL, 
Power_order_num int NOT NULL, 
Generation_type char(50) NOT NULL, 
Battery_storage int NULL, 
Avg_kwh int NOT NULL, 
PRIMARY KEY (Email, Power_order_num), 
FOREIGN KEY (Email) REFERENCES Household (Email), 
FOREIGN KEY (Generation_type) REFERENCES PowerGenType (Power_gen_type) 
); 

CREATE TABLE PowerGenType ( 
Power_gen_type varchar(20) NOT NULL, 
PRIMARY KEY (Power_gen _type) 
); 

CREATE TABLE Manufacturer ( 
Name varchar(50) NOT NULL, 
PRIMARY KEY (Name) 
);  

CREATE TABLE PostalCode ( 
Zip_code int NOT NULL, 
City char(50) NOT NULL, 
State char(50) NOT NULL, 
Latitude float NOT NULL, 
Longitude float NOT NULL, 
PRIMARY KEY (Zip_code) 
); 