# to run: Rscript generate_lineups.R '2016_07_09' 'early' 10 'fanduel' 
require(lpSolve)
require(data.table)

args <- commandArgs(trailingOnly = TRUE)

num_gen <- as.numeric(args[3])
site <- args[4]
file_name <- paste(args[1], '_', args[2], sep='')

data_loc <- paste("./simplified_projections/", site, "_", file_name, ".csv", sep='')
output_loc <- paste("./lineups/", site, "_", file_name, "_linear.csv", sep='')
output_loc_ext <-paste("./lineups/", site, "_", file_name, "_ext.csv", sep='')

#setup data
df <- fread(data_loc)
mm <- cbind(
  ifelse(grepl("P", df$pos), 1, 0), ifelse(grepl("C", df$pos), 1, 0), ifelse(grepl("SS", df$pos), 1, 0),
  ifelse(grepl("1B", df$pos), 1, 0), ifelse(grepl("2B", df$pos), 1, 0), ifelse(grepl("3B", df$pos), 1, 0),
  ifelse(grepl("OF", df$pos), 1, 0), df$cost, df$mean,
  ifelse(df$team=='BAL', 1, 0), ifelse(df$team=='BOS', 1, 0), ifelse(df$team=='TOR', 1, 0), ifelse(df$team=='NYY', 1, 0), ifelse(df$team=='TBR', 1, 0),
  ifelse(df$team=='CLE', 1, 0), ifelse(df$team=='DET', 1, 0), ifelse(df$team=='KCR', 1, 0), ifelse(df$team=='CWS', 1, 0), ifelse(df$team=='MIN', 1, 0),
  ifelse(df$team=='TEX', 1, 0), ifelse(df$team=='SEA', 1, 0), ifelse(df$team=='HOU', 1, 0), ifelse(df$team=='LAA', 1, 0), ifelse(df$team=='OAK', 1, 0),
  ifelse(df$team=='WAS', 1, 0), ifelse(df$team=='NYM', 1, 0), ifelse(df$team=='MIA', 1, 0), ifelse(df$team=='PHI', 1, 0), ifelse(df$team=='ATL', 1, 0),
  ifelse(df$team=='CHC', 1, 0), ifelse(df$team=='PIT', 1, 0), ifelse(df$team=='STL', 1, 0), ifelse(df$team=='MIL', 1, 0), ifelse(df$team=='CIN', 1, 0),
  ifelse(df$team=='SFG', 1, 0), ifelse(df$team=='LAD', 1, 0), ifelse(df$team=='COL', 1, 0), ifelse(df$team=='ARI', 1, 0), ifelse(df$team=='SDP', 1, 0))
colnames(mm) <- c(
  "P", "C", "SS", "1B", "2B", "3B", "OF", "cost", "mean", 
  "BAL", "BOS", "TOR", "NYY", "TBR", "CLE", "DET", "KCR", "CWS", "MIN",
  "TEX", "SEA", "HOU", "LAA", "OAK", "WAS", "NYM", "MIA", "PHI", "ATL",
  "CHC", "PIT", "STL", "MIL", "CIN", "SFG", "LAD", "COL", "ARI", "SDP")

#setup solver
mm <- t(mm)
# print(mm)
obj <- df$mean

dir <- c('=', '=', '=', '=', '=', '=', '=', '<=', '<=',
         '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=',
         '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=',
         '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=', '<=')

x <- 20000
if (site == 'fanduel') {
  lineups.frame = as.data.frame(matrix(ncol=10, nrow=num_gen))
  # lineups_ext.frame = as.data.frame(matrix(ncol=5, nrow=num_gen * 10))
  names(lineups.frame) = c("P", "C", "SS", "1B", "2B", "3B", "OF", "OF", "OF", "Points")
} else {
  # lineups_ext.frame = as.data.frame(matrix(ncol=5, nrow=num_gen * 11))
  lineups.frame = as.data.frame(matrix(ncol=11, nrow=num_gen))
  names(lineups.frame) = c("P", "P", "C", "SS", "1B", "2B", "3B", "OF", "OF", "OF", "Points")
}
# names(lineups_ext.frame) = c("name", "pos", "mean", "cost", "team")
vals <- c()
ptm <- proc.time()
for(i in 1:num_gen){
  if (site == 'fanduel') {
    rhs <- c(1, 1, 1, 1, 1, 1, 3, 35000, x,
      4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 
      4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 
      4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
  } else {
    rhs <- c(2, 1, 1, 1, 1, 1, 3, 50000, x,
      5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
      5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
      5, 5, 5, 5, 5, 5, 5, 5, 5, 5)
  }
  lp <- lp(direction = 'max',
           objective.in = obj,
           all.bin = T,
           const.rhs = rhs,
           const.dir = dir,
           const.mat = mm)
  idxs <- which(lp$solution %in% c(1))
  short_dat <- df[idxs]
  # max_team_count <- sort(rle(sort(short_dat$))$lengths, decreasing=TRUE)[1]
  names <- unique(c(short_dat[grepl('P', pos),]$name, short_dat[pos=='C']$name, short_dat[pos=='SS']$name, short_dat[pos=='1B']$name, short_dat[pos=='2B']$name, short_dat[pos=='3B']$name, short_dat[pos=='OF']$name))

  # if (site == 'fanduel') {
  #   for(j in 0:9)
  #     lineups_ext.frame[i + j * 10,] = short_dat[i,]
  # } else {
  #   names <- c(short_dat[pos=='P']$name, short_dat[pos=='C']$name, short_dat[pos=='SS']$name, short_dat[pos=='1B']$name, short_dat[pos=='2B']$name, short_dat[pos=='3B']$name, short_dat[pos=='OF']$name, lp$objval)
  #   for(j in 0:10)
  #     lineups_ext.frame[i + j * 11,] = short_dat[i,]
  # }
  lineups.frame[i,] = c(names, lp$objval)
  vals <- c(vals, lp$objval)
  x <- lp$objval - 0.00001
}
write.csv(output_loc, x=lineups.frame)
# write.csv(output_loc_ext, x=lineups_ext.frame)
print(lineups.frame)
proc.time() - ptm