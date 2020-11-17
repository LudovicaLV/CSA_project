#note that main_folder, filename, fold and datetime need to be changed 

#set the folder which contains the code and the CSV files as directory 
main_folder <- "..."
setwd(main_folder)

#from Python_CSA_project folder (Detroit as an example)
file_name <- "Detroit_Warren_Ann Arbor, MI_day50.csv"

#from Output folder (Detroit as an example)
fold <- "Detroit"
datetime <- "20201023103844"

#set the working directory to the output folder DateTime
setwd(paste(main_folder, "Output/", fold, "/", datetime, sep = ""))

#plot the incidence data: day 0-30
inc_data <- read.csv(paste(main_folder, file_name, sep = ""), header = FALSE)
rt <-  data.frame(t(inc_data))
v <- rt$X1
plot(c(0:30), v[1:31], type = "l", xlab = "Day (data collection)", ylab = "Moving average (inc. cases)")
#name: CSAname_cases

#read results of simulation, given the fit of phase 1
i <- 1
data_phase_1 <- list()
for (j in 1:200){
  data <- read.csv(paste(main_folder, "Output/", fold, "/", datetime, "/VTables/Phase_", i, "_Repeat_", j, ".csv", sep = ""), skip = 1)
  data_phase_1[[j]] <- data
}

#read results of the fits 
params <- read.csv(paste(main_folder, "Output/", fold, "/", datetime, "/results_log.csv", sep = ""))

#create vectors of error and basic parameters
error <- vector()
k <- vector()
c <- vector()
i <- vector()
p <- vector()
for (j in 1:200){
  d <- data_phase_1[[j]] 
  error <- c(error, d$ErrorFit[15])
  k <- c(k, params$kappa[j])
  c <- c(c, params$C_0[j])
  i <- c(i, params$I_0[j])
  p <- c(p, params$P_suc[j])
}

#plot error and threshold (20000)
plot(error)
abline (h = 20000, lty = 2)
#name: CSAname_error

#select indices of error below threshold and index of minimum error
ind_e <- which(error < 20000)
ind <- which(error == min(error))

#distribution of basic parameters (for error below threshold)
#with selected 4-tuple in red (minimum error)
hist(k[ind_e], xlab = "Value", main = "kappa", breaks = 10)
points(k[ind], 0, col = "red", pch = 19, cex = 2)
#name: CSAname_k
hist(c[ind_e], xlab = "Value", main = "C_init", breaks = 10)
points(c[ind], 0, col = "red", pch = 19, cex = 2)
#name: CSAname_c
hist(i[ind_e], xlab = "Value", main = "I_init", breaks = 10)
points(i[ind], 0, col = "red", pch = 19, cex = 2)
#name: CSAname_i
hist(p[ind_e], xlab = "Value", main = "p_suc", breaks = 10)
points(p[ind], 0, col = "red", pch = 19, cex = 2)
#name: CSAname_p

#read results of simulation, given the fit of phase 2 (and fixed basic parameters)
i <- 2
data_phase_2 <- list()
for (j in 1:200){
  data <- read.csv(paste(main_folder, "Output/", fold, "/", datetime, "/VTables/Phase_", i, "_Repeat_", j, ".csv", sep = ""), skip = 1)
  data_phase_2[[j]] <- data
}

#create vectors of error and social distancing parameters
error_2 <- vector()
sd_on <- vector()
sd_in <- vector()
sd_fn <- vector()
sd_sw <- vector()
for (j in 1:200){
  d <- data_phase_2[[j]] 
  error_2 <- c(error_2, d$ErrorFit[31])
  h <- j + 200
  sd_on <- c(sd_on, params$SocDist_on[h])
  sd_in <- c(sd_in, params$SocDist_init[h])
  sd_fn <- c(sd_fn, params$SocDist_fnl[h])
  sd_sw <- c(sd_sw, params$SocDist_switch[h])
}

#plot error and threshold (20000)
plot(error_2, ylab = "error")
abline (h = 20000, lty = 2)
#name: CSAname_error_2

#select indices of error below threshold and index of minimum error
ind_e <- which(error_2 < 20000)
ind2 <- which(error_2 == min(error_2))

#distribution of social distancing parameters (for error below threshold)
#with selected 4-tuple in red (minimum error)
hist(sd_on[ind_e], xlab = "Value", main = "SocDist_on", breaks = 10)
points(sd_on[ind2], rep(0, length(ind2)), col = "red", pch = 19, cex = 2)
#name: CSAname_son
hist(sd_in[ind_e], xlab = "Value", main = "SocDist_init", breaks = 10)
points(sd_in[ind2], rep(0, length(ind2)), col = "red", pch = 19, cex = 2)
#name: CSAname_sin
hist(sd_fn[ind_e], xlab = "Value", main = "SocDist_fnl", breaks = 10)
points(sd_fn[ind2], rep(0, length(ind2)), col = "red", pch = 19, cex = 2)
#name: CSAname_sfn
hist(sd_sw[ind_e], xlab = "Value", main = "SocDist_switch", breaks = 10)
points(sd_sw[ind2], rep(0, length(ind2)), col = "red", pch = 19, cex = 2)
#name: CSAname_ssw

#evaluate mean and sd of SR/(S + SR), 
#considering the best 20 fits (lowest 20 errors)
total_s <- list()
total_s[[1]] <- ss
n <- 1
ndx <- order(error_2)[1:20]
for (j in ndx){
  s <- data_phase_2[[j]]$S1
  sr <- data_phase_2[[j]]$SR7
  ss <- sr/(s+sr)
  total_s[[n]] <- ss
  n <- n + 1
}
m_tot <- vector()
sd_tot <- vector()
for (k in 1:length(total_s[[1]])){
  m <- vector()
  for (h in 1:length(total_s)){
    m <- c(m,total_s[[h]][k])
  }
  mm <- mean(m)
  sm <- sd(m)
  m_tot <- c(m_tot, mm)
  sd_tot <- c(sd_tot, sm)
}

#plot mean ± sd for SR/(S + SR)
plot(m_tot, type = "l", xlab = "Day", ylab = "Sr/(S+Sr)", main = fold)
points(m_tot + sd_tot, type = "l", col = "blue")
points(m_tot - sd_tot, type = "l", col = "blue")
#name: CSAname_s

#indices of best fit for phase 1 (ind) and phase 2 (ind2)
#(used to choose screenshot for analysis report)
print(ind)
print(ind2)
print(paste("Add screenshot: Phase_1_Repeat_", ind, "_CSAname", sep = ""))
print(paste("Add screenshot: Phase_2_Repeat_", ind2,  "_CSAname", sep = ""))

