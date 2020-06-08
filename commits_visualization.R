# install.packages("RPostgreSQL")
require("RPostgreSQL")
pw <- {
  "posgres123"
}
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "EnergyConsumption",
                 host = "localhost", port = 5432,
                 user = "postgres", password = pw)
rm(pw) # removes the password

dbExistsTable(con, "refactoring_data")

#dbDisconnect(con)

library(ggplot2)

df_all_data <- dbGetQuery(con, "SELECT * from app_data where commits is not null")
df_mobile_app <- subset(df_all_data,android_manifests_count > 0)


summary(df_mobile_app$commits)
aggregate(df_mobile_app$commits,FUN=median)

plot1<-ggplot(df_mobile_app, )+geom_boxplot(aes(y=commits)) +
  scale_y_log10() +
  labs(y="Number of commits",x="Mobile apps") 
print(plot1)
