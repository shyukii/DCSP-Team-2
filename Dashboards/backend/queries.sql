-- name: readiness-latest
SELECT DISTINCT ON (d.deviceid)
  d.devicename,
  dd.devicetimestamp,
  MAX(sd.value::float) FILTER (WHERE s.sensor = 'Soil Nitrogen')    AS nitrogen,
  MAX(sd.value::float) FILTER (WHERE s.sensor = 'Soil Phosphorus')  AS phosphorus,
  MAX(sd.value::float) FILTER (WHERE s.sensor = 'Soil Potassium')   AS potassium,
  MAX(sd.value::float) FILTER (WHERE s.sensor = 'Soil Moisture')    AS moisture
FROM sensordata sd
JOIN devicedata dd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
JOIN devicesensors ds ON sd.sensorid = ds.sensorid
JOIN devices d ON ds.deviceid = d.deviceid
WHERE dd.devicetimestamp >= NOW() - INTERVAL '12 hours'
  AND d.devicename ILIKE 'NDS%' -- 🔥 NDS tanks only
GROUP BY d.deviceid, d.devicename, dd.devicetimestamp
ORDER BY d.deviceid, dd.devicetimestamp DESC;

-- name: readiness-daily-quarters
SELECT
  d.devicename,
  DATE_TRUNC('day', dd.devicetimestamp) AS day,
  CASE
    WHEN EXTRACT(HOUR FROM dd.devicetimestamp) < 6 THEN 'Q1 (00–06)'
    WHEN EXTRACT(HOUR FROM dd.devicetimestamp) < 12 THEN 'Q2 (06–12)'
    WHEN EXTRACT(HOUR FROM dd.devicetimestamp) < 18 THEN 'Q3 (12–18)'
    ELSE 'Q4 (18–00)'
  END AS quarter,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Nitrogen')    AS nitrogen_avg,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Phosphorus')  AS phosphorus_avg,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Potassium')   AS potassium_avg,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Moisture')    AS moisture_avg
FROM sensordata sd
JOIN devicedata dd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
JOIN devicesensors ds ON sd.sensorid = ds.sensorid
JOIN devices d ON ds.deviceid = d.deviceid
WHERE dd.devicetimestamp >= NOW() - INTERVAL '7 days'
  AND d.devicename ILIKE 'NDS%' -- 🔥 NDS tanks only
GROUP BY d.devicename, day, quarter
ORDER BY d.devicename, day, quarter;

