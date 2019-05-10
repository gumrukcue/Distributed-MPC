\* Source Pyomo model name=unknown *\

min 
x17:
+1 x10
+1 x11
+1 x12
+1 x13
+1 x14
+1 x15
+1 x16
+1 x9

s.t.

c_e_x18_:
-4.5965532813381813 x1
+1 x9
= 0

c_e_x19_:
+1 x10
-4.7985967670923628 x2
= 0

c_e_x20_:
+1 x11
-4.8627992083453968 x3
= 0

c_e_x21_:
+1 x12
+7.5054746938049028 x4
= 0

c_e_x22_:
+1 x13
-4.5965532813381813 x5
= 0

c_e_x23_:
+1 x14
-4.7985967670923628 x6
= 0

c_e_x24_:
+1 x15
-4.8627992083453968 x7
= 0

c_e_x25_:
+1 x16
+7.5054746938049028 x8
= 0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= x1 <= 1
   0 <= x2 <= 1
   0 <= x3 <= 1
   0 <= x4 <= 1
   0 <= x5 <= 1
   0 <= x6 <= 1
   0 <= x7 <= 1
   0 <= x8 <= 1
    -inf <= x9 <= +inf
    -inf <= x10 <= +inf
    -inf <= x11 <= +inf
    -inf <= x12 <= +inf
    -inf <= x13 <= +inf
    -inf <= x14 <= +inf
    -inf <= x15 <= +inf
    -inf <= x16 <= +inf
binary
  x1
  x2
  x3
  x4
  x5
  x6
  x7
  x8
end
