// Stop trigger by set local busy to 1
W 3C 4 02 01

// Read back trigger status
R 3C 4

// Read back buffer status
R 3C 14

// Stop server DAQ
W JMDC:SELF 1F0601

