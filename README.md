# ERDToSQL
## Input:
ERD as Hand-drawen image
![Flowchart8](https://github.com/islamshaabaan/ERDToSQL/assets/36308342/58f6606d-e324-46c0-940f-c2d6656bb232)

## Output:
SQL Queries like

  -  CREATE TABLE employee ( Ename CHAR(40) , SSID INT(20) PRIMARY KEY AUTO_INCREMENT);
  -  CREATE TABLE Department ( Dname INT(20) PRIMARY KEY AUTO_INCREMENT, location CHAR(40) , manager CHAR(40) );
  -  ALTER TABLE employee ADD Dname_fk SMALLINT UNSIGNED NOT NULL DEFAULT 0;
  -  ALTER TABLE employee ADD CONSTRAINT fk_Dname FOREIGN KEY (Dname_fk) REFERENCES Department(Dname);
