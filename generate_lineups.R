require(lpSolve)
require(data.table)

num_gen <- 10
site <- 'fanduel'
file_name <- '2016_07_08_main'

data_loc <- paste("./simplified_projections/", site, "_", file_name, ".csv", sep='')
output_loc <- paste("./lineups/", site, "_", file_name, ".csv", sep='')
output_loc_ext <-paste("./lineups/", site, "_", file_name, "_ext.csv", sep='')

#setup data
df <- fread(data_loc)
print(df)
mm <- cbind(ifelse(grepl("P", df$pos), 1, 0), ifelse(grepl("C", df$pos), 1, 0), ifelse(grepl("SS", df$pos), 1, 0), ifelse(grepl("1B", df$pos), 1, 0), ifelse(grepl("2B", df$pos), 1, 0), ifelse(grepl("3B", df$pos), 1, 0), ifelse(grepl("OF", df$pos), 1, 0), df$cost, df$mean)
colnames(mm) <- c('P', 'C', 'SS', '1B', '2B', '3B', 'OF', "cost", "mean")

print(mm)
#setup solver
mm <- t(mm)
# print(mm)
obj <- df$mean

dir <- c('=', '=', '=', '=', '=', '=', '=', '<=', '<=')

x <- 20000
if (site == 'fanduel') {
  lineups.frame = as.data.frame(matrix(ncol=10, nrow=num_gen))
  lineups_ext.frame = as.data.frame(matrix(ncol=5, nrow=num_gen * 10))
  names(lineups.frame) = c("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "Points")
} else {
  lineups_ext.frame = as.data.frame(matrix(ncol=5, nrow=num_gen * 11))
  lineups.frame = as.data.frame(matrix(ncol=11, nrow=num_gen))
  names(lineups.frame) = c("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "Points")
}
names(lineups_ext.frame) = c("name", "pos", "mean", "cost", "team")
vals <- c()
ptm <- proc.time()
for(i in 1:num_gen){
  if (site == 'fanduel') {
    rhs <- c(1, 1, 1, 3, 1, 1, 1, 35000, x)
  } else {
    rhs <- c(1, 1, 1, 3, 2, 1, 1, 50000, x)
  }
  lp <- lp(direction = 'max',
           objective.in = obj,
           all.bin = T,
           const.rhs = rhs,
           const.dir = dir,
           const.mat = mm)
  idxs <- which(lp$solution %in% c(1))
  short_dat <- df[idxs]
  names <- c(short_dat$name, lp$objval)
  lineups.frame[i,] = names
  if (site == 'fanduel') {
    for(j in 0:9)
      lineups_ext.frame[i + j * 10,] = short_dat[i,]
  } else {
    for(j in 0:10)
      lineups_ext.frame[i + j * 11,] = short_dat[i,]
  }

  vals <- c(vals, lp$objval)
  x <- lp$objval - 0.00001
}
write.csv(output_loc, x=lineups.frame)
write.csv(output_loc_ext, x=lineups_ext.frame)
print(lineups.frame)
proc.time() - ptm