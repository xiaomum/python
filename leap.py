import datetime
def isLeapYear(y):
    return (y % 400==0 or (y % 4==0  and y % 100!=0))
dofm =[0,31,28,31,30,31,30,31,31,30,31,30,31]
res =0
year = int(input("year:"))
month = int(input("month:")
day = int(input("day:"))  # type: object
if isLeapYear(year):
    dofm[2] +=1
for i in range(month):
    res +=dofm[i]
print(res+day)

