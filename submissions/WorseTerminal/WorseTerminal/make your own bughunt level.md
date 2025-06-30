# Make Your Own Bughunt Level

## Step 1  
Create a `bughunt.ini` file

---

## Step 2  
Each level should start with an open bracket, the word `Level`, the level number, and a close bracket.

**Example:**
```
[Level 1]
```

---

## Step 3  
Add the coding language that this level will be written in by entering a new line and typing:  
`language = language name here`

**Example:**
```
[Level 1]
language = python
```

---

## Step 4  
Type `code =`, enter a new line, and paste your code snippet.

**Example:**
```
[Level 1]
language = python
code = 
def add(a, b):
    return a - b
```

---

## Step 5  
Add an indent or press tab for every line of code after `code =`

**Example:**
```
[Level 1]
language = python
code = 
    def add(a, b):
        return a - b
```

---

## Step 6  
Replace all **EXTRA** tabs (those inside the code) with `<tab>`

**Example:**
```
[Level 1]
language = python
code = 
    def add(a, b):
    <tab>return a - b
```

---

## Step 7  
Add the hint by typing `hint = type hint here` on a new line

**Example:**
```
[Level 1]
language = python
code = 
    def add(a, b):
    <tab>return a - b
hint = Check the operator used in the return statement.
```

---

## Step 8  
Type keywords that should be in a sentence for the answer to be considered correct by typing:  
`answerkeywords = answer keywords here`

**Example:**
```
[Level 1]
language = python
code = 
    def add(a, b):
    <tab>return a - b
hint = Check the operator used in the return statement.
answerkeywords = addition, add, plus, sum, mistake, operator, incorrect, invert, subtract, subtracting, subtraction, adding, opposite
```

---

## Step 9  
Add the explanation of why it is correct by typing:  
`explanation = explanation here`

**Example:**
```
[Level 1]
language = python
code = 
    def add(a, b):
    <tab>return a - b
hint = Check the operator used in the return statement.
answerkeywords = addition, add, plus, sum, mistake, operator, incorrect, invert, subtract, subtracting, subtraction, adding, opposite
explanation = The function is supposed to add two numbers, but it's subtracting them instead. Just change the minus sign to a plus.
```

---

## Step 10  
Repeat!

**Example:**
```
[Level 5]
language = java
code =
    public class Main {
    <tab>public static void main(String[] args) {
    <tab><tab>System.out.println("Hello world);
    <tab>}
    }
hint = String literals need proper ending.
answerkeywords = syntax, missing quote, quotes, string, delimiter, unclosed
explanation = The string is missing the closing quote. Java needs both quotes to know where the text ends.
```
