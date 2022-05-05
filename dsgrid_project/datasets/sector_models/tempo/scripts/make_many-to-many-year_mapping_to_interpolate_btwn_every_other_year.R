library(tidyverse)
many_to_many <- tibble(from_id = c(rep(2018, 8), rep(seq(2020, 2048, by = 2), each = 3), 2018, 2018, 2050, 2050) %>% sort(),
       to_id = c(seq(2010, 2017, 1), rep(seq(2019, 2049, by = 2), each = 2), seq(2018,2050,by=2)) %>% sort(),
       fraction = c(rep(0, 8), rep(c(1,0.5,0.5), times = (2050-2018)/2), 1))
write_csv(many_to_many, "c:/users/ayip/documents/github/dsgrid-project-StandardScenarios/dsgrid_project/datasets/sector_models/tempo/dimension_mappings/model_year_to_model_year.csv")
