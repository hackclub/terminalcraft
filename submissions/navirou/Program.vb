Imports Microsoft.VisualBasic
Imports System
Imports System.Runtime.InteropServices.JavaScript
Imports System.Threading


Module Program
    
    Sub Main(args As String())
        
        
        dim menuOption as Integer
        dim modeSelector as string = "> start from random seed"
        
        Console.ForegroundColor = ConsoleColor.White
        
        Console.WriteLine("navirou")
        Console.WriteLine()
        Console.WriteLine("import level from seed")
        Console.WriteLine("> start from random seed")
        
        do 
            
            menuoption = Console.ReadKey().Key
            
            if menuOption = ConsoleKey.UpArrow or menuOption = ConsoleKey.W
                
                if Console.CursorTop = 3 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("import level from seed")
                    Console.WriteLine("> start from random seed")
                    Console.SetCursorPosition(0, 4)
                    modeSelector = "> start from random seed"
                elseif Console.CursorTop = 4 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("> import level from seed")
                    Console.WriteLine(" start from random seed")
                    Console.SetCursorPosition(0, 3)
                    modeSelector = "> import level from seed"
                End If
        
            End If
            
            if menuOption = ConsoleKey.DownArrow or menuOption = ConsoleKey.S
                
                if Console.CursorTop = 3 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("import level from seed")
                    Console.WriteLine("> start from random seed")
                    Console.SetCursorPosition(0, 4)
                    modeSelector = "> start from random seed"
                ElseIf Console.CursorTop = 4 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("> import level from seed")
                    Console.WriteLine(" start from random seed")
                    Console.SetCursorPosition(0, 3)
                    modeSelector = "> import level from seed"
                End If
        
            End If
            
        loop until menuOption = ConsoleKey.Enter
        
        if modeSelector = "> start from random seed"
            Console.Clear()
            RandomelevenByElevenGrid()
            ElseIf modeSelector = "> import level from seed"
                Console.Clear()
                seedElevenByElevenGrid()
        End If
        
    End Sub
    
    Sub RandomElevenByElevenGrid()
        
        Console.ForegroundColor = ConsoleColor.White
        
        console.WriteLine()
        Console.Write(" ")
        for a as Integer = 0 to 10
        for b as Integer = 0 to 10
            Console.Write("__")
            Threading.Thread.Sleep(10)
            Console.Write("|")
            
        Next
            Console.WriteLine()
            Console.Write(" ")
        next
        
        Console.ForegroundColor = ConsoleColor.Red
        Console.SetCursorPosition(16, 6)
        Console.Write("__")
        
        dim treasureLocationOkay as Boolean = False
        dim treasureLocationTop as Integer 
        dim treasureLocationLeft as Integer
        
        Console.ForegroundColor = ConsoleColor.Yellow
        
        do until treasureLocationOkay = True
            
            
            Randomize()
            treasureLocationLeft= Math.Ceiling(Rnd() * 30)
            Randomize()
            treasureLocationTop = Math.Ceiling(Rnd() * 10)
            
            
            if treasureLocationLeft mod 3 <> 0 and (treasureLocationLeft + 1) mod 3 <> 0 ' makes sure it isn't in a barrier
                if treasureLocationLeft <> 16 AndAlso treasureLocationTop <> 6 or  treasureLocationLeft <> 17 AndAlso  treasureLocationTop <> 6 ' makes sure it isn't on the user starting position
                treasureLocationOkay = true
                    else
                        treasureLocationOkay = false
                    End If
                Else 
                    treasureLocationOkay = false
            End If
                
            loop
        
        
        
        dim treasureFound as boolean = false
        Dim moveNumber As Integer = 0
        Dim numberOfSquaresAway as Integer
        dim trueTreasureLocationLeft as Integer 
        dim trueTreasureLocationTop as Integer
        dim userLocationLeft as Integer = 16
        dim userLocationTop as Integer = 6
        dim trueUserLocationLeft as Integer
        dim trueUserLocationTop as Integer
        dim noSquaresAwayLeft as Integer = Nothing
        dim noSquaresAwayTop as Integer = Nothing
        dim userDirection as Integer
        dim goingOutOfBounds as Boolean = false
        dim outOfBoundsPos(1)
        dim hotterOrColder as string
        
        If treasureLocationLeft = 1 or treasureLocationLeft = 2
            trueTreasureLocationLeft = 1
        ElseIf treasureLocationLeft = 4 or treasureLocationLeft = 5
            trueTreasureLocationLeft = 2
        ElseIf treasureLocationLeft = 7 or treasureLocationLeft = 8
            trueTreasureLocationLeft = 3
        ElseIf treasureLocationLeft = 10 or treasureLocationLeft = 11
            trueTreasureLocationLeft = 4
        ElseIf treasureLocationLeft = 13 or treasureLocationLeft = 14
            trueTreasureLocationLeft = 5
        ElseIf treasureLocationLeft = 16 or treasureLocationLeft = 17
            trueTreasureLocationLeft = 6
        ElseIf treasureLocationLeft = 19 or treasureLocationLeft = 20
            trueTreasureLocationLeft = 7
        ElseIf  treasureLocationLeft = 22 or treasureLocationLeft = 23
            trueTreasureLocationLeft = 8
        ElseIf treasureLocationLeft = 25 or treasureLocationLeft = 26
            trueTreasureLocationLeft = 9
        ElseIf treasureLocationLeft = 28 or treasureLocationLeft = 29
            trueTreasureLocationLeft = 10
        ElseIf treasureLocationLeft = 31 or treasureLocationLeft = 32
            trueTreasureLocationLeft = 11
        End If
            
        trueTreasureLocationTop = treasureLocationtop
        
        If UserLocationLeft = 1 or UserLocationLeft = 2
            trueUserLocationLeft = 1
        ElseIf UserLocationLeft = 4 or UserLocationLeft = 5
            trueUserLocationLeft = 2
        ElseIf UserLocationLeft = 7 or UserLocationLeft = 8
            trueUserLocationLeft = 3
        ElseIf UserLocationLeft = 10 or UserLocationLeft = 11
            trueUserLocationLeft = 4
        ElseIf UserLocationLeft = 13 or UserLocationLeft = 14
            trueUserLocationLeft = 5
        ElseIf UserLocationLeft = 16 or UserLocationLeft = 17
            trueUserLocationLeft = 6
        ElseIf UserLocationLeft = 19 or UserLocationLeft = 20
            trueUserLocationLeft = 7
        ElseIf  UserLocationLeft = 22 or UserLocationLeft = 23
            trueUserLocationLeft = 8
        ElseIf UserLocationLeft = 25 or UserLocationLeft = 26
            trueUserLocationLeft = 9
        ElseIf UserLocationLeft = 28 or UserLocationLeft = 29
            trueUserLocationLeft = 10
        ElseIf UserLocationLeft = 31 or UserLocationLeft = 32
            trueUserLocationLeft = 11
        End If
            
        trueUserLocationTop = UserLocationTop
        
      dim firstmove as Boolean = true
      dim triggerMovement as boolean = true  
        dim seedNumberRandom(2) as Integer
        dim leftZeroFiller as Integer = 0
        dim topZeroFiller as Integer = 0
        
           seedNumberRandom(1) = trueTreasureLocationLeft * 69
        seedNumberRandom(2) = trueTreasureLocationTop * 69
        
        ' the following code checks whether the seed for a given axis is a 2 digit number. it will be if one of the locations are 0.
        ' it adds an extra 0 where needed, whist the last 2 digits of the seed now mean when the seed is parsed, it
        ' knows when 690 = 690 and when 690 is actually 69 but aligned to fit the seed requirements.
        
        if seedNumberRandom(1).ToString().Length = 2
            seedNumberRandom(1) = seedNumberRandom(1) & 0
            leftZeroFiller = 1
        End If
        
        if seedNumberRandom(2).ToString().Length = 2
           seedNumberRandom(2) = seedNumberRandom(2) & 0
            topZeroFiller = 1
            End If
        
        
           seedNumberRandom(0) = seedNumberRandom(1) & seedNumberRandom(2)
        
        if leftZeroFiller = 1 AndAlso topZeroFiller = 1
            seedNumberRandom(0) = seedNumberRandom(0) & 1 & 1
        End If
        
        if leftZeroFiller = 0 AndAlso topZeroFiller = 1
            seedNumberRandom(0) = seedNumberRandom(0) & 0 & 1
        End If
        
        if leftZeroFiller = 1 AndAlso topZeroFiller = 0
            seedNumberRandom(0) = seedNumberRandom(0) & 1 & 0
        End If
        
        if leftZeroFiller = 0 AndAlso topZeroFiller = 0
            seedNumberRandom(0) = seedNumberRandom(0) & 0 & 0
        End If
        
        do until treasureFound = True
            
            
            
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
                else
                    noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
            if trueTreasureLocationTop > trueUserLocationTop
                noSquaresAwayTop = trueTreasureLocationTop - trueUserLocationTop
            else
                noSquaresAwayTop = trueUserLocationTop - trueTreasureLocationTop
            End If
            
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
                else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                    hotterOrColder = "colder"
                    ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                        
            End If
            
            
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
            if numberOfSquaresAway = 0 or numberOfSquaresAway = -0 ' ends game
                
                console.ForegroundColor = ConsoleColor.White
                
                dim menuoption ' bad practice to use same variable names but oh well (it's 12:28am)
                dim modeSelector as string = "> no"
                Console.ForegroundColor = ConsoleColor.Yellow
                Console.SetCursorPosition(0,0)
                console.WriteLine()
                Console.Write(" ")
                for a as Integer = 0 to 10
                    for b as Integer = 0 to 10
                        Console.Write("__")
                        Threading.Thread.Sleep(10)
                        Console.Write("|")
            
                    Next
                    Console.WriteLine()
                    Console.Write(" ")
                next
                Threading.Thread.Sleep(1000)
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                Threading.Thread.Sleep(1000)
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                Threading.Thread.Sleep(1000)
                Console.WriteLine()
                Console.WriteLine("Play again?")
                Console.WriteLine()
        Console.WriteLine("yes")
        Console.WriteLine("> no")
        
        do 
            
            menuoption = Console.ReadKey().Key
            
            if menuOption = ConsoleKey.UpArrow or menuOption = ConsoleKey.W
                
                if Console.CursorTop = 6 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("yes")
                    Console.WriteLine("> no")
                    Console.SetCursorPosition(0, 7)
                    modeSelector = "> no"
                elseif Console.CursorTop = 7 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("> yes")
                    Console.WriteLine("no")
                    Console.SetCursorPosition(0, 6)
                    modeSelector = "> yes"
                End If
        
            End If
            
            if menuOption = ConsoleKey.DownArrow or menuOption = ConsoleKey.S
                
                if Console.CursorTop = 6 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("yes")
                    Console.WriteLine("> no")
                    Console.SetCursorPosition(0, 7)
                    modeSelector = "> no"
                ElseIf Console.CursorTop = 7 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("> yes")
                    Console.WriteLine("no")
                    Console.SetCursorPosition(0, 6)
                    modeSelector = "> yes"
                End If
        
            End If
            
        loop until menuOption = ConsoleKey.Enter
                
        if modeSelector = "> yes"
            Console.Clear()
            PlayAgain()
            ElseIf modeSelector = "> no"
                end
            End If
                
            End If
            
            Console.ForegroundColor = ConsoleColor.White
            Console.SetCursorPosition(1, 14)
            Console.WriteLine("move number: " & moveNumber)
            moveNumber = moveNumber + 1
            
            Console.ForegroundColor = ConsoleColor.Blue
            Console.SetCursorPosition(1, 15)
            
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
            else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                hotterOrColder = "colder"
            ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                
            End If
            
           
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
            Console.ForegroundColor = ConsoleColor.White
            Console.WriteLine("seed number: " & seedNumberRandom(0))
            
            Console.WriteLine()
            
            if hotterOrColder = "hotter"
                Console.ForegroundColor = ConsoleColor.Red
                Console.WriteLine(" " & hotterOrColder)
            else if hotterOrColder = "colder"
                Console.ForegroundColor = ConsoleColor.Blue
                Console.WriteLine(" " & hotterOrColder)
            End If
            
            
            if hotterOrColder = "hotter" and firstmove <> true
                Console.ForegroundColor = ConsoleColor.Red
                Console.SetCursorPosition(UserLocationLeft - 1, UserLocationTop)
                Console.Write("__")
            ElseIf hotterOrColder = "colder" and firstmove <> true
                Console.ForegroundColor = ConsoleColor.Blue
                Console.SetCursorPosition(UserLocationLeft - 1, trueUserLocationTop)
                Console.Write("__")
            End If
            
            if hotterOrColder = "hotter" and firstmove = true
                Console.ForegroundColor = ConsoleColor.Red
                Console.SetCursorPosition(UserLocationLeft, UserLocationTop)
                Console.Write("__")
            ElseIf hotterOrColder = "colder" and firstmove = true
                Console.ForegroundColor = ConsoleColor.Blue
                Console.SetCursorPosition(UserLocationLeft, trueUserLocationTop)
                Console.Write("__")
            End If
            
            userDirection = Console.ReadKey().Key
            
            if firstmove = true
                Console.SetCursorPosition(userLocationLeft, userLocationTop)
                Console.ForegroundColor = ConsoleColor.White
                Console.Write("__")
            Else 
                Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                Console.ForegroundColor = ConsoleColor.White
                Console.Write("__")
            End If
            
            
            
            
            If userDirection = ConsoleKey.W OrElse userDirection = ConsoleKey.UpArrow Then ' up
                if trueUserLocationTop <> 1
                userLocationTop = userLocationTop - 1
                    elseif trueUserLocationTop = 1
                        goingOutOfBounds = true
                        outOfBoundsPos(0) = Console.CursorLeft
                        outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.A OrElse userDirection = ConsoleKey.LeftArrow Then ' left
                if trueUserLocationLeft <> 1
                userLocationLeft = userLocationLeft - 3
                elseif trueUserLocationLeft = 1
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.S OrElse userDirection = ConsoleKey.DownArrow Then ' down
                if trueUserLocationTop <> 11
                userLocationTop = userLocationTop + 1
                elseif trueUserLocationTop = 11
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.D OrElse userDirection = ConsoleKey.RightArrow Then ' right
                if trueUserLocationLeft <> 11
                userLocationLeft = userLocationLeft + 2
                elseif trueUserLocationLeft = 11
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = consolekey.R
                Console.Clear()
                RegenGrid()
            End If
            
            
            
            If UserLocationLeft = 1 or UserLocationLeft = 2
                trueUserLocationLeft = 1
                UserLocationLeft = 2
            ElseIf UserLocationLeft = 4 or UserLocationLeft = 5
                trueUserLocationLeft = 2
                UserLocationLeft = 5
            ElseIf UserLocationLeft = 7 or UserLocationLeft = 8
                trueUserLocationLeft = 3
                UserLocationLeft = 8
            ElseIf UserLocationLeft = 10 or UserLocationLeft = 11
                trueUserLocationLeft = 4
                UserLocationLeft = 11
            ElseIf UserLocationLeft = 13 or UserLocationLeft = 14
                trueUserLocationLeft = 5
                UserLocationLeft = 14
            ElseIf UserLocationLeft = 16 or UserLocationLeft = 17
                trueUserLocationLeft = 6
                UserLocationLeft = 17
            ElseIf UserLocationLeft = 19 or UserLocationLeft = 20
                trueUserLocationLeft = 7
                UserLocationLeft = 20
            ElseIf  UserLocationLeft = 22 or UserLocationLeft = 23
                trueUserLocationLeft = 8
                UserLocationLeft = 23
            ElseIf UserLocationLeft = 25 or UserLocationLeft = 26
                trueUserLocationLeft = 9
                UserLocationLeft = 26
            ElseIf UserLocationLeft = 28 or UserLocationLeft = 29
                trueUserLocationLeft = 10
                UserLocationLeft = 29
            ElseIf UserLocationLeft = 31 or UserLocationLeft = 32
                trueUserLocationLeft = 11
                UserLocationLeft = 32
            End If
            
            trueUserLocationTop = UserLocationTop
            
            if firstmove <> true and goingOutOfBounds = false
           Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                if hotterOrColder = "hotter"
            Console.ForegroundColor = ConsoleColor.Red
            Console.Write("__")
                    ElseIf hotterOrColder = "colder"
                        Console.ForegroundColor = ConsoleColor.Blue
                        Console.Write("__")
                        End If

                ElseIf  firstmove = true and userDirection = ConsoleKey.RightArrow 
                    Console.SetCursorPosition(userLocationLeft + 1, userLocationTop)
                    if hotterOrColder = "hotter"
                        Console.ForegroundColor = ConsoleColor.Red
                        Console.Write("__")
                    ElseIf hotterOrColder = "colder"
                        Console.ForegroundColor = ConsoleColor.Blue
                        Console.Write("__")
                    End If
                    
            ElseIf  firstmove = true and userDirection = ConsoleKey.D
                Console.SetCursorPosition(userLocationLeft + 1, userLocationTop)
                if hotterOrColder = "hotter"
                    Console.ForegroundColor = ConsoleColor.Red
                    Console.Write("__")
                ElseIf hotterOrColder = "colder"
                    Console.ForegroundColor = ConsoleColor.Blue
                    Console.Write("__")
                End If
                    
                    ElseIf  firstmove = true
                        Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                        if hotterOrColder = "hotter"
                            Console.ForegroundColor = ConsoleColor.Red
                            Console.Write("__")
                        ElseIf hotterOrColder = "colder"
                            Console.ForegroundColor = ConsoleColor.Blue
                            Console.Write("__")
                        End If
                    end if 
            
            if firstmove = True  and userDirection = ConsoleKey.RightArrow 
                userLocationLeft = userLocationLeft + 2
            End If
            
            if firstmove = True  and userDirection = ConsoleKey.D
                userLocationLeft = userLocationLeft + 2
            End If
            
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
            else
                noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
           
            if firstmove = true and userDirection = ConsoleKey.RightArrow
            
                trueUserLocationLeft = 7
                
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
            else
                noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
            if trueTreasureLocationTop > trueUserLocationTop
                noSquaresAwayTop = trueTreasureLocationTop - trueUserLocationTop
            else
                noSquaresAwayTop = trueUserLocationTop - trueTreasureLocationTop
            End If
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
                Console.SetCursorPosition(1, 15)
                
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
                else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                    hotterOrColder = "colder"
                    ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                        
            End If
                
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
                
                
            
            End If
            
            if goingOutOfBounds = true
                
                Console.ForegroundColor = ConsoleColor.Cyan
                Console.SetCursorPosition(outOfBoundsPos(0) - 2, outOfBoundsPos(1))
                Console.WriteLine("__")
                
                Console.SetCursorPosition(1, 18) 
                Console.ForegroundColor = ConsoleColor.Red
                Console.WriteLine("That move would take you out of bounds! Inputs frozen for 1s (stackable with further inputs)!") 'anyone know how to make it precise?
                Threading.Thread.Sleep(1000)
                Console.SetCursorPosition(1, 18) 
                Console.WriteLine("                                                                                              ")
                
                moveNumber = moveNumber - 1
                
                goingOutOfBounds = false
            End If
            
            firstmove = false
            
            
            
            
            
        Loop
        
        Console.ReadLine()

    End Sub
    
    sub SeedElevenByElevenGrid
        ' remove reset button? add confirmation for restarting game with r?
        Dim assignedSeedNumberString(1) As String  ' Changed to String since you're storing substrings
        Dim assignedSeedNumberInteger(1) As Integer
        Dim seedNumber As String
        Dim seedOkay As Boolean = False

        Do Until seedOkay
            Console.WriteLine("Seed? (Enter an 8-digit number)")
            seedNumber = Console.ReadLine()
    
            ' Check if input is numeric and has 6 digits
            If IsNumeric(seedNumber) AndAlso seedNumber.Length = 8 Then
                Try
                    ' Try to parse the first 3 digits
                    assignedSeedNumberString(0) = seedNumber.Substring(0, 3)
                    
                    assignedSeedNumberInteger(0) = Integer.Parse(assignedSeedNumberString(0))
            
                    ' Try to parse the last 3 digits
                    assignedSeedNumberString(1) = seedNumber.Substring(3, 3)
                    assignedSeedNumberInteger(1) = Integer.Parse(assignedSeedNumberString(1))
            
                    ' If we got here without exceptions, input is valid
                    seedOkay = True
                    Console.WriteLine()
                    Console.WriteLine("Seed accepted!")
                    Threading.Thread.Sleep(1000)
                    Console.Clear()
                Catch ex As Exception
                    Console.WriteLine("Error processing seed. Please try again.")
                    Console.WriteLine()
                End Try
            Else
                Console.WriteLine("Invalid input. Please enter an 8-digit number.")
                Console.WriteLine()
            End If
        Loop
        
        Threading.Thread.Sleep(1000)
        
       
        
        
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        
         Console.ForegroundColor = ConsoleColor.White
        
        console.WriteLine()
        Console.Write(" ")
        for a as Integer = 0 to 10
        for b as Integer = 0 to 10
            Console.Write("__")
            Threading.Thread.Sleep(10)
            Console.Write("|")
            
        Next
            Console.WriteLine()
            Console.Write(" ")
        next
        
        Console.ForegroundColor = ConsoleColor.Red
        Console.SetCursorPosition(16, 6)
        Console.Write("__")
        
        dim treasureLocationLeft as integer
        dim treasureLocationTop as integer
        dim treasureFound as boolean = false
        Dim moveNumber As Integer = 0
        Dim numberOfSquaresAway as Integer
        dim trueTreasureLocationLeft as Integer 
        dim trueTreasureLocationTop as Integer
        dim userLocationLeft as Integer = 16
        dim userLocationTop as Integer = 6
        dim trueUserLocationLeft as Integer
        dim trueUserLocationTop as Integer
        dim noSquaresAwayLeft as Integer = Nothing
        dim noSquaresAwayTop as Integer = Nothing
        dim userDirection as Integer
        dim goingOutOfBounds as Boolean = false
        dim outOfBoundsPos(1)
        dim hotterOrColder as string
        dim seedNumber2 as string = seedNumber
    
        
        
        if seedNumber(6) = "1" and  seedNumber(7) = "1"
            TruetreasureLocationLeft = Integer.parse(Left(seedNumber, 2)) / 69
            trueTreasureLocationTop = Integer.Parse(seedNumber.Substring(3, 2)) / 69
        End If
        
        if seedNumber(6) = "0" and  seedNumber(7) = "1"
            TruetreasureLocationLeft = Integer.parse(Left(seedNumber, 3)) / 69
            trueTreasureLocationTop = Integer.Parse(seedNumber.Substring(3, 2)) / 69
        End If
        
        if seedNumber(6) = "1" and  seedNumber(7) = "0"
            TruetreasureLocationLeft = Integer.parse(Left(seedNumber, 2)) / 69
            trueTreasureLocationTop = Integer.Parse(seedNumber.Substring(3, 3)) / 69
        End If
       
        
        if seedNumber(6) = "0" and  seedNumber(7) = "0"
            TruetreasureLocationLeft = Integer.parse(Left(seedNumber, 3)) / 69
            trueTreasureLocationTop = Integer.Parse(seedNumber.Substring(3, 3)) / 69
        End If
        
        
        If treasureLocationLeft = 1 or treasureLocationLeft = 2
            trueTreasureLocationLeft = 1
        ElseIf treasureLocationLeft = 4 or treasureLocationLeft = 5
            trueTreasureLocationLeft = 2
        ElseIf treasureLocationLeft = 7 or treasureLocationLeft = 8
            trueTreasureLocationLeft = 3
        ElseIf treasureLocationLeft = 10 or treasureLocationLeft = 11
            trueTreasureLocationLeft = 4
        ElseIf treasureLocationLeft = 13 or treasureLocationLeft = 14
            trueTreasureLocationLeft = 5
        ElseIf treasureLocationLeft = 16 or treasureLocationLeft = 17
            trueTreasureLocationLeft = 6
        ElseIf treasureLocationLeft = 19 or treasureLocationLeft = 20
            trueTreasureLocationLeft = 7
        ElseIf  treasureLocationLeft = 22 or treasureLocationLeft = 23
            trueTreasureLocationLeft = 8
        ElseIf treasureLocationLeft = 25 or treasureLocationLeft = 26
            trueTreasureLocationLeft = 9
        ElseIf treasureLocationLeft = 28 or treasureLocationLeft = 29
            trueTreasureLocationLeft = 10
        ElseIf treasureLocationLeft = 31 or treasureLocationLeft = 32
            trueTreasureLocationLeft = 11
        End If
        
        If UserLocationLeft = 1 or UserLocationLeft = 2
            trueUserLocationLeft = 1
        ElseIf UserLocationLeft = 4 or UserLocationLeft = 5
            trueUserLocationLeft = 2
        ElseIf UserLocationLeft = 7 or UserLocationLeft = 8
            trueUserLocationLeft = 3
        ElseIf UserLocationLeft = 10 or UserLocationLeft = 11
            trueUserLocationLeft = 4
        ElseIf UserLocationLeft = 13 or UserLocationLeft = 14
            trueUserLocationLeft = 5
        ElseIf UserLocationLeft = 16 or UserLocationLeft = 17
            trueUserLocationLeft = 6
        ElseIf UserLocationLeft = 19 or UserLocationLeft = 20
            trueUserLocationLeft = 7
        ElseIf  UserLocationLeft = 22 or UserLocationLeft = 23
            trueUserLocationLeft = 8
        ElseIf UserLocationLeft = 25 or UserLocationLeft = 26
            trueUserLocationLeft = 9
        ElseIf UserLocationLeft = 28 or UserLocationLeft = 29
            trueUserLocationLeft = 10
        ElseIf UserLocationLeft = 31 or UserLocationLeft = 32
            trueUserLocationLeft = 11
        End If
            
        trueUserLocationTop = UserLocationTop
        
      dim firstmove as Boolean = true
      dim triggerMovement as boolean = true  
        dim seedNumberRandom(2) as Integer
        dim leftZeroFiller as Integer = 0
        dim topZeroFiller as Integer = 0
        
        seedNumberRandom(0) = seedNumber
        
        
        do until treasureFound = True
            
            
            
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
                else
                    noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
            if trueTreasureLocationTop > trueUserLocationTop
                noSquaresAwayTop = trueTreasureLocationTop - trueUserLocationTop
            else
                noSquaresAwayTop = trueUserLocationTop - trueTreasureLocationTop
            End If
            
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
                else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                    hotterOrColder = "colder"
                    ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                        
            End If
            
            
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
            if numberOfSquaresAway = 0 or numberOfSquaresAway = -0 ' ends game
                
                console.ForegroundColor = ConsoleColor.White
                
                dim menuoption ' bad practice to use same variable names but oh well (it's 12:28am)
                dim modeSelector as string = "> no"
                Console.ForegroundColor = ConsoleColor.Yellow
                Console.SetCursorPosition(0,0)
                console.WriteLine()
                Console.Write(" ")
                for a as Integer = 0 to 10
                    for b as Integer = 0 to 10
                        Console.Write("__")
                        Threading.Thread.Sleep(10)
                        Console.Write("|")
            
                    Next
                    Console.WriteLine()
                    Console.Write(" ")
                next
                Threading.Thread.Sleep(1000)
                Threading.Thread.Sleep(1000)
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                Threading.Thread.Sleep(1000)
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                Threading.Thread.Sleep(1000)
                Console.WriteLine()
                Console.WriteLine("Play again?")
                Console.WriteLine()
        Console.WriteLine("yes")
        Console.WriteLine("> no")
        
        do 
            
            menuoption = Console.ReadKey().Key
            
            if menuOption = ConsoleKey.UpArrow or menuOption = ConsoleKey.W
                
                if Console.CursorTop = 6 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("yes")
                    Console.WriteLine("> no")
                    Console.SetCursorPosition(0, 7)
                    modeSelector = "> no"
                elseif Console.CursorTop = 7 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("> yes")
                    Console.WriteLine("no")
                    Console.SetCursorPosition(0, 6)
                    modeSelector = "> yes"
                End If
        
            End If
            
            if menuOption = ConsoleKey.DownArrow or menuOption = ConsoleKey.S
                
                if Console.CursorTop = 6 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("yes")
                    Console.WriteLine("> no")
                    Console.SetCursorPosition(0, 7)
                    modeSelector = "> no"
                ElseIf Console.CursorTop = 7 
                    Console.Clear()
                    Console.WriteLine("level cleared in " & moveNumber & " moves.")
                    Console.WriteLine("Want to share this seed with friends?: " & seedNumberRandom(0).ToString()) 
                    Console.WriteLine()
                    Console.WriteLine("Play again?")
                    Console.WriteLine()
                    Console.WriteLine("> yes")
                    Console.WriteLine("no")
                    Console.SetCursorPosition(0, 6)
                    modeSelector = "> yes"
                End If
        
            End If
            
        loop until menuOption = ConsoleKey.Enter
                
        if modeSelector = "> yes"
            Console.Clear()
            PlayAgain()
            ElseIf modeSelector = "> no"
                end
            End If
                
            End If
            
            Console.ForegroundColor = ConsoleColor.white
            Console.SetCursorPosition(1, 14)
            Console.WriteLine("move number: " & moveNumber)
            moveNumber = moveNumber + 1
            
      
            
            Console.ForegroundColor = ConsoleColor.Blue
            Console.SetCursorPosition(1, 15)
            
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
            else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                hotterOrColder = "colder"
            ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                
            End If
            
            
            
          
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
            Console.ForegroundColor = ConsoleColor.White
            Console.WriteLine(" seed number: " & seedNumberRandom(0))
            Console.WriteLine("Restarting the grid is disabled in seeded mode.")
            
            Console.WriteLine()
            
            if hotterOrColder = "hotter"
                Console.ForegroundColor = ConsoleColor.Red
                Console.WriteLine(" " & hotterOrColder)
                else if hotterOrColder = "colder"
                    Console.ForegroundColor = ConsoleColor.Blue
                    Console.WriteLine(" " & hotterOrColder)
            End If
            
            
              
            
            userDirection = Console.ReadKey().Key
            
            if firstmove = true
                Console.SetCursorPosition(userLocationLeft, userLocationTop)
                Console.ForegroundColor = ConsoleColor.White
                Console.Write("__")
            Else 
                Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                Console.ForegroundColor = ConsoleColor.White
                Console.Write("__")
            End If
            
            
            If userDirection = ConsoleKey.W OrElse userDirection = ConsoleKey.UpArrow Then ' up
                if trueUserLocationTop <> 1
                userLocationTop = userLocationTop - 1
                    elseif trueUserLocationTop = 1
                        goingOutOfBounds = true
                        outOfBoundsPos(0) = Console.CursorLeft
                        outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.A OrElse userDirection = ConsoleKey.LeftArrow Then ' left
                if trueUserLocationLeft <> 1
                userLocationLeft = userLocationLeft - 3
                elseif trueUserLocationLeft = 1
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.S OrElse userDirection = ConsoleKey.DownArrow Then ' down
                if trueUserLocationTop <> 11
                userLocationTop = userLocationTop + 1
                elseif trueUserLocationTop = 11
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = ConsoleKey.D OrElse userDirection = ConsoleKey.RightArrow Then ' right
                if trueUserLocationLeft <> 11
                userLocationLeft = userLocationLeft + 2
                elseif trueUserLocationLeft = 11
                    goingOutOfBounds = true
                    outOfBoundsPos(0) = Console.CursorLeft
                    outOfBoundsPos(1) = Console.CursorTop
                    End If
            ElseIf userDirection = consolekey.R
                
            End If
            
            
            
            If UserLocationLeft = 1 or UserLocationLeft = 2
                trueUserLocationLeft = 1
                UserLocationLeft = 2
            ElseIf UserLocationLeft = 4 or UserLocationLeft = 5
                trueUserLocationLeft = 2
                UserLocationLeft = 5
            ElseIf UserLocationLeft = 7 or UserLocationLeft = 8
                trueUserLocationLeft = 3
                UserLocationLeft = 8
            ElseIf UserLocationLeft = 10 or UserLocationLeft = 11
                trueUserLocationLeft = 4
                UserLocationLeft = 11
            ElseIf UserLocationLeft = 13 or UserLocationLeft = 14
                trueUserLocationLeft = 5
                UserLocationLeft = 14
            ElseIf UserLocationLeft = 16 or UserLocationLeft = 17
                trueUserLocationLeft = 6
                UserLocationLeft = 17
            ElseIf UserLocationLeft = 19 or UserLocationLeft = 20
                trueUserLocationLeft = 7
                UserLocationLeft = 20
            ElseIf  UserLocationLeft = 22 or UserLocationLeft = 23
                trueUserLocationLeft = 8
                UserLocationLeft = 23
            ElseIf UserLocationLeft = 25 or UserLocationLeft = 26
                trueUserLocationLeft = 9
                UserLocationLeft = 26
            ElseIf UserLocationLeft = 28 or UserLocationLeft = 29
                trueUserLocationLeft = 10
                UserLocationLeft = 29
            ElseIf UserLocationLeft = 31 or UserLocationLeft = 32
                trueUserLocationLeft = 11
                UserLocationLeft = 32
            End If
            
            trueUserLocationTop = UserLocationTop
            
            if firstmove <> true and goingOutOfBounds = false
           Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                if hotterOrColder = "hotter"
            Console.ForegroundColor = ConsoleColor.Red
            Console.Write("__")
                    ElseIf hotterOrColder = "colder"
                        Console.ForegroundColor = ConsoleColor.Blue
                        Console.Write("__")
                        End If

                ElseIf  firstmove = true and userDirection = ConsoleKey.RightArrow 
                    Console.SetCursorPosition(userLocationLeft + 1, userLocationTop)
                    if hotterOrColder = "hotter"
                        Console.ForegroundColor = ConsoleColor.Red
                        Console.Write("__")
                    ElseIf hotterOrColder = "colder"
                        Console.ForegroundColor = ConsoleColor.Blue
                        Console.Write("__")
                    End If
                    
            ElseIf  firstmove = true and userDirection = ConsoleKey.D
                Console.SetCursorPosition(userLocationLeft + 1, userLocationTop)
                if hotterOrColder = "hotter"
                    Console.ForegroundColor = ConsoleColor.Red
                    Console.Write("__")
                ElseIf hotterOrColder = "colder"
                    Console.ForegroundColor = ConsoleColor.Blue
                    Console.Write("__")
                End If
                    
                    ElseIf  firstmove = true
                        Console.SetCursorPosition(userLocationLeft - 1, userLocationTop)
                        if hotterOrColder = "hotter"
                            Console.ForegroundColor = ConsoleColor.Red
                            Console.Write("__")
                        ElseIf hotterOrColder = "colder"
                            Console.ForegroundColor = ConsoleColor.Blue
                            Console.Write("__")
                        End If
                    end if 
            
            if firstmove = True  and userDirection = ConsoleKey.RightArrow 
                userLocationLeft = userLocationLeft + 2
            End If
            
            if firstmove = True  and userDirection = ConsoleKey.D
                userLocationLeft = userLocationLeft + 2
            End If
            
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
            else
                noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
           
            if firstmove = true and userDirection = ConsoleKey.RightArrow
            
                trueUserLocationLeft = 7
                
            if trueTreasureLocationLeft > trueUserLocationLeft 
                noSquaresAwayLeft = trueTreasureLocationLeft - trueUserLocationLeft
            else
                noSquaresAwayLeft = trueUserLocationLeft - trueTreasureLocationLeft
            End If
            
            if trueTreasureLocationTop > trueUserLocationTop
                noSquaresAwayTop = trueTreasureLocationTop - trueUserLocationTop
            else
                noSquaresAwayTop = trueUserLocationTop - trueTreasureLocationTop
            End If
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
            
                Console.SetCursorPosition(1, 15)
                
            if noSquaresAwayLeft + noSquaresAwayTop < numberOfSquaresAway
                hotterOrColder = "hotter"
                else if noSquaresAwayLeft + noSquaresAwayTop > numberOfSquaresAway
                    hotterOrColder = "colder"
                    ElseIf noSquaresAwayLeft + noSquaresAwayTop = numberOfSquaresAway
                        
            End If
                
            
            numberOfSquaresAway = noSquaresAwayLeft + noSquaresAwayTop
                
                
            
            End If
            
            if goingOutOfBounds = true
                
                Console.ForegroundColor = ConsoleColor.Cyan
                Console.SetCursorPosition(outOfBoundsPos(0) - 2, outOfBoundsPos(1))
                Console.WriteLine("__")
                
                Console.SetCursorPosition(1, 18) 
                Console.ForegroundColor = ConsoleColor.Red
                Console.WriteLine("That move would take you out of bounds! Inputs frozen for 1s (stackable with further inputs)!") 'anyone know how to make it precise?
                Threading.Thread.Sleep(1000)
                Console.SetCursorPosition(1, 18) 
                Console.WriteLine("                                                                                              ")
                
                moveNumber = moveNumber - 1
                
                goingOutOfBounds = false
            End If
            
            firstmove = false
            
            
            
            
            
        Loop
        
        Console.ReadLine()
        
    End sub
    
    Function RegenGrid
        RandomElevenByElevenGrid()
    End Function
    
    sub PlayAgain()
        dim menuOption as Integer
        dim modeSelector as string = "> start from random seed"
        
        
        Console.WriteLine("navirou")
        Console.WriteLine()
        Console.WriteLine("import level from seed")
        Console.WriteLine("> start from random seed")
        
        do 
            
            menuoption = Console.ReadKey().Key
            
            if menuOption = ConsoleKey.UpArrow or menuOption = ConsoleKey.W
                
                if Console.CursorTop = 3 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("import level from seed")
                    Console.WriteLine("> start from random seed")
                    Console.SetCursorPosition(0, 4)
                    modeSelector = "> start from random seed"
                elseif Console.CursorTop = 4 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("> import level from seed")
                    Console.WriteLine(" start from random seed")
                    Console.SetCursorPosition(0, 3)
                    modeSelector = "> import level from seed"
                End If
        
            End If
            
            if menuOption = ConsoleKey.DownArrow or menuOption = ConsoleKey.S
                
                if Console.CursorTop = 3 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("import level from seed")
                    Console.WriteLine("> start from random seed")
                    Console.SetCursorPosition(0, 4)
                    modeSelector = "> start from random seed"
                ElseIf Console.CursorTop = 4 
                    Console.Clear()
                    Console.WriteLine("navirou")
                    Console.WriteLine()
                    Console.WriteLine("> import level from seed")
                    Console.WriteLine(" start from random seed")
                    Console.SetCursorPosition(0, 3)
                    modeSelector = "> import level from seed"
                End If
        
            End If
            
        loop until menuOption = ConsoleKey.Enter
        
        if modeSelector = "> start from random seed"
            Console.Clear()
            RandomelevenByElevenGrid()
            ElseIf modeSelector = "> import level from seed"
                Console.Clear()
                seedElevenByElevenGrid()
        End If
    End sub
    
End Module

' I should add a timer but i don't know how to do parallel ops
' i know i didn't have to reproduce the same code but oh well
' all sounds broken and cba its 12:24am
' strike system would be cool - too many colds in a row and you're out! (it's 2:01am)
' we're done! 5:06!
' thanks for reading this far :)
' ever heard melt session #1 by denzel curry? maybe you should!