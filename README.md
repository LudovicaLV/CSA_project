# Getz-Hubbard group
CSA project 

This folder provides all the necessary code to run the automatic fits and the analysis. The necessary data (CSV file with incidence and mortality data) can be download from this [Dropbox folder](https://www.dropbox.com/sh/jous6hx5t72vjff/AABnFV_nUDt5vt0-NVZUqMENa?dl=1).

Once the data are downloaded, please unzip the data, make sure all the data are put into folder `CSA_120_days` such as:

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

Example command to run the code:
```
python AutoNMB.py --input_file ./CSA_120_days/Indianapolis_Carmel_Muncie,\ IN_day47.csv
```
!!!!NOTE!!!!
You need to put `\` before the space charactors. (this way of filenaming should be changed in the future to avoid this kind of issue.)

For additional information on procedure and analysis, please read the [project guide](https://docs.google.com/document/d/1GF44ZtaOd41afMRhhlmjqKYxbi8JGJxU_kbhxQylSiM/edit?usp=sharing).
