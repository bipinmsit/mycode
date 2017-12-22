library(data.table)
library(ggplot2)
library(reshape2)

bds <- fread('border-depth-samples.csv')
head(bds)

plot(bds)
hist(bds$`16june`)
hist(bds$`20may`)
hist(bds$`29apr`)

meltdepth <- melt(bds)

ggplot(data = melt(meltdepth), mapping = aes(x = value)) + 
  geom_histogram(bins = 10) + facet_wrap(~variable, scales = 'free_x')

