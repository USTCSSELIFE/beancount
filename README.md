# beancount
Beancount Importer of USTC for E-card Transaction

## Usage
### 1. Fill in the Configurations
### 2. Get Data from E-card Website
```python3
 python3 main.py
```
generate xxx.csv
### 3. Import Data to Beancount
```shell
bean-extract importer.py xxx.csv
```
