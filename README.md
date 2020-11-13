# Getz-Hubbard group
CSA project 

This folder provides all the necessary code to run the automatic fits and the analysis. Please download and unzip this folder. In addition, the necessary data (CSV file with incidence and mortality data) can be download from this [Dropbox folder](https://www.dropbox.com/sh/jous6hx5t72vjff/AABnFV_nUDt5vt0-NVZUqMENa?dl=1).

Once the data are downloaded, please unzip the data, add the folder to the Getz-Hubbard folder and make sure all the data are put into folder `CSA_120_days` such as:

```
Getz-Hubbard
    |--CSA_120_days
        |--xx.csv
        |--xx.csv
        |--xx.csv
            .
            .
            .
```

Open the terminal and run the following command to run the code. Please change the name of the CSV file according to your CSAs:
```
python AutoNMB.py --input_file ./CSA_120_days/Indianapolis_Carmel_Muncie_IN_day47.csv
```

For additional information on procedure and analysis, please read the [project guide](https://docs.google.com/document/d/1GF44ZtaOd41afMRhhlmjqKYxbi8JGJxU_kbhxQylSiM/edit?usp=sharing).
