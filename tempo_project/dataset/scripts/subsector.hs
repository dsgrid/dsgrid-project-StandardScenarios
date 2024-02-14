module Main where


import Data.List (intercalate)


main :: IO ()
main = writeFile "bin.csv" . unlines . ("id,name" :) $ row <$> bins
 

row :: (String, String, String, String, String) -> String
row (c, i, u, z, t) = intercalate "+" [c, i, u, z, t] <> "," <> clean ("Composition = " <> c <> ", Income = " <> i <> ", Urbanity = " <> u <> ", Class = " <> z <> ", Technology = " <> t)

clean :: String -> String
clean = show . fmap (\x -> if x == '_' then ' ' else x)

bins :: [(String, String, String, String, String)]
bins = (,,,,) <$> composition <*> income <*> urbanity <*> clazz <*> tech

composition :: [String]
composition =
  [
    "No_Drivers"
  , "Single_Driver"
  , "Some_Drivers_Smaller"
  , "Some_Drivers_Larger"
  ]

income :: [String]
income =
  [
    "Low_Income"
  , "Middle_Income"
  , "High_Income"
  ]

urbanity :: [String]
urbanity =
  [
    "Urban"
  , "Suburban"
  , "Second_City"
  , "Small_Town"
  , "Rural"
  ]

clazz :: [String]
clazz =
  [
    "Compact"
  , "Midsize"
  , "SUV"
  , "Pickup"
  ]

tech :: [String]
tech =
  [
    "BEV_100"
  , "BEV_300"
  , "BEV_500"
  ]
