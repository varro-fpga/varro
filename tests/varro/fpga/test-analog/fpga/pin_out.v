module test_analog (
digital0, digital1, digital2, digital3, digital4, digital5, digital6, digital7, digital8, digital9, digital10, digital11, analog0, analog1, analog2, analog3, analog4, analog5);

input digital0, digital1, digital2, digital3, digital4, digital5, digital6, digital7, digital8, digital9, digital10, digital11;
output analog0, analog1, analog2, analog3, analog4, analog5;

assign analog0 = digital0; 
assign analog1 = digital1; 
assign analog2 = digital2; 
assign analog3 = digital3; 
assign analog4 = digital4; 
assign analog5 = digital5 & digital6 & digital7 & digital8 & digital9 & digital10 & digital11; 

endmodule
