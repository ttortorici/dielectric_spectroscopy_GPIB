dielectric_spectroscopy_GPIB

Run measurement_server.py to open communication with GPIB.

Send strings to the server and it will parse and communicate with GPIB instruments.

"XX::YY::msg"
  -- where XX is instrument ID (eg 'AH' for AH2700A bridge, 'HP' for HP4275 bridge, 'LS' will communicate with whichever lakeshore is loaded)
  -- where YY is 'WR' to write to the instrument, and 'QU' queries the instrument (when you want a response from your write)
  -- msg is the string sent to the instrument.
  
In measurment_tools.py there is a definition called send(msg, port)
  -- where msg is the message to send to the server (in the format above)
  -- and port is the port number the server is using.
