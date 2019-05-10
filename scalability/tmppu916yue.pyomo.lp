\* Source Pyomo model name=unknown *\

min 
x9:
-32.508250054108998 x5
-33.354379041978234 x6
-33.029952727787645 x7
+39.49521539200083 x8
+ [
+2 x5 ^ 2
+2 x6 ^ 2
+2 x7 ^ 2
+2 x8 ^ 2
] / 2
+1205.037684729215 ONE_VAR_CONSTANT

s.t.

c_e_x10_:
+5 x1
+1 x5
= 12.179975417018174

c_e_x11_:
+5 x2
+1 x6
= 11.087713767796362

c_e_x12_:
+5 x3
+1 x7
= 10.443982301303347

c_e_x13_:
+5 x4
+1 x8
= 15.543452507536381

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= x1 <= 1
   0 <= x2 <= 1
   0 <= x3 <= 1
   0 <= x4 <= 1
    -inf <= x5 <= +inf
    -inf <= x6 <= +inf
    -inf <= x7 <= +inf
    -inf <= x8 <= +inf
binary
  x1
  x2
  x3
  x4
end
