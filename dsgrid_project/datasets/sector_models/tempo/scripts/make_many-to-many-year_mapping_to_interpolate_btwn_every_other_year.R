library(tidyverse)
many_to_many <- tibble(from_id = c(rep(seq(2020, 2048, by = 2), each = 3), 2018, 2018, 2050, 2050) %>% sort(),
       to_id = c(rep(seq(2019, 2049, by = 2), each = 2), seq(2018,2050,by=2)) %>% sort(),
       fraction = c(rep(c(1,0.5,0.5), times = (2050-2018)/2), 1))
write_csv(many_to_many, "model_year_to_model_year.csv")
