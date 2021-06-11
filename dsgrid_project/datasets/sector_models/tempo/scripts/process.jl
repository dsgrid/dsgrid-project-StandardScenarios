
using CSV
using DataFrames, DataFramesMeta
using Dates


function quantize(df :: AbstractDataFrame; dt = 1. :: Float64, tmax = 168. :: Float64)
  n = round(Int64, tmax / dt)
  ts = [
     Dates.format(DateTime(2021, 4, 19) + Dates.Second(floor(Int64, 3600 * t)), dateformat"u e HH:MM:SS")
     for t in 0:dt:(tmax-dt)
  ]
  es = Dict([
    "Electricity_Residential" => [0.0 for t in ts],
    "Electricity_Commercial"  => [0.0 for t in ts],
    "Electricity_DCFC"        => [0.0 for t in ts],
  ])
  ifloor(t) = floor(Int64, t / dt)
  iceil(t) = ceil(Int64, t / dt)
  for row in eachrow(df)
    t0 = row.Hour_of_Week
    t1 = t0 + row.TripDuration
    r = 33.7 * row.Weight * row.Charger_GGE / (t1 - t0) * dt
    i0 = ifloor(t0)
    es[row.Fuel][1 + i0 % n] += - (t0 - i0 * dt) / dt * r
    i1 = ifloor(t1)
    es[row.Fuel][1 + i1 % n] += (t1 - i1 * dt) / dt * r
    for i in i0:(i1-1)
      es[row.Fuel][1 + i % n] += r
    end
  end
  DataFrame(
    timestamp = ts,
    L1        = es["Electricity_Residential"],
    L2        = es["Electricity_Commercial" ],
    DCFC      = es["Electricity_DCFC"       ],
  )
end


z_raw = CSV.read("../tmp/household-ev-greedycharging.csv", types = Dict(:Region => String));
rename!(z_raw, Dict(:Region => :geography, :Year => :model_year))
z_raw |> names

z_key = [:geography, :model_year, :Season, :Composition, :Income, :Urbanity, :Class, :Tech]

z_unique = z_raw[:, z_key] |> unique;
z_unique |> nrow
z_unique.data_id = 1:nrow(z_unique)


z_lookup = @select(
  z_unique,
  :geography,
  :model_year,
  :Season,
  subsector = string.(
    :Composition,
    "+",
    :Income,
    "+",
    :Urbanity,
    "+",
    :Class,
    "+",
    :Tech,
  ),
  :data_id,
);


z_data = @linq join(z_raw, z_unique, on=z_key, kind=:inner) |>
  where(:Charger_GGE .!= 0) |>
  select(
    id = :data_id,
    :HouseholdID,
    :Vehicle_ID,
    :Hour_of_Week, 
    :TripDuration,
    :Charger_GGE,
    :Weight,
    :Fuel,
  ) |>
  groupby([:id, :HouseholdID, :Vehicle_ID]) |>
  combine(t -> quantize(t)) |>
  by(
    [:id, :timestamp],
    L1   = sum(:L1  ),
    L2   = sum(:L2  ),
    DCFC = sum(:DCFC),
  );


CSV.write("../tmp/household-ev-greedy.lookup.csv", z_lookup)

CSV.write("../tmp/household-ev-greedy.data.csv", z_data)
