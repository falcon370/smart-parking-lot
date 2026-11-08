# Sample Input and Output

A complete session, starting from an empty database. Input typed by the user comes after each `:` prompt. To show realistic fees, the times were simulated: the car stays 2h 15m and the bike stays 13h 30m. In normal use the system clock is used. The menu is printed before every choice but is shown only once below.

```
========= SMART PARKING LOT =========
1. Park vehicle
2. Remove vehicle (pay and get receipt)
3. Show slot availability
4. Show parked vehicles
5. Show payment history
6. Export payments to CSV
7. Exit
=====================================
```

## 1. Parking vehicles (valid input)

```
Enter choice: 1
Vehicle type (car/bike): car
Plate number: ka01ab1234
Owner name (optional): Ravi Kumar
Car KA01AB1234, owner Ravi Kumar parked in slot 1.

Enter choice: 1
Vehicle type (car/bike): bike
Plate number: TN09XY7777
Owner name (optional):
Bike TN09XY7777 parked in slot 6.
```

The plate number is converted to upper case automatically.

## 2. Invalid input and operations

```
Enter choice: 1
Vehicle type (car/bike): car
Plate number: KA01AB1234
Owner name (optional):
Error: KA01AB1234 is already parked.

Enter choice: 1
Vehicle type (car/bike): truck
Plate number: AB1234
Owner name (optional):
Error: Unknown vehicle type 'truck'. Choose: car, bike.

Enter choice: 1
Vehicle type (car/bike): car
Plate number: !!
Owner name (optional):
Error: Plate number must be 4-12 characters: letters, digits or '-'.

Enter choice: 9
Invalid choice. Please enter a number from 1 to 7.
```

## 3. Availability and parked vehicles

```
Enter choice: 3
Car   slots: 4/5 free [2, 3, 4, 5]
Bike  slots: 4/5 free [7, 8, 9, 10]

Enter choice: 4
Slot Plate         Type  Owner               Entry time
1    KA01AB1234    car   Ravi Kumar          2026-11-08 10:00:00
6    TN09XY7777    bike  -                   2026-11-08 10:05:00
```

## 4. Removing vehicles and receipts

The car is charged 3 started hours × Rs. 20 = Rs. 60. The bike's 14 started hours × Rs. 10 = Rs. 140 is capped at the bike daily maximum of Rs. 100.

```
Enter choice: 2
Plate number: KA01AB1234

------- PARKING RECEIPT -------
Receipt No : 1
Vehicle    : KA01AB1234 (car)
Slot       : 1
Entry      : 2026-11-08 10:00:00
Exit       : 2026-11-08 12:15:00
Duration   : 2h 15m
Amount     : Rs. 60.00
-------------------------------
Receipt saved to ...\receipts

Enter choice: 2
Plate number: TN09XY7777

------- PARKING RECEIPT -------
Receipt No : 2
Vehicle    : TN09XY7777 (bike)
Slot       : 6
Entry      : 2026-11-08 10:05:00
Exit       : 2026-11-08 23:35:00
Duration   : 13h 30m
Amount     : Rs. 100.00
-------------------------------
Receipt saved to ...\receipts

Enter choice: 2
Plate number: NOPE123
Error: No active parking record for NOPE123.
```

## 5. Payment history and CSV export

```
Enter choice: 5
No  Plate         Type  Slot Duration  Amount
1   KA01AB1234    car   1    2h 15m    Rs. 60.00
2   TN09XY7777    bike  6    13h 30m   Rs. 100.00
Total collected: Rs. 160.00

Enter choice: 6
Exported 2 payment(s) to ...\payments.csv

Enter choice: 7
Goodbye!
```

## 6. Files written

`receipts/receipt_2.txt`

```
------- PARKING RECEIPT -------
Receipt No : 2
Vehicle    : TN09XY7777 (bike)
Slot       : 6
Entry      : 2026-11-08 10:05:00
Exit       : 2026-11-08 23:35:00
Duration   : 13h 30m
Amount     : Rs. 100.00
-------------------------------
```

`payments.csv`

```
payment_id,plate_number,vehicle_type,slot_id,entry_time,exit_time,amount
1,KA01AB1234,car,1,2026-11-08 10:00:00,2026-11-08 12:15:00,60.00
2,TN09XY7777,bike,6,2026-11-08 10:05:00,2026-11-08 23:35:00,100.00
```
