print("1-Addition")
print("2-Substraction")
print("3-Multiplication")
print("4-Division")
option=int(input("Choose an operation:"))
if (option in [1,2,3,4]):
    num1=int(input("Enter the first number:"))
    num2=int(input("Enter the second number:"))
if (option==1):
    result=num1+num2
elif (option==2):
    result=num1-num2
elif (option==3):
    result=num1*num2
elif (option==4):
    result=num1/num2
else:
    print("Invalid operation entered")
print(f"The result of the operation is: {result}")
print("Thanks for using my project")