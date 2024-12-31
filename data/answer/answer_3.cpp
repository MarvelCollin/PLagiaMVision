#include <iostream>
using namespace std;

int calculatePay(int basePay, int overtime, int bonus) {
  return (basePay * 0.3) + (overtime * 0.3) + (bonus * 0.4);
}

int main() {
  int basePay, overtime, bonus;

  cout << "Enter base pay: ";
  cin >> basePay;

  cout << "Enter overtime pay: ";
  cin >> overtime;

  cout << "Enter bonus amount: ";
  cin >> bonus;

  int totalPay = calculatePay(basePay, overtime, bonus);

  if (totalPay >= 9000)
    cout << "Salary: High";
  else if (totalPay >= 8000)
    cout << "Salary: Medium";
  else if (totalPay >= 7000)
    cout << "Salary: Low";
  else
    cout << "Salary: Entry";

  return 0;
}
