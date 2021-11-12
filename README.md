# A comparison of COVID-19 outbreaks across US Combined Statistical Areas using new methods for estimating R_0 and social distancing

This folder provides all the necessary code to run the automatic fits and the analysis. Please download and unzip this folder. In addition, download the data (CSV file with incidence and mortality data) from this [Dropbox folder](https://www.dropbox.com/sh/jous6hx5t72vjff/AABnFV_nUDt5vt0-NVZUqMENa?dl=1).

Once the data are downloaded, please unzip the folder and add it to the Python_CSA_project folder. Make sure all the data are put into folder `CSA_120_days` such as:

```
Python_CSA_project
    |--CSA_120_days
        |--xx.csv
        |--xx.csv
        |--xx.csv
            .
            .
            .
```

Open the terminal, navigate to the Python_CSA_project folder (using “cd” command) and run the following command to run the code. Please change the name of the CSV file according to your CSAs:
```
python AutoNMB.py --input_file ./CSA_120_days/Indianapolis_Carmel_Muncie_IN_day47.csv
```

For additional information on procedure and analysis, please read the [project guide](https://ludovicalv.github.io/PDFs/SOF2_CSA.pdf).
