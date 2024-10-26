// Set Trigger number to 1 and clear Auto-trigger with local busy set
W 3C 4 02 01

// Clear circular buffer
W 3C 14

// Read back trigger status
R 3C 4

// Read back buffer status
R 3C 14

// Start server DAQ
// first  data: 00-FF
// second data: CAL=0C, DAQ=0D 
W JMDC:SELF 1F0600 03 0D

// Set local busy to 0 to enable trigger coming
W 3C 4 00 01

// Read back trigger status
R 3C 4

