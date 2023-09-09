# ERDToSQL
## Input:
ERD as Hand-drawen image
## Output:
SQL Queries like:
  CREATE TABLE employee ( Ename CHAR(40) , SSID INT(20) PRIMARY KEY AUTO_INCREMENT);
  CREATE TABLE Department ( Dname INT(20) PRIMARY KEY AUTO_INCREMENT, location CHAR(40) , manager CHAR(40) );
  ALTER TABLE employee ADD Dname_fk SMALLINT UNSIGNED NOT NULL DEFAULT 0;
  ALTER TABLE employee ADD CONSTRAINT fk_Dname FOREIGN KEY (Dname_fk) REFERENCES Department(Dname);
