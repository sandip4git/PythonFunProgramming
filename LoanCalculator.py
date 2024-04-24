loanAmount=float(input("What is your loan amount\n"))
annualInterestRate=float(input("What is your annual interest rate\n"))
monthlyEMI=float(input("Your monthly EMI\n"))

monthlyInterestRate=annualInterestRate/12/100
print("monthly interest rate", monthlyInterestRate)
counter=1
remainingLoan=loanAmount
while remainingLoan > 0:    
    remainingLoan= (loanAmount + (loanAmount * monthlyInterestRate) - monthlyEMI)
    print("You paid EMI of", monthlyEMI, "remaining loan amount is", remainingLoan, "EMI number", counter)
    loanAmount=remainingLoan
    if loanAmount > 0:
        counter+=1

print("With current interest rate you need to pay", counter, "EMIs to payoff loan")
years = counter//12
months= counter%12
print("You will pay off your loan in", years, "years", "and", months, "months")
