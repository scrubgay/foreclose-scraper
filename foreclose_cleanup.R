# foreclose_cleanup.r
# Cleans up the output from foreclose_parser.py

library(tidyverse)
library(lubridate)
library(fs)

fc <- read_csv("./output/foreclosure-data.csv")

parcels <- read_csv("./data/PublicParcels.csv") %>%
  select(c(Name, X_CENTER, Y_CENTER)) %>%
  distinct(Name, .keep_all = TRUE)

addresses <- read_csv("./data/Address_Points.csv") %>% 
  filter(PLACE_TYPE %in% c("COMMERCIAL", "RESIDENTIAL", "COMMERCIAL PRIMARY, RESIDENTIAL PRIMARY, NONLIVABLE STRUCTURE")) %>%
  arrange(desc(PLACE_TYPE)) %>% 
  distinct(FULLADDR, .keep_all = TRUE) %>%
  select(c(FULLADDR:LST_TYPE, X_CENTER = X, Y_CENTER = Y)) %>%
  mutate(
    ADD_NUMBER = as.character(ADD_NUMBER), 
    LST_NAME_ALT = if_else(
      str_detect(LST_NAME, "^[0-9]"),
      str_remove_all(LST_NAME, "[^0-9]"),
      LST_NAME)
  ) %>%
  unite("FULLADDR", ADD_NUMBER, LST_PREDIR, LST_NAME, LST_TYPE, sep = " ", remove = FALSE, na.rm = TRUE) %>%
  unite("FULLADDR_ALT", ADD_NUMBER, LST_PREDIR, LST_NAME_ALT, LST_TYPE, sep = " ", remove = FALSE, na.rm = TRUE) %>%
  select(FULLADDR, FULLADDR_ALT, X_CENTER, Y_CENTER) %>%
  pivot_longer(c(FULLADDR, FULLADDR_ALT), names_to = "ADDR_TYPE", values_to = "ADDR") %>%
  distinct(ADDR, .keep_all = TRUE)

outputDir <- "./output/"

fc <- fc %>%
  mutate(
    `Auction Date` = mdy(`Auction Date`),
    `Auction Sold` = ifelse(str_detect(`Auction status/sold`, "^[0-9]"), `Auction status/sold` %>% str_remove(" ET"), NA) %>% mdy_hm(),
    `Auction Status` = ifelse(str_detect(`Auction status/sold`, "^[A-Za-z]"), `Auction status/sold`, "Sold"),
    `Plaintiff Max Bid` = ifelse(str_detect(`Plaintiff Max Bid`, "Hid"), NA, str_remove_all(`Plaintiff Max Bid`, "[^0-9.]")) %>% as.numeric(),
    `Assessed Value` = str_remove_all(`Assessed Value`, "[^0-9.]") %>% as.numeric(),
    `Final Judgment Amount` = str_remove_all(`Final Judgment Amount`, "[^0-9.]") %>% as.numeric(),
    `Property Address ZIP` = str_extract(`Property Address2`, "(?<=- )[0-9]*"),
    `Property Address2`= str_extract(`Property Address2`, ".*(?=-)"),
    Amount = str_remove_all(Amount, "[^0-9.]") %>% as.numeric(),
    `Case Year` = str_extract(`Case #`, "(?<=01 )[0-9]{4}") %>% as.numeric()
  ) %>%
  select(-c(`Auction status/sold`, `Auction Type`)) %>%
  relocate(c(`Auction Status`, `Auction Sold`), .before = Amount) %>%
  relocate(`Property Address ZIP`, .after = `Property Address2`) %>%
  relocate(`Case Year`, .after = `Case #`)

# write_csv(fc, path(outputDir, "foreclosures_cleaned.csv"), na = "", quote = "all")

fc_less <- fc %>%
  group_by(`Case #`) %>%
  filter(`Auction Date` == max(`Auction Date`)) %>%
  ungroup() %>%
  distinct() %>%
  arrange(`Auction Date`) 

# 1715

fc_less <- fc_less %>%
  left_join(parcels %>% select(c(Name, X_CENTER, Y_CENTER)), by = c("Parcel ID" = "Name")) %>%
  mutate(GEOCODE = "Parcel")

fc_geo <- fc_less %>% filter(!is.na(X_CENTER))
fc_ungeo <- fc_less %>% filter(is.na(X_CENTER)) %>%
  select(-contains("CENTER"))

fc_ungeo <- fc_ungeo %>% 
  left_join(addresses, by = c("Property Address" = "ADDR")) %>%
  mutate(GEOCODE = ADDR_TYPE,
         ADDR_TYPE = NULL)

fc_geo <- bind_rows(fc_geo, fc_ungeo %>% filter(!is.na(X_CENTER)))
fc_ungeo <- fc_ungeo %>%
  filter(is.na(X_CENTER))

write_csv(fc_geo, path(outputDir,"foreclosures_cleaned_geocoded.csv"), na = "", quote = "all")
write_csv(fc_ungeo, path(outputDir, "foreclosures_cleaned_notgeocoded.csv"), na = "", quote = "all")
