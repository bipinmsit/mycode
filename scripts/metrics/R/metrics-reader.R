library(data.table)
library(ggplot2)
library(zoo)
library(anytime)
library(psych)
# Activate `rjson`
library(rjson)

#fname <- 'metrics.log'
#fname <- 'metrics-vimana-prod-photoscan-ubuntu1604-8x64x4-8.log'
#workflow_state_json_file = "workflow-state-golden_gate_tennis_court_2017_11_09.json"

create_metrics_plot <- function(metrics_fname, workflow_state_json_file, title) {
  md <- fread(metrics_fname, col.names = c('dt', 'key', 'value'))
  md$dt <- gsub('T', ' ', md$dt)
  md$dt <- gsub('Z', '', md$dt)
  md$key <- gsub(':', '', md$key)
  
  md$dt <- anytime(md$dt)
  
  mdw <- dcast(md, dt ~ key, value.var = 'value')
  mdw$cpu <- mdw$cpu/8
  mdw$cpu <- na.locf(mdw$cpu)
  mdw$gpu1 <- na.locf(mdw$gpu1)
  mdw$gpu2 <- na.locf(mdw$gpu2)
  mdw$gpu3 <- na.locf(mdw$gpu3)
  mdw$gpu4 <- na.locf(mdw$gpu4)
  
  mdw[, allgpu := (gpu1 + gpu2 + gpu3 + gpu4)/4]
  
  ggplot(mdw, aes(dt)) + 
    geom_line(aes(y = cpu, colour = "cpu")) + 
    geom_line(aes(y = gpu1, colour = "gpu1")) + 
    geom_line(aes(y = gpu2, colour = "gpu2")) + 
    geom_line(aes(y = gpu3, colour = "gpu3")) + 
    geom_line(aes(y = gpu4, colour = "gpu4")) + 
    geom_line(aes(y = gpu4, colour = "allgpu"))
  
  ggplot(mdw, aes(dt)) + 
    geom_line(aes(y = cpu, colour = "cpu")) + 
    geom_line(aes(y = gpu4, colour = "allgpu"))
  
  ggplot(mdw, aes(x=cpu)) + geom_histogram()
  
  ggplot(mdw, aes(x=gpu1+gpu2+gpu3+gpu4)) + geom_histogram()
  
  
  # Import data from json file
  workflow_state_json <- fromJSON(file=workflow_state_json_file)
  
  out <- matrix(NA, nrow=10, ncol=3)
  step_labels <- c()
  step_ticks <- c()
  i <- 0
  for (s in workflow_state_json$steps) {
    out[i, ] = c(s$name, s$start_time, s$end_time)
    #step_labels <- append(step_labels, c(paste('Start', s$name, sep='_'), paste('End', s$name, sep='_')))
    s$start_time <- gsub('ZUTC', '', s$start_time)
    s$start_time <- gsub('T', ' ', s$start_time)
    s$start_time <- as.POSIXct(anytime(s$start_time), origin="1960-01-01")
    s$end_time <- gsub('ZUTC', '', s$end_time)
    s$end_time <- gsub('T', ' ', s$end_time)
    s$end_time <- as.POSIXct(anytime(s$end_time), origin="1960-01-01")
    #step_ticks <- append(step_ticks, c(s$start_time, s$end_time))
    if ((difftime(s$end_time, s$start_time, units = 'secs') > 6000) & (s$name != 'BuildDEM')) {
      step_labels <- append(step_labels, c(paste(s$name, round(difftime(s$end_time, s$start_time, units = 'hours')), 'Hrs', sep=' ')))
      step_ticks <- append(step_ticks, c(s$end_time))
    }
    i <- i + 1
  }
  
  step_times <- data.table(out)
  names(step_times) <- c('step', 'start_time', 'end_time')
  
  step_times$start_time <- gsub('ZUTC', '', step_times$start_time)
  step_times$start_time <- gsub('T', ' ', step_times$start_time)
  step_times$start_time <- anytime(step_times$start_time)
  
  step_times$end_time <- gsub('ZUTC', '', step_times$end_time)
  step_times$end_time <- gsub('T', ' ', step_times$end_time)
  step_times$end_time <- anytime(step_times$end_time)
  
  ggplot(mdw, aes(dt)) + 
    geom_line(aes(y = cpu, colour = "cpu")) + 
    geom_line(aes(y = gpu4, colour = "allgpu")) +
    scale_x_datetime(breaks = step_ticks, labels = step_labels) +
    theme(axis.text.x = element_text(angle = c(45), hjust = c(1))) + 
    ggtitle(title) +
    ylab("CPU/GPU Usage (%)")
}

metrics_fname <- 'golden_gate_construction_site_2017-11-9-metrics.log'
workflow_state_json_file <- 'workflow-state-golden_gate_construction_site_2017_11_09.json'
title <- "Golden Gate Construction Site - Photogrammetry CPU/GPU Usage (10-11 Nov 2017)"

create_metrics_plot(metrics_fname, workflow_state_json_file, title)